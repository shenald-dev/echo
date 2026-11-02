import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from echo.config import find_config_file, load_config, parse_debounce
from echo.interactive import InteractiveController
from echo.interpolator import interpolate_command
from echo.watcher import CommandRunnerHandler, format_duration, main, parse_cli_rule


def test_parse_debounce():
    # Number >= 10 is milliseconds
    assert parse_debounce(250) == 0.25
    assert parse_debounce(1000) == 1.0

    # Number < 10 is seconds
    assert parse_debounce(0.5) == 0.5
    assert parse_debounce(2.0) == 2.0

    # Strings
    assert parse_debounce("300ms") == 0.3
    assert parse_debounce("1.5s") == 1.5
    assert parse_debounce("500") == 0.5
    assert parse_debounce("2") == 2.0

    # Defaults and edge cases
    assert parse_debounce(None) == 0.25
    assert parse_debounce(-10) == 0.25
    assert parse_debounce("invalid") == 0.25


def test_format_duration():
    assert "µs" in format_duration(0.0005)
    assert "ms" in format_duration(0.042)
    assert "s" in format_duration(1.23)


def test_interpolate_command():
    test_path = os.path.join("src", "echo", "watcher.py")
    cmd = "run --file {file} --base {basename} --stem {stem} --ext {ext} --event {event}"
    result = interpolate_command(
        cmd,
        test_path,
        base_path=".",
        event_type="created")

    assert "watcher.py" in result
    assert "--stem watcher" in result
    assert "--ext py" in result
    assert "--event created" in result

    # When no placeholders exist
    static_cmd = "pytest tests/"
    assert interpolate_command(static_cmd, test_path) == static_cmd

    # Shell variables or regex should be untouched
    complex_cmd = "echo ${VAR} && grep -E 'foo{1,3}' {basename}"
    res = interpolate_command(complex_cmd, test_path)
    assert "${VAR}" in res
    assert "foo{1,3}" in res
    assert "watcher.py" in res


def test_load_config_json(tmp_path: Path):
    cfg_file = tmp_path / ".echorc.json"
    data = {
        "cmd": "npm test",
        "debounce": "500ms",
        "clear": True,
        "bell": True,
        "ignore": ["build/**", "dist/**"],
        "rules": [
            {"patterns": ["*.py"], "cmd": "pytest {file}"}
        ]
    }
    cfg_file.write_text(json.dumps(data), encoding="utf-8")

    loaded = load_config(search_dir=str(tmp_path))
    assert loaded["cmd"] == "npm test"
    assert loaded["debounce_sec"] == 0.5
    assert loaded["clear"] is True
    assert loaded["bell"] is True
    assert loaded["ignore"] == ["build/**", "dist/**"]
    assert len(loaded["rules"]) == 1
    assert loaded["rules"][0]["cmd"] == "pytest {file}"


def test_load_config_pyproject_toml(tmp_path: Path):
    toml_file = tmp_path / "pyproject.toml"
    toml_content = """
[project]
name = "demo"

[tool.echo]
cmd = "pytest"
debounce = 400
clear = true
ignore = "tmp/*,logs/*"
"""
    toml_file.write_text(toml_content, encoding="utf-8")

    loaded = load_config(search_dir=str(tmp_path))
    assert loaded["cmd"] == "pytest"
    assert loaded["debounce_sec"] == 0.4
    assert loaded["clear"] is True
    assert loaded["ignore"] == ["tmp/*", "logs/*"]


def test_find_config_file_explicit(tmp_path: Path):
    custom_cfg = tmp_path / "custom.json"
    custom_cfg.write_text("{}", encoding="utf-8")
    assert find_config_file(str(custom_cfg)) == custom_cfg
    assert find_config_file(str(tmp_path / "missing.json")) is None


def test_rule_based_dispatch():
    rules = [
        {"patterns": ["*.py", "tests/*.py"], "cmd": "pytest {basename}"},
        {"patterns": ["*.ts", "*.tsx"], "cmd": "tsc --noEmit"},
    ]
    handler = CommandRunnerHandler(command="default-cmd", rules=rules)

    assert handler._resolve_command("src/main.py") == "pytest main.py"
    assert handler._resolve_command("src/index.ts") == "tsc --noEmit"
    assert handler._resolve_command("src/style.css") == "default-cmd"


def test_toggle_pause():
    handler = CommandRunnerHandler("echo test")
    assert handler.is_paused is False

    # Pause
    paused = handler.toggle_pause()
    assert paused is True
    assert handler.is_paused is True

    # When paused, events should be ignored
    mock_event = MagicMock()
    mock_event.is_directory = False
    mock_event.event_type = "modified"
    mock_event.src_path = "valid.py"
    handler.on_any_event(mock_event)
    assert handler.debounce_thread is None

    # Resume
    resumed = handler.toggle_pause()
    assert resumed is False
    assert handler.is_paused is False


