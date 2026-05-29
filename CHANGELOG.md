We are given a merge conflict in CHANGELOG.md between base (main) and head (PR branch).
 The base (main) has changes that include a new version [0.1.31] and [0.1.30] and so on, while the head (PR branch) has a new version [0.1.29] and then continues with [0.1.28] etc.

 However, note that the base (main) has:
   ## [0.1.31] - 2026-05-28
   ## [0.1.30] - 2026-05-27
   ... and then goes down to older versions.

 The head (PR branch) has:
   ## [0.1.29] - 2026-05-23
   ## [0.1.28] - 2026-05-22
   ... and then goes down to older versions.

 The base (main) has two newer versions (0.1.31 and 0.1.30) that the head does not have.
 The head (PR branch) has a version 0.1.29 that the base does not have (because base skipped from 0.1.28 to 0.1.30? Actually, base has 0.1.31 and 0.1.30, then 0.1.28?).

 Let's look at the provided diff for the head changes vs base:

   @@ -1,4 +1,9 @@
    # Changelog
   +## [0.1.29] - 2026-05-23
   +
   +### Changed
   +* **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.
   +
    ## [0.1.28] - 2026-05-22
    
    ### Changed

 This diff shows that the head (PR branch) added a new section for [0.1.29] at the top, and then the base (main) has [0.1.28] and so on.

 However, the base (main) actually has:
   ## [0.1.31] - 2026-05-28
   ## [0.1.30] - 2026-05-27
   ... and then ## [0.1.28] - 2026-05-22

 So the base (main) has two versions (0.1.31 and 0.1.30) that are newer than 0.1.29 and 0.1.28.

 Therefore, to resolve the conflict we must:

   - Keep the two new versions from base (main): [0.1.31] and [0.1.30]
   - Keep the new version from head (PR branch): [0.1.29] (which is between 0.1.30 and 0.1.28 in time? Actually, 0.1.29 is 2026-05-23, 0.1.30 is 2026-05-27, 0.1.31 is 2026-05-28)

 But note: the base (main) has:
     [0.1.31] - 2026-05-28
     [0.1.30] - 2026-05-27
     ... then it jumps to [0.1.28] - 2026-05-22 (skipping 0.1.29)

 The head (PR branch) has:
     [0.1.29] - 2026-05-23
     [0.1.28] - 2026-05-22

 So the correct chronological order should be:
     [0.1.31] - 2026-05-28
     [0.1.30] - 2026-05-27
     [0.1.29] - 2026-05-23   (from head)
     [0.1.28] - 2026-05-22

 However, note that the base (main) does not have 0.1.29, and the head (PR branch) does not have 0.1.30 and 0.1.31.

 Therefore, we must insert the head's [0.1.29] between the base's [0.1.30] and [0.1.28].

 But wait: the base (main) has after [0.1.30] the next version is [0.1.28]? That seems odd because 0.1.29 is missing.

 Actually, looking at the base (main) provided in the context:

   Base (main): 
        ## [0.1.31] - 2026-05-28
        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ... and then ...

        ## [0.1.28] - 2026-05-22

 So the base (main) has skipped 0.1.29.

 The head (PR branch) has:

        ## [0.1.29] - 2026-05-23
        ### Changed
        * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

        ## [0.1.28] - 2026-05-22
        ... etc.

 Therefore, the resolved file should have:

   [0.1.31] (from base)
   [0.1.30] (from base)
   [0.1.29] (from head)
   [0.1.28] (from both, but note: the base and head both have [0.1.28] but with different changes? We must check)

 However, note the diff for head changes vs base only shows the addition of [0.1.29] at the top. The rest of the file from [0.1.28] onward in the head is the same as the base? Not exactly.

 Let's look at the provided versions:

   Base (main) has for [0.1.28]:
        ## [0.1.28] - 2026-05-22
        ### Changed
        * **[Performance]:** Replaced generator expressions with explicit string checks during object initialization to eliminate evaluation overhead and reduce startup latency.

   Head (PR branch) has for [0.1.28]:
        ## [0.1.28] - 2026-05-22
        ### Changed
        * **[Performance]:** Replaced generator expressions with explicit string checks during object initialization to eliminate evaluation overhead and reduce startup latency.

   So they are the same? Actually, the head (PR branch) version of [0.1.28] is the same as the base (main) version? 

   But wait, the base (main) also has a [0.1.28] section that is exactly the same as the head's [0.1.28]? 

   However, note that the base (main) has more recent versions (0.1.31 and 0.1.30) and then 0.1.28, while the head (PR branch) has 0.1.29 and then 0.1.28.

   The conflict is only at the very top: the head added a new version [0.1.29] and the base added two new versions [0.1.31] and [0.1.30] and then the rest of the file (from [0.1.28] downward) is the same in both? 

   But note: the base (main) has after [0.1.30] the next version is [0.1.28] (skipping 0.1.29). The head (PR branch) has [0.1.29] and then [0.1.28]. 

   Therefore, to resolve we must:

     - Keep the base's [0.1.31] and [0.1.30] at the top.
     - Then insert the head's [0.1.29] (because it's missing in base and the head has it).
     - Then keep the rest of the file from [0.1.28] downward (which is the same in both base and head?).

   However, we must check if there are any differences in the [0.1.28] section or below.

   Looking at the provided file versions:

     Ancestor: 
        ... (truncated) ... but we know the ancestor had [0.1.28] at the top? Actually, the ancestor is the common base.

     Base (main): 
        ... [0.1.31], [0.1.30], then [0.1.28] and so on.

     Head (PR branch):
        ... [0.1.29], [0.1.28] and so on.

   The diff for head changes vs base only shows the addition of [0.1.29] at the top. This suggests that from [0.1.28] downward, the head and base are identical.

   But note: the base (main) has two extra versions at the top (0.1.31 and 0.1.30) that the head does not have, and the head has one extra version (0.1.29) that the base does not have.

   Therefore, the resolved file should be:

        # Changelog

        ## [0.1.31] - 2026-05-28

        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ... (the rest of the changes for 0.1.30) ...

        ## [0.1.29] - 2026-05-23

        ### Changed
        * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

        ## [0.1.28] - 2026-05-22

        ### Changed
        * **[Performance]:** Replaced generator expressions with explicit string checks during object initialization to eliminate evaluation overhead and reduce startup latency.

        ... and then the rest of the file as in the base (or head, since they are the same from 0.1.28 downward) ...

   However, note that the base (main) provided in the context has after [0.1.30] the next section is [0.1.28] (without 0.1.29). We are inserting 0.1.29 between 0.1.30 and 0.1.28.

   But wait: the base (main) also has a section for [0.1.27] and so on. We must preserve the entire history.

   How do we know the exact content of the base (main) and head (PR branch) for the entire file? We are given truncated versions, but we have the diff for the head changes vs base which only shows the top.

   Since the problem states that the base (main) has 135 lines changed (lines 2-169) and the head has 99 lines changed (lines 2-156), and the ancestor is the common base, we can assume that the only differences are:

        - Base (main) added two versions at the top: [0.1.31] and [0.1.30]
        - Head (PR branch) added one version at the top: [0.1.29]

   And the rest of the file (from the original [0.1.28] downward) is identical in both base and head and matches the ancestor from that point.

   Therefore, we can construct the resolved file by:

        [base's added versions] + [head's added version] + [the common part from the ancestor starting at [0.1.28]]

   However, note: the base (main) has the common part starting at [0.1.28] (which is the same as the ancestor's [0.1.28] and beyond) but with two extra versions at the top.

   The head (PR branch) has the common part starting at [0.1.28] (same as base and ancestor) but with one extra version at the top ([0.1.29]).

   So the resolved file should be:

        # Changelog

        ## [0.1.31] - 2026-05-28
        ... (base's changes for 0.1.31) ...

        ## [0.1.30] - 2026-05-27
        ... (base's changes for 0.1.30) ...

        ## [0.1.29] - 2026-05-23
        ... (head's changes for 0.1.29) ...

        ## [0.1.28] - 2026-05-22
        ... (the common part from the ancestor for 0.1.28 and below) ...

   But note: the base (main) provided in the context already includes the common part from [0.1.28] downward? Yes, because the base (main) has:

        ## [0.1.31] - ... 
        ## [0.1.30] - ...
        ## [0.1.28] - ...   [and then the rest]

   Similarly, the head (PR branch) has:

        ## [0.1.29] - ...
        ## [0.1.28] - ...   [and then the rest]

   And the rest (from [0.1.28] downward) is the same in both.

   Therefore, we can take:

        base (main) but insert the head's [0.1.29] section between the base's [0.1.30] and [0.1.28] sections.

   How to do that?

        We know the base (main) has:

            ... 
            ## [0.1.30] - 2026-05-27
            ... (changes for 0.1.30) ...
            ## [0.1.28] - 2026-05-22
            ...

        We want to put the head's [0.1.29] section right after the base's [0.1.30] section and before the base's [0.1.28] section.

   Let's extract the head's [0.1.29] section from the head (PR branch) version:

        ## [0.1.29] - 2026-05-23

        ### Changed
        * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

   And note: the head (PR branch) version has this section at the very top, followed by the [0.1.28] section.

   Now, the base (main) version has:

        # Changelog

        ## [0.1.31] - 2026-05-28

        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ... (then it goes to [0.1.28]) ...

   So we will:

        Keep the base (main) from the start until the end of the [0.1.30] section.
        Then insert the head's [0.1.29] section.
        Then continue with the base (main) from the [0.1.28] section onward.

   But note: the base (main) has a blank line after the [0.1.30] section? We must preserve the formatting.

   Looking at the base (main) provided:

        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ... (then a blank line?) and then the next version.

   Actually, in the base (main) we see:

        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ## [0.1.28] - 2026-05-22

   There is no blank line between the end of the [0.1.30] changes and the next version header.

   Similarly, the head (PR branch) has:

        ## [0.1.29] - 2026-05-23

        ### Changed
        * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

        ## [0.1.28] - 2026-05-22

   So we want to put:

        ... (end of base's [0.1.30] section)
        ## [0.1.29] - 2026-05-23

        ### Changed
        * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

        ## [0.1.28] - 2026-05-22
        ... (the rest)

   However, note that the base (main) does not have a blank line after the [0.1.30] section's changes. We are inserting a new section, so we should add a blank line for readability? But the existing style in the base (main) does not have blank lines between sections.

   Looking at the base (main):

        ## [0.1.31] - 2026-05-28

        ### Changed
        * ... 
        * ...

        ## [0.1.30] - 2026-05-27

        ### Changed
        * ...

        ## [0.1.28] - 2026-05-22

   There is a blank line between the version header and the "### Changed", but not between the end of the changes and the next version header.

   Actually, in the base (main) we see:

        ## [0.1.31] - 2026-05-28

        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

   There are two blank lines between the end of the [0.1.31] changes and the [0.1.30] header? 

        ... dead code.
        [blank line]
        [blank line]
        ## [0.1.30] ...

   But wait, the base (main) provided in the context is:

        # Changelog

        ## [0.1.31] - 2026-05-28

        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

   So after the two bullet points, there is a blank line (the line after the second bullet is empty) and then another blank line? Actually, the text shows:

        * **[Lifecycle]:** Synced documentation and pruned dead code.
        [empty line]
        [empty line]
        ## [0.1.30] ...

   But that might be due to the truncation. However, the problem says we must maintain proper markdown syntax.

   To be safe, we will follow the pattern we see in the base (main) for separating versions: there is a blank line between the last change of a version and the next version header.

   In the base (main):

        After the [0.1.31] changes, there is a blank line (actually two newlines: one to end the last bullet and then an empty line) and then the next version.

        Specifically:

            * **[Lifecycle]:** Synced documentation and pruned dead code.
            [empty line]
            ## [0.1.30] - 2026-05-27

        But wait, the base (main) shows:

            * **[Lifecycle]:** Synced documentation and pruned dead code.


            ## [0.1.30] - 2026-05-27

        That is two empty lines? Actually, in markdown, two consecutive newlines create a blank line.

        However, the head (PR branch) shows for [0.1.29]:

            ## [0.1.29] - 2026-05-23

            ### Changed
            * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

            ## [0.1.28] - 2026-05-22

        So after the bullet point, there is a blank line and then the next version.

   Therefore, we will insert:

        After the base's [0.1.30] section (which ends with the bullet point), we put a blank line, then the [0.1.29] header, then a blank line, then the "### Changed", then the bullet point, then a blank line, and then the next version header ([0.1.28]).

   But note: the base (main) does not have a blank line after the [0.1.30] section's bullet point? Actually, in the base (main) we see:

        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.

        ## [0.1.28] - 2026-05-22

   There is no blank line between the end of the bullet and the next version header. However, looking at the [0.1.31] section, there was a blank line (or two) between the end of the bullets and the next version.

   Let me reexamine the base (main) as provided:

        # Changelog

        ## [0.1.31] - 2026-05-28

        ### Changed
        * **[Quality]:** Assured the optimization to hoist regex variables in the ignore loop. Resolved static analysis warnings related to mocking in the shutdown test suite.
        * **[Lifecycle]:** Synced documentation and pruned dead code.


        ## [0.1.30] - 2026-05-27

        ### Changed
        * **[Performance]:** Hoisted loop-invariant truthiness checks and regex property lookups into local scope within the ignore evaluation hot path to reduce evaluation overhead.


        ## [0.1.28] - 2026-05-22

   Now I see: after the bullet points of each version, there are two blank lines (i.e., two newline characters) before the next version header.

   Specifically:

        ... dead code.
        [newline]
        [newline]
        ## [0.1.30] ...

        ... overhead.
        [newline]
        [newline]
        ## [0.1.28] ...

   So the pattern is: each version section ends with two newlines (which in markdown renders as a blank line) and then the next version header.

   Therefore, to insert the [0.1.29] section between [0.1.30] and [0.1.28] in the base (main), we do:

        We take the base (main) and split it at the point after the [0.1.30] section's content (i.e., after the two newlines that follow the bullet points of [0.1.30]) but note that the base (main) already has two newlines and then the [0.1.28] header.

        Actually, we want to replace:

            ... (end of [0.1.30] bullet)
            \n\n
            ## [0.1.28] - 2026-05-22

        with:

            ... (end of [0.1.30] bullet)
            \n\n
            ## [0.1.29] - 2026-05-23\n\n### Changed\n\n* **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.\n\n\n## [0.1.28] - 2026-05-22

        But wait, that would be:

            ... (end of [0.1.30] bullet)
            \n\n
            ## [0.1.29] - 2026-05-23
            \n\n
            ### Changed
            \n\n
            * **[Reliability]:** ...
            \n\n
            ## [0.1.28] - 2026-05-22

        However, note that the base (main) already has two newlines after the [0.1.30] bullet and then the [0.1.28] header. We are inserting the entire [0.1.29] section (which includes its own two newlines after the bullet) and then we want to put the [0.1.28] header.

        But the [0.1.29] section in the head (PR branch) is:

            ## [0.1.29] - 2026-05-23

            ### Changed
            * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

            ## [0.1.28] - 2026-05-22

        So if we take the head's [0.1.29] section and remove the trailing "## [0.1.28] - 2026-05-22" (because we are going to put the base's [0.1.28] and beyond after it), then we have:

            ## [0.1.29] - 2026-05-23

            ### Changed
            * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.

        And then we put two newlines and then the base's content starting from the [0.1.28] header.

        However, note that the base (main) already has two newlines after the [0.1.30] bullet and then the [0.1.28] header. We are going to replace the two newlines and the [0.1.28] header with:

            [two newlines] 
            [the head's [0.1.29] section without the trailing [0.1.28] header] 
            [two newlines] 
            [the base's [0.1.28] header and beyond]

        But wait, the head's [0.1.29] section ends with two newlines and then the [0.1.28] header? Actually, in the head (PR branch) we see:

            ... crash on errors.

            ## [0.1.28] - 2026-05-22

        So there are two newlines between the end of the bullet and the [0.1.28] header.

        Therefore, if we take the head's [0.1.29] section including the two newlines and the [0.1.28] header, we would be duplicating the [0.1.28] header.

        Instead, we want to take the head's [0.1.29] section without the trailing [0.1.28] header and the two newlines that precede it? Actually, no.

        Let me break down the head (PR branch) from the top:

            # Changelog
            ## [0.1.29] - 2026-05-23
            \n\n
            ### Changed
            \n\n
            * **[Reliability]:** ...
            \n\n
            ## [0.1.28] - 2026-05-22
            ... (the rest)

        We want to insert after the base's [0.1.30] section (which ends with two newlines and then the [0.1.28] header) the following:

            ## [0.1.29] - 2026-05-23
            \n\n
            ### Changed
            \n\n
            * **[Reliability]:** ...
            \n\n

        and then we leave the base's [0.1.28] header and beyond.

        So the insertion is exactly the head's [0.1.29] section up to and including the two newlines after its bullet point, but without the [0.1.28] header.

        How many newlines are after the bullet in the head's [0.1.29] section? Two (to make a blank line) and then the next header.

        Therefore, we take from the head (PR branch):

            "## [0.1.29] - 2026-05-23\n\n### Changed\n\n* **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.\n\n"

        and insert that string after the base's [0.1.30] section's content (which ends with two newlines) but before the base's [0.1.28] header.

        However, note that the base (main) already has two newlines after the [0.1.30] bullet and then the [0.1.28] header. We are going to keep those two newlines? Actually, we are replacing the [0.1.28] header and beyond with:

            [inserted string] + [the base's [0.1.28] header and beyond]

        But wait, the base (main) has:

            ... (end of [0.1.30] bullet)
            \n\n
            ## [0.1.28] - 2026-05-22
            ... (rest)

        We want to change it to:

            ... (end of [0.1.30] bullet)
            \n\n
            ## [0.1.29] - 2026-05-23
            \n\n
            ### Changed
            \n\n
            * **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.
            \n\n
            ## [0.1.28] - 2026-05-22
            ... (rest)

        So we are inserting the [0.1.29] section (with its two trailing newlines) between the two newlines after [0.1.30] and the [0.1.28] header.

        But note: the two newlines after [0.1.30] are already there. We are not removing them. We are inserting the [0.1.29] section right after those two newlines and before the [0.1.28] header.

        Therefore, the resolved file is:

            [base (main) from start to the end of the [0.1.30] section's content (i.e., up to and including the two newlines after the bullet)] 
            + 
            [the head's [0.1.29] section without the trailing [0.1.28] header (i.e., the string: "## [0.1.29] - 2026-05-23\n\n### Changed\n\n* **[Reliability]:** Wrapped graceful shutdown routines in isolated `try...except` blocks to ensure application termination does not hang or crash on errors.\n\n")]
            +
            [base (main) from the [0.1.28] header to the end]

        However, note that the base (main) already has the two newlines after the [0.1.30] bullet. We are not duplicating them because we are inserting after them.

        But wait: the base (main) has:

            ... (last bullet of [0.1.30])
            \n\n   [these two newlines are part of the base (main)]
            ## [0.1.28] ...

        We are inserting after those two newlines, so we get:

            ... (last bullet of