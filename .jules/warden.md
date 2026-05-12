We are given a merge conflict scenario for the file `.jules/warden.md`.
 We have three versions: ancestor, base (main), and head (PR branch).

 The conflict is in the section around the dates 2026-05-04 and 2026-05-08 (base) and 2026-05-10 (head).

 Let's break down the changes:

 Ancestor (common base) had:
   ## 2026-05-04 — Assessment & Lifecycle
     ... (observation about exact ignore pattern matching) ...
     Alignment / Deferred:
     Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

 Base (main) changed the ancestor's 2026-05-04 section to:
   ## 2026-05-08 — Assessment & Lifecycle   [Note: date changed from 05-04 to 05-08]
     ... (observation about exact ignore pattern matching, with slight wording change) ...
     Alignment / Deferred:
     Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

 Head (PR branch) did not change the 2026-05-04 section (it remains as in the ancestor? but note: the head version provided in the file versions shows that the head has the 2026-05-04 section as in the ancestor? Actually, looking at the head version provided:

   ## 2026-05-04 — Assessment & Lifecycle
     Observation / Pruned:
     Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues.

     Alignment / Deferred:
     Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

 However, note that the base version changed the date to 2026-05-08 and also tweaked the observation and the alignment note.

 But wait: the head version provided in the file versions does not show the 2026-05-08 section? Actually, the head version provided in the file versions shows:

   ... (after the 2026-05-04 section) ...
   ## 2026-05-10 — Assessment & Lifecycle
     ... (new observation about ignore file watcher) ...
     Alignment / Deferred:
     Version bumped to `0.1.26` as a patch release. Updated CHANGELOG.md.

 And the base version has:

   ... (after the 2026-05-02 section) ...
   ## 2026-05-08 — Assessment & Lifecycle
     ... (the observation about exact ignore pattern matching, as modified in base) ...
     Alignment / Deferred:
     Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

 So the conflict is that:

   - Base changed the 2026-05-04 section (from ancestor) to 2026-05-08 and modified the text.
   - Head did not change the 2026-05-04 section (so it remains as in the ancestor) but added a new section for 2026-05-10.

 However, note that the base version also has a section for 2026-05-02 (which is present in both ancestor and head?).

 Let's look at the provided file versions:

 Ancestor:
   ...
   ## 2026-05-04 — Assessment & Lifecycle
     ... (observation) ...
     Alignment / Deferred:
     Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

 Base:
   ...
   ## 2026-05-02 — Assessment & Lifecycle   [Note: this is a new section in base? Actually, looking at the base version provided, it has:
        ## 2026-05-02 — Assessment & Lifecycle
        ... (observation about wildcard ignore patterns) ...
        Alignment / Deferred:
        Version bumped to `0.1.24` as a patch release. Updated CHANGELOG.md.

        ## 2026-05-08 — Assessment & Lifecycle   [this is the changed one from 05-04]
        ...
   ]

 Head:
   ...
   ## 2026-05-04 — Assessment & Lifecycle   [unchanged from ancestor]
   ...
   ## 2026-05-10 — Assessment & Lifecycle   [new]

 So the conflict is not exactly on the same lines? But the problem states:

   Base (main): 3 lines changed (lines 188-194)
   Head (jules-11099419540196164827-07549cf6): 8 lines changed (lines 196-203)

 And the git diff provided shows:

   @@ -192,3 +192,11 @@ Observed the preceding agent optimized the exact ignore pattern matching by spli

   Alignment / Deferred:
   Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
   +
   +## 2026-05-10 — Assessment & Lifecycle
   +
   +Observation / Pruned:
   +Observed the preceding agent optimized the ignore file watcher hot paths by hoisting loop-invariant wildcard regex checks and caching method lookups, avoiding redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues.
   +
   +Alignment / Deferred:
   +Version bumped to `0.1.26` as a patch release. Updated CHANGELOG.md.

 This diff is showing that the base (which is the target branch) had, at the end of the 2026-05-04 section (or rather, the section that was 2026-05-04 in the ancestor and became 2026-05-08 in base) three lines:

      Alignment / Deferred:
      Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

 And the head branch added 8 lines (so 11 total) after that.

 However, note that the base version actually changed the date of that section to 2026-05-08 and also changed the observation and the alignment note.

 But the git diff provided is only showing the head changes relative to the base? Let me read the diff again:

   The diff is: "Head changes vs base"

   So it's showing what the head branch has that the base doesn't, and what the base has that the head doesn't? Actually, the format is:

      @@ -<start in base>,<number of lines in base> +<start in head>,<number of lines in head> @@

   Here: -192,3 +192,11

   Meaning: in the base, starting at line 192, there are 3 lines that are being replaced by 11 lines in the head.

   But wait, the base version of the file (as provided in the file versions) does not have the 2026-05-10 section. It has the 2026-05-08 section.

   However, the diff shows that the base had 3 lines at that position (which are the alignment/deferred lines for the 2026-05-08 section?).

   Actually, let's reconstruct:

   In the base version, the section for 2026-05-08 ends with:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

   And then the next section would be ... but the base version provided in the file versions does not show anything after that? Actually, the base version provided in the file versions ends with that section? Or maybe there is more? But the truncation says middle section.

   The key is: the diff shows that the base had 3 lines at that location (which are the two lines of the alignment/deferred and maybe an empty line? or the three lines are:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

   But wait, that's only two lines? Unless there's an empty line after.

   Actually, the diff output shows:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

   And then the head adds:

        (empty line)
        ## 2026-05-10 — Assessment & Lifecycle
        (empty line)
        Observation / Pruned:
        ... (the observation) ...
        (empty line)
        Alignment / Deferred:
        Version bumped to `0.1.26` as a patch release. Updated CHANGELOG.md.

   So the base had:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

   (and note: the base version actually has a slightly different string for the version bump: "reflecting the performance optimization", but the diff shows the base as having the string without that?).

   This is confusing.

   Let me look at the provided base version in the file versions:

        ## 2026-05-08 — Assessment & Lifecycle

        Observation / Pruned:
        Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations against individual path segments in the hot path. I verified this via the test suite and confirmed structural soundness. Static analysis tools reported no dead code or linting issues.

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

   And the head version in the file versions for the 2026-05-04 section (which is unchanged from ancestor) is:

        ## 2026-05-04 — Assessment & Lifecycle

        Observation / Pruned:
        Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues.

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

   But note: the base version changed the date to 2026-05-08 and also changed the observation and the alignment note.

   However, the git diff provided (Head changes vs base) is only showing the addition of the 2026-05-10 section. It does not show the change in the 2026-05-04/05-08 section.

   Why? Because the base branch changed the 2026-05-04 section to 2026-05-08 and modified the text, and the head branch did not change that section (so it remains as in the ancestor, which is 2026-05-04). Therefore, there is a conflict in that section as well.

   But the problem states:

        Base (main): 3 lines changed (lines 188-194)
        Head (jules-11099419540196164827-07549cf6): 8 lines changed (lines 196-203)

   And the git diff provided is only for the head changes relative to base? And it shows an addition of 8 lines (so 11 total) at the end of the base's 2026-05-08 section.

   However, the base branch also changed the 2026-05-04 section (which in the ancestor was at a certain location) to 2026-05-08. So the base branch has changes in two places? But the problem says base changed 3 lines (lines 188-194) and head changed 8 lines (lines 196-203). This suggests that the conflict is only in one contiguous block?

   Alternatively, the 3 lines changed in base (lines 188-194) might be the change from the ancestor's 2026-05-04 section to the base's 2026-05-08 section? And the head branch did not change those lines (so they remain as in the ancestor) but then added 8 lines after (at lines 196-203).

   Let me try to map:

   Ancestor at the relevant part:

        ...
        ## 2026-05-04 — Assessment & Lifecycle   [let's say this starts at line 188?]
        Observation / Pruned:
        Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues.

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
        ...

   Base changed that to:

        ## 2026-05-08 — Assessment & Lifecycle   [so line 188 changed from 05-04 to 05-08]
        ... (then the observation was changed slightly) ...
        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

   So the base changed:
        line 188: the date
        and then some words in the observation and the alignment note.

   But the problem says base changed 3 lines (lines 188-194). So perhaps the entire block from line 188 to 194 in the ancestor was replaced by 3 lines in the base? That doesn't seem to match.

   Alternatively, the 3 lines changed in base might be the three lines that are the alignment/deferred block? But that block is two lines of text and maybe an empty line?

   Given the confusion, let's rely on the provided file versions and the resolution rules.

   We are to keep ALL meaningful changes from both branches.

   Changes in base (main) relative to ancestor:
        - Changed the date of the section from 2026-05-04 to 2026-05-08.
        - Changed the observation text:
            ancestor: "Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues."
            base: "Observed the preceding agent optimized the exact ignore pattern matching by splitting `exact_ignores` into simple and compound frozensets, preventing redundant evaluations against individual path segments in the hot path. I verified this via the test suite and confirmed structural soundness. Static analysis tools reported no dead code or linting issues."
        - Changed the alignment note:
            ancestor: "Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md."
            base: "Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md."

   Changes in head (PR branch) relative to ancestor:
        - Left the 2026-05-04 section unchanged (so it remains as in the ancestor).
        - Added a new section for 2026-05-10:
            ## 2026-05-10 — Assessment & Lifecycle
            Observation / Pruned:
            Observed the preceding agent optimized the ignore file watcher hot paths by hoisting loop-invariant wildcard regex checks and caching method lookups, avoiding redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues.
            Alignment / Deferred:
            Version bumped to `0.1.26` as a patch release. Updated CHANGELOG.md.

   However, note: the base branch also has a section for 2026-05-02 (which is present in the ancestor? Let's check the ancestor file versions:

        Ancestor:
          ...
          ## 2026-04-26 — Assessment & Lifecycle
          ...
          Alignment / Deferred:
          Version bumped to `0.1.19` as a patch release. Updated CHANGELOG.md.

          ## 2026-04-02 — Assessment & Lifecycle
          ...
          Alignment / Deferred:
          Version bumped to `0.1.24` as a patch release. Updated CHANGELOG.md.

          ... [truncated] ...

          ## 2026-05-04 — Assessment & Lifecycle
          ...

        So the ancestor does not have a 2026-05-02 section? But the base and head versions both have:

          ## 2026-05-02 — Assessment & Lifecycle
          ... (observation about wildcard ignore patterns) ...
          Alignment / Deferred:
          Version bumped to `0.1.24` as a patch release. Updated CHANGELOG.md.

        This suggests that the ancestor file versions provided in the problem statement are truncated, and the 2026-05-02 section is actually present in the ancestor? But the ancestor section provided in the problem statement does not show it.

        However, the problem states that the ancestor is the common base, and then the base and head branches both have the 2026-05-02 section. So it must be that the ancestor had that section, but it was truncated in the display.

        Therefore, we can assume that the 2026-05-02 section is the same in ancestor, base, and head.

   Now, the conflict:

        The base branch changed the 2026-05-04 section (to 2026-05-08 and modified text).
        The head branch did not change the 2026-05-04 section (so it remains as in the ancestor) but added a new section for 2026-05-10.

   However, note: the base branch changed the date to 2026-05-08, so in the base branch, the section that was 2026-05-04 in the ancestor is now 2026-05-08.

   In the head branch, the section is still 2026-05-04.

   Therefore, we have two different sections:

        Base:
            ## 2026-05-08 — Assessment & Lifecycle
            ... (modified observation) ...
            Alignment / Deferred:
            Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

        Head:
            ## 2026-05-04 — Assessment & Lifecycle
            ... (original observation) ...
            Alignment / Deferred:
            Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
            ## 2026-05-10 — Assessment & Lifecycle
            ... (new observation) ...
            Alignment / Deferred:
            Version bumped to `0.1.26` as a patch release. Updated CHANGELOG.md.

   But wait, the head branch does not have the 2026-05-08 section? It has the 2026-05-04 section and then the 2026-05-10 section.

   How do we resolve?

   According to the rules:

        1. This is a TRUE CONFLICT — both branches modified the same file from the same ancestor.
        2. Keep ALL meaningful changes from BOTH branches.

   We have two sets of changes:

        Base changed:
            - The date of the section (from 05-04 to 05-08)
            - The observation text (added "against individual path segments", added verification sentence, changed "confirmed" to "reported ... issues")
            - The alignment note (added "reflecting the performance optimization")

        Head changed:
            - Left the 2026-05-04 section as is (so no change there) but then added a new section for 2026-05-10.

   However, note: the base branch did not add the 2026-05-10 section, and the head branch did not change the 2026-05-04 section (so it remains as ancestor) but the base branch changed that section to 2026-05-08.

   Therefore, the two branches have made conflicting changes to the same logical section (the one that was 2026-05-04 in the ancestor).

   We must keep all meaningful changes from both branches. But we cannot have two different dates for the same section.

   How to resolve the conflict in the section?

        The base branch changed the date to 2026-05-08 and modified the text.
        The head branch kept the date as 2026-05-04 and the original text.

   Since the base branch changed the date and the head branch did not, and the base branch's change is a date bump (which is meaningful) and also text changes, we have to choose.

   Rule 3:
        - If they modify the same logic, prefer the HEAD branch (PR author's intent) unless the base has an obvious bug fix or security patch.

   Here, the base branch changed the date and the text. Is this an obvious bug fix or security patch? The changes are about documentation of a performance optimization. It doesn't sound like a bug fix or security patch.

   Therefore, we should prefer the HEAD branch for the conflicting part? But note: the head branch did not change that section at all (it kept the ancestor version). So if we prefer the head branch, we would keep the ancestor version for that section.

   However, the base branch's changes are also meaningful. We are supposed to keep ALL meaningful changes.

   But we cannot have both the date 05-04 and 05-08 for the same section.

   Alternative: maybe the base branch intended to move the section to a later date because they made a change on that date? And the head branch added a new section for a later date (05-10) without changing the existing section.

   In a changelog, it is common to have sections in chronological order. The ancestor had:

        2026-04-26
        2026-04-02
        ... [older] ...
        2026-05-04

   The base branch changed the 2026-05-04 section to 2026-05-08, meaning they are saying the change happened on 2026-05-08.

   The head branch kept the section as 2026-05-04 and added a new section for 2026-05-10.

   This suggests that the base branch believes the optimization was done on 2026-05-08, while the head branch believes it was done on 2026-05-04 (and then did another optimization on 2026-05-10).

   Without knowing the actual dates of the changes, we have to rely on the branches.

   However, note: the base branch is the target branch (main) and has newer changes from others. The head branch is the PR branch.

   The base branch's change (to 2026-05-08) might be correcting the date to when the change was actually made.

   But the head branch's PR author did not change that section, meaning they agree with the ancestor's date (2026-05-04) for that optimization.

   Given the rule: prefer HEAD unless base has an obvious bug fix or security patch.

   Since this is a documentation change (changelog) and not a bug fix, we should prefer the head branch for the conflicting part.

   Therefore, for the section that was 2026-05-04 in the ancestor, we keep the head branch's version (which is the same as the ancestor: date 2026-05-04 and the original observation text and alignment note).

   Additionally, we keep the head branch's new section for 2026-05-10.

   But what about the base branch's changes to that section? We are not taking them because we are preferring the head branch for the conflicting part.

   However, note: the base branch also has a section for 2026-05-02 (which is the same in both) and then the section we are discussing.

   And the head branch has the 2026-05-02 section, then the 2026-05-04 section (as ancestor), then the 2026-05-10 section.

   The base branch has the 2026-05-02 section, then the 2026-05-08 section (which is the changed version of the ancestor's 2026-05-04).

   Since we are taking the head branch's version for the conflicting section (so we keep the 2026-05-04 section as in ancestor), we do not include the base branch's 2026-05-08 section.

   But wait: the base branch's change to the section might be considered meaningful and we are supposed to keep all meaningful changes. However, the head branch did not make that change, so if we take the head branch's version we are losing the base branch's change.

   Alternatively, we might consider that the base branch's change is a correction and should be kept. But the rule says to prefer head unless base has an obvious bug fix.

   Since it's not an obvious bug fix, we prefer head.

   However, let's look at the exact changes in the base branch for that section:

        Date: changed from 05-04 to 05-08 -> this is a correction of the date.
        Observation:
            base: "preventing redundant evaluations against individual path segments in the hot path. I verified this via the test suite and confirmed structural soundness. Static analysis tools reported no dead code or linting issues."
            ancestor/head: "preventing redundant evaluations in the hot path. Tests passed successfully and static analysis tools confirmed no dead code or lint issues."

        The base branch's observation is more detailed and includes verification. This seems like an improvement in the documentation.

        Alignment note:
            base: "Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md."
            ancestor/head: "Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md."

        The base branch added "reflecting the performance optimization", which is meaningful.

   Given that the base branch's changes are improvements to the documentation (more precise, added verification note, and clarified the release note), and the head branch did not make any change to that section (so it's still the less detailed version), we might want to keep the base branch's changes.

   But the rule says: prefer head unless base has an obvious bug fix or security patch.

   This is not a bug fix or security patch, so we should prefer head.

   However, note: the head branch's PR author might have intentionally not changed that section because they believed the ancestor version was correct. But the base branch (which is main) has newer changes from others, meaning others have reviewed and approved the base branch's change.

   In a typical merge, if the base branch has a change that is not controversial and the head branch didn't touch it, we would take the base branch's change. But here, the head branch did not change that section, so there is no conflict in the sense of two different changes to the same lines?

   Actually, there is a conflict because the base branch changed the section and the head branch did not. But in a 3-way merge, if one branch changed it and the other didn't, we take the change from the branch that changed it.

   However, the problem states: "This is a TRUE CONFLICT — both branches modified the same file from the same ancestor"

   And then it says base changed 3 lines (lines 188-194) and head changed 8 lines (lines 196-203). This implies that the changes are in adjacent but non-overlapping lines?

   Let me assume that the file lines are:

        ...
        188: ... (part of the 2026-05-04 section in ancestor)
        189: ...
        190: ...
        191: ...
        192: Alignment / Deferred:
        193: Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
        194: (empty line or next section)
        195: ...
        196: ... (start of head's added section)

   But the base branch changed lines 188-194 (which in the ancestor were the 2026-05-04 section) to something else (the 2026-05-08 section with modified text).

   The head branch changed lines 196-203 (which in the ancestor were after the 2026-05-04 section) by adding 8 lines (so inserting the 2026-05-10 section).

   Therefore, the two changes are in non-overlapping line ranges. So there is no actual conflict in the version control sense?

   But the problem says it's a true conflict.

   Alternatively, the base branch's change to lines 188-194 might have shifted the lines, so that the head branch's change (which was based on the ancestor) now applies to different lines.

   Specifically, in the ancestor, the 2026-05-04 section ended at line 194 (say). Then the head branch, based on the ancestor, wanted to add something after line 194.

   But the base branch changed the 2026-05-04 section to be longer or shorter, so that the point after the 2026-05-04 section is now at a different line number.

   However, the git diff provided (Head changes vs base) shows:

        @@ -192,3 +192,11 @@
        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
        +
        +## 2026-05-10 — Assessment & Lifecycle
        + ...

   This means that in the base branch, at line 192, there are 3 lines that are:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.

   And the head branch, instead of those 3 lines, has 11 lines (the 3 lines plus 8 new lines).

   But wait, the base branch's version of those 3 lines is actually:

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md.

   So the base branch changed the second line of that block.

   Therefore, the base branch changed lines 193 (if we count the two lines of text and maybe an empty line as three lines) and the head branch is trying to add after that block.

   However, the base branch's change to the alignment note (line 193) is a change that the head branch did not make. So when merging, we have:

        Base:
            line 192: "Alignment / Deferred:"
            line 193: "Version bumped to `0.1.25` as a patch release reflecting the performance optimization. Updated CHANGELOG.md."
            line 194: (maybe empty or next section starts)

        Head (based on ancestor):
            line 192: "Alignment / Deferred:"
            line 193: "Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md."
            line 194: (empty)
            line 195: "## 2026-05-10 — Assessment & Lifecycle"
            ...

   So the conflict is that the base branch changed line 193, and the head branch inserted new content starting at what was line 194 in the ancestor (which is now line 195 in the base?).

   But the head branch's changes are based on the ancestor, so in the head branch, after the alignment/deferred block (which is two lines) there is an empty line and then the new section.

   In the base branch, the alignment/deferred block is two lines (but the second line is changed) and then presumably an empty line and then the next section? Or maybe the base branch did not have an empty line?

   The git diff shows that the base branch had 3 lines at that position (which we are interpreting as the two lines of the block and one empty line? or three lines of text?).

   Given the diff output:

        -192,3 +192,11

   and the context:

        @@ -192,3 +192,11 @@ Observed the preceding agent optimized the exact ignore pattern matching by spli

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
        +

   It seems that the three lines in the base are:

        line 192: (empty?) -> but the context shows "Observed ..." and then a blank line? Actually, the context line is: "Observed the preceding agent optimized the exact ignore pattern matching by spli"

   So the three lines in the base starting at line 192 are:

        line 192: (the rest of the observation line? or empty?) -> actually, the context is the last part of the observation.

   Let me read the diff again:

        @@ -192,3 +192,11 @@ Observed the preceding agent optimized the exact ignore pattern matching by spli

        Alignment / Deferred:
        Version bumped to `0.1.25` as a patch release. Updated CHANGELOG.md.
        +

   This means:

        In the base, starting at line 192, there are