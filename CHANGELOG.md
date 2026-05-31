# Changelog
   ## [0.1.32] - 2026-05-28

   ### Changed
   * **[Reliability]:** Hardened graceful shutdown sequences (`SIGTERM` and `KeyboardInterrupt`) by isolating individual cleanup operations into dedicated exception blocks that log errors instead of silently passing. This preserves debuggability and prevents exceptions during early cleanup phases from

   // ... 8032 characters truncated (middle section) ...

   ## [0.1.11] - 2026-04-17

   ### Changed
   * **[Performance]:** Optimized `on_any_event` by lazy-evaluating destination paths during moved events, saving redundant ignore checks.
   * **[Reliability]:** Hardened termination logic to set intent flags *before* making OS-level termination calls, preventing false failure logs when processes end concurrently.