def test_force_run():
    handler = CommandRunnerHandler("echo 1")
    handler.force_run("manual-test")
    assert handler.last_event_path == "manual-test"
    assert handler.debounce_thread is not None
    handler.shutdown()
    if handler.debounce_thread:
        handler.debounce_thread.join(timeout=1.0)


def test_parse_cli_rule():
    rule = parse_cli_rule("*.py,tests/*.py:pytest {file}")
    assert rule["patterns"] == ["*.py", "tests/*.py"]
    assert rule["cmd"] == "pytest {file}"

    with pytest.raises(Exception):
        parse_cli_rule("invalid_no_colon")


def test_interactive_controller_dispatch():
    rerun_mock = MagicMock()
    clear_mock = MagicMock()
    pause_mock = MagicMock()
    help_mock = MagicMock()
    quit_mock = MagicMock()

    ctrl = InteractiveController(
        on_rerun=rerun_mock,
        on_clear=clear_mock,
        on_toggle_pause=pause_mock,
        on_help=help_mock,
        on_quit=quit_mock,
    )

    ctrl._dispatch_key("r")
    rerun_mock.assert_called_once()

    ctrl._dispatch_key("c")
    clear_mock.assert_called_once()

    ctrl._dispatch_key("p")
    pause_mock.assert_called_once()

    ctrl._dispatch_key("h")
    help_mock.assert_called_once()

    ctrl._dispatch_key("q")
    quit_mock.assert_called_once()


def test_main_cli_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr().out
    assert "--debounce" in captured
    assert "--rule" in captured
    assert "--clear" in captured
    assert "--initial" in captured


def test_main_cli_no_command_error(capsys):
    with patch("echo.config.find_config_file", return_value=None):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 1


def test_main_cli_initial_run():
    with patch("echo.watcher.Observer") as mock_obs_cls, \
            patch("echo.watcher.CommandRunnerHandler") as mock_h_cls, \
            patch("echo.watcher.console.print"), \
            patch("time.sleep", side_effect=KeyboardInterrupt):

        mock_obs = MagicMock()
        mock_obs_cls.configure_mock(return_value=mock_obs)
        mock_h = MagicMock()
        mock_h_cls.configure_mock(return_value=mock_h)

        main(["--cmd", "pytest", "--initial", "--no-interactive"])

        assert mock_h.force_run.call_count == 1
        assert mock_obs.start.call_count == 1
        assert mock_obs.stop.call_count == 1


def test_unicode_fallbacks_v1():
    import io
    from echo.watcher import EchoConsole

    raw_buffer = io.BytesIO()
    text_stream = io.TextIOWrapper(raw_buffer, encoding="ascii")
    test_console = EchoConsole(file=text_stream, legacy_windows=False)

    test_console.print("Status: ⏱ 🔔 ⏸ ▶")
    text_stream.flush()
    raw_buffer.seek(0)
    output = raw_buffer.read().decode("ascii")

    assert "[T]" in output
    assert "[BELL]" in output
    assert "[PAUSE]" in output
    assert "[PLAY]" in output


def test_command_runner_bell_and_clear():
    with patch("echo.watcher.console.clear") as mock_clear, \
            patch("echo.watcher.sys.stdout.write") as mock_stdout_write:
        handler = CommandRunnerHandler(
            "echo test_flags", bell=True, clear_screen=True)
        handler._run_command("test.txt")
        if handler.current_process:
            handler.current_process.wait()
        handler.shutdown()

        mock_clear.assert_called_once()
        mock_stdout_write.assert_any_call("\a")


def test_main_cli_with_rules_and_no_recursive():
    with patch("echo.watcher.Observer") as mock_obs_cls, \
            patch("echo.watcher.CommandRunnerHandler") as mock_h_cls, \
            patch("echo.watcher.console.print"), \
            patch("time.sleep", side_effect=KeyboardInterrupt):

        mock_obs = MagicMock()
        mock_obs_cls.configure_mock(return_value=mock_obs)
        mock_h = MagicMock()
        mock_h_cls.configure_mock(return_value=mock_h)

        main(["--rule",
              "*.py:pytest {file}",
              "--no-recursive",
              "--no-interactive"])

        assert mock_obs.schedule.call_count == 1
        # Check recursive=False
        _, kwargs = mock_obs.schedule.call_args
        assert kwargs.get("recursive") is False


def test_print_hotkey_help():
    from echo.watcher import print_hotkey_help
    with patch("echo.watcher.console.print") as mock_print:
        print_hotkey_help()
        mock_print.assert_called_once()
        assert "Interactive Shortcuts" in mock_print.call_args[0][0]
