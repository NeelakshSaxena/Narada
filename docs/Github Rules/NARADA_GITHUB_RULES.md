# NĀRADA — Git & GitHub Engineering Rules

> **Status:** Authoritative companion to `NARADA_MASTER_RULES.md`
>
> **Purpose:** Define the mandatory Git/GitHub workflow for phase-based implementation of Nārada.
>
> **Core rule:** Every implementation phase has its own dedicated branch. A later phase may modify code introduced by an earlier phase when necessary, but the change belongs to the later phase and must be verified, documented, and reviewed there.

---

# 1. Repository Is the Source of Implementation History

Git is not merely a backup mechanism. It is the chronological record of how Nārada is built.

The repository must make it possible to answer:

- What phase introduced this behavior?
- Which branch implemented it?
- What changed during that phase?
- What tests proved it worked?
- What earlier code was changed by a later phase?
- Who/what approved the merge?
- What documentation and logbook were updated?

Never rewrite history merely to hide mistakes.

---

# 2. One Dedicated Branch Per Phase

Every implementation phase MUST have its own branch.

Recommended naming:

```text
phase/01-foundation
phase/02-config
phase/03-llm-provider
phase/04-api
phase/05-cli
...
```

The exact descriptive suffix may vary, but the phase number MUST be present.

## Branch rule

```text
main
  │
  ├── phase/01-foundation
  │
  ├── phase/02-config
  │
  ├── phase/03-llm-provider
  │
  └── phase/05-cli
```

A phase branch is the working branch for that phase from start to merge.

Do not implement Phase 05 directly on `main`.

---

# 3. Branch Creation

Before beginning a phase:

1. Ensure the previous phase is formally complete.
2. Ensure the previous phase's logbook has its completion summary appended.
3. Ensure the previous phase branch has been merged or otherwise explicitly integrated according to repository policy.
4. Update the local branch from the current integration point.
5. Create the new phase branch.
6. Create the fresh phase logbook.
7. Record the branch name in the logbook.

Example:

```bash
git switch main
git pull --ff-only
git switch -c phase/05-cli
```

Do not silently branch from an obsolete local commit.

---

# 4. Phase Branch Ownership

A phase branch owns all implementation work required to satisfy that phase's specification.

This includes:

- new code
- modifications to existing code
- tests
- migrations
- configuration changes
- documentation
- Docker changes
- CI changes
- tooling required for the phase
- fixes discovered while verifying the phase

Do not create a separate "fix" branch merely because the file being changed was originally introduced in another phase.

The **current phase owns the correction** when the correction is required to complete the current phase.

---

# 5. Later Phases May Modify Earlier Code

This is an explicit Nārada rule.

Suppose:

```text
Phase 01 → creates `core/config.py`
Phase 05 → discovers `core/config.py` must change for CLI integration
```

Phase 05 MAY modify `core/config.py` directly on:

```text
phase/05-cli
```

It does NOT need to reopen Phase 01 or merge a Phase 01 fix first, unless the issue is independently severe enough to require that process.

The Phase 05 logbook MUST record:

```text
Earlier component affected: core/config.py
Originally introduced by: Phase 01
Reason Phase 05 needed the change: <reason>
Change made: <summary>
Compatibility impact: <impact>
Tests added/updated: <tests>
```

This rule exists because architecture evolves as integration exposes real requirements.

---

# 6. Cross-Phase Change Classification

When a later phase changes earlier code, classify the change.

### A. Required integration change

The earlier component must change for the current phase to work.

Allowed directly on the current phase branch.

### B. Bug discovered in earlier code

The current phase exposes an existing defect.

Allowed directly on the current phase branch if fixing it is necessary for the current phase or its verification.

Record the defect and fix in the current phase logbook.

### C. Refactor unrelated to the current phase

Do not casually perform it.

Defer it to a dedicated phase/task unless it is required to safely implement the current phase.

### D. Security or data-integrity defect

Fix immediately when necessary to prevent unsafe behavior, even if the affected code belongs to an earlier phase.

Document the reason and scope carefully.

---

# 7. No Silent Scope Expansion

A later phase may modify earlier code, but this does NOT grant unlimited refactoring freedom.

Before making a cross-phase change ask:

```text
Is this required for the current phase?
Is it required for correctness?
Is it required for security?
Is it required for maintainability of the feature being implemented?
```

If the answer is no to all four, defer it.

A later phase is allowed to **repair dependencies**, not to use the phase branch as a dumping ground for unrelated cleanup.

---

# 8. Commit Rules

Commits should represent coherent engineering steps.

Prefer:

```text
feat(phase-05): add CLI command routing
fix(phase-05): handle missing config during startup
 test(phase-05): cover CLI startup failure
 docs(phase-05): record CLI verification results
```

Do not use meaningless commits such as:

```text
stuff
changes
final
final2
working
asdf
```

A commit should leave the repository in a comprehensible state whenever practical.

---

# 9. Commit After Meaningful Milestones

Do not wait until the entire phase is finished to make the first commit.

Good commit boundaries include:

- interface created
- core behavior implemented
- tests added
- integration completed
- bug fixed
- documentation updated
- verification completed

Avoid excessive micro-commits that have no useful meaning.

---

# 10. Never Commit Secrets

Never commit:

- API keys
- access tokens
- passwords
- private keys
- OAuth secrets
- session cookies
- production credentials
- personal authentication material
- `.env` files containing secrets

Use:

```text
.env.example
```

for configuration shape only.

Before pushing, inspect staged changes for secrets.

---

# 11. Required Pre-Push Checks

Before pushing a phase branch, the agent MUST:

1. Inspect `git status`.
2. Inspect the diff.
3. Confirm only intended files changed.
4. Check for secrets.
5. Run relevant tests.
6. Run formatting/lint/type checks required by the repository.
7. Update the phase logbook with the work and verification results.

Do not push an unexplained dirty tree.

---

# 12. Phase Documentation Update Is Part of the Phase

A phase is not complete when only code works.

The phase must update the appropriate project documentation.

At minimum, when applicable:

```text
phase logbook
project status / roadmap
architecture documentation
API/tool documentation
README / setup documentation
configuration examples
changelog or release notes
```

Do not update documents mechanically when there is genuinely nothing relevant to change; record that determination in the logbook.

---

# 13. Mandatory Post-Success Update Action

After a phase successfully passes its verification gate, perform the documentation/update sequence **before merge**.

Required sequence:

```text
IMPLEMENT
   ↓
TEST
   ↓
FIX
   ↓
RETEST
   ↓
ALL EXIT CRITERIA PASS
   ↓
UPDATE PHASE LOGBOOK
   ↓
UPDATE PROJECT STATUS / ROADMAP
   ↓
UPDATE RELEVANT DOCS
   ↓
RUN DOC CONSISTENCY CHECK
   ↓
COMMIT DOCUMENTATION
   ↓
FINAL PRE-MERGE CHECK
   ↓
PULL REQUEST
```

The phrase **successful phase** means the phase has passed its technical verification criteria, not merely that the implementation appears finished.

---

# 14. Files to Update After Every Successful Phase

The exact repository paths may evolve, but the phase must evaluate these categories:

```text
1. Phase logbook
2. Project status / roadmap
3. Architecture or design docs affected by the phase
4. README/setup docs affected by the phase
5. API/tool/config docs affected by the phase
6. Changelog/release notes when the project uses them
7. Test evidence / verification records when applicable
```

Recommended structure:

```text
docs/
├── logs/
│   ├── phase-01-logbook.md
│   ├── phase-02-logbook.md
│   └── ...
├── architecture/
├── decisions/
├── status/
└── changelog.md
```

Do not invent documentation merely to satisfy a checklist. Update only documents whose truth changed, and record skipped categories in the phase logbook.

---

# 15. Phase Logbook Must Record Git State

Each phase logbook must contain:

```markdown
## Git / GitHub

- Branch: `phase/05-cli`
- Base commit: `<sha>`
- Important commits:
  - `<sha>` — <description>
- Cross-phase files changed: <list or none>
- Pull request: <number/link when available>
- Review status: <status>
- Merge commit: <sha or pending>
```

If the repository is local-only at that point, record that the GitHub PR step is pending.

---

# 16. Pull Request Is the Phase Review Boundary

A phase branch should normally merge through a pull request.

The PR title should identify the phase.

Example:

```text
Phase 05 — CLI
```

The PR body should contain:

```text
## Objective

## What changed

## Cross-phase changes

## Tests run

## Verification result

## Documentation updated

## Known limitations

## Risk / migration notes

## Approval requirements
```

---

# 17. Mandatory Pre-Merge Checklist

Before merging ANY phase branch:

### Repository state

- [ ] Correct phase branch is checked out.
- [ ] Branch is based on the expected integration point.
- [ ] Working tree is understood and clean or intentionally documented.
- [ ] No unrelated files are included.
- [ ] No secrets are present.

### Phase correctness

- [ ] Phase objective is satisfied.
- [ ] Every phase exit criterion passes.
- [ ] Required tests pass.
- [ ] Regression tests pass.
- [ ] Failure paths are tested where applicable.
- [ ] Restart/recovery behavior is tested where applicable.
- [ ] Security/permission behavior is tested where applicable.
- [ ] Cross-phase modifications are documented.

### Documentation

- [ ] Phase logbook is complete.
- [ ] Phase completion summary is appended.
- [ ] Project status/roadmap is updated.
- [ ] Affected architecture/design docs are updated.
- [ ] Affected README/setup/API/config docs are updated.
- [ ] Changelog/release notes are updated when applicable.
- [ ] Documentation consistency check passes.

### Git/GitHub

- [ ] Commit history is understandable.
- [ ] Diff has been reviewed.
- [ ] PR description is complete.
- [ ] Required reviewers have reviewed the change.
- [ ] CI checks pass.
- [ ] No unresolved blocking review comments remain.
- [ ] Merge is explicitly authorized.

Do not merge merely because CI is green.

---

# 18. Merge Is an Explicit State Transition

The lifecycle is:

```text
phase branch
    ↓
implementation complete
    ↓
verification complete
    ↓
documentation complete
    ↓
PR opened
    ↓
review
    ↓
approval
    ↓
merge
    ↓
post-merge verification
    ↓
phase marked COMPLETE
```

A green build is not the same as an approved merge.

---

# 19. Merge Strategy

Use the repository's chosen merge strategy consistently.

The project should prefer a strategy that preserves understandable phase history.

Do not rewrite shared branch history after others depend on it.

Never force-push to protected integration branches unless the repository's explicit recovery policy permits it.

---

# 20. Post-Merge Verification

After merge:

1. Update the integration branch locally.
2. Verify the merged commit.
3. Run the smoke/regression suite appropriate to the phase.
4. Confirm documentation files are present on the integration branch.
5. Confirm the phase is marked complete.
6. Record the merge commit in the phase logbook.
7. Only then create/start the next phase branch.

If post-merge verification fails:

```text
STOP
 ↓
record failure
 ↓
diagnose
 ↓
fix on the appropriate branch
 ↓
verify
 ↓
record resolution
```

Do not silently declare the phase complete.

---

# 21. Phase Branches Are Not Permanent Product Branches

A phase branch exists to implement one phase.

After successful merge:

```text
phase/05-cli
```

should normally become historical rather than the active development branch.

The next phase starts from the integrated state:

```text
phase/06-memory
```

---

# 22. Hotfixes During a Later Phase

If Phase 06 discovers that Phase 05 has a defect:

### If the fix is necessary for Phase 06

Fix it in:

```text
phase/06-memory
```

and record:

```text
Origin: Phase 05
Discovered by: Phase 06
Reason fixed now: <reason>
Impact: <impact>
Tests: <tests>
```

### If the fix is unrelated to Phase 06

Create a separate bug-fix workflow or defer it.

Do not smuggle unrelated fixes into the phase.

---

# 23. Conflict Resolution

When a phase branch conflicts with the integration branch:

1. Stop and inspect the conflict.
2. Understand both sides.
3. Preserve current phase behavior.
4. Preserve required behavior from earlier phases.
5. Run affected tests.
6. Add a regression test when the conflict reveals a behavioral edge case.
7. Record the resolution in the phase logbook.

Never resolve conflicts by blindly choosing "ours" or "theirs."

---

# 24. Rebase Policy

Rebase only when it improves integration and does not rewrite history that other contributors rely upon.

Never use rebase as a substitute for understanding a conflict.

After a significant rebase, rerun the complete relevant verification suite.

---

# 25. CI Must Enforce the Important Rules

Where practical, CI should automatically check:

- tests
- lint
- formatting
- type checks
- dependency integrity
- secret scanning
- security checks
- Docker build
- migration checks
- documentation consistency
- branch/PR policy

Human review remains required for architectural and consequential decisions.

---

# 26. Required Phase PR Template

The repository should contain a pull request template similar to:

```markdown
## Phase

Phase XX — <name>

## Objective

<what this phase accomplishes>

## Implementation

- ...

## Cross-Phase Changes

- None

or

- `<file>` — originally introduced in Phase XX — changed because ...

## Verification

- [ ] Unit tests
- [ ] Integration tests
- [ ] Regression tests
- [ ] Security/permission tests
- [ ] Restart/recovery tests, if applicable
- [ ] Docker verification, if applicable
- [ ] Full phase exit criteria

## Documentation

- [ ] Phase logbook
- [ ] Status/roadmap
- [ ] Architecture/design docs
- [ ] README/setup/API/config docs
- [ ] Changelog, if applicable

## Risks / Known Limitations

...

## Merge Authorization

- [ ] Required review complete
- [ ] CI green
- [ ] No blocking comments
- [ ] Explicitly approved for merge
```

---

# 27. GitHub Issues / Tasks

Large work discovered during implementation should not disappear into chat history.

Create an issue/task when:

- work is outside the current phase
- a non-blocking bug is discovered
- a design decision needs future work
- technical debt is intentionally deferred
- a security concern requires follow-up
- an infrastructure improvement is needed later

Reference the issue from the phase logbook and PR when useful.

---

# 28. GitHub Actions Must Not Replace Engineering Judgment

Automation may verify:

```text
tests
lint
security scans
builds
secret scans
policy checks
```

Automation must not be treated as proof that:

```text
architecture is correct
permissions are correct
product behavior is correct
risk is acceptable
merge is authorized
```

Those remain engineering decisions.

---

# 29. Documentation and Code Must Move Together

If a successful phase changes behavior, configuration, interfaces, architecture, commands, or deployment behavior, the corresponding documentation MUST be updated in the same phase branch before merge.

Never knowingly merge:

```text
new behavior + old documentation
```

when the documentation is now materially false.

---

# 30. Definition of Done for a Phase

A phase is DONE only when:

```text
code complete
    AND
required tests pass
    AND
phase exit criteria pass
    AND
cross-phase changes documented
    AND
documentation updated
    AND
phase logbook completed
    AND
phase summary appended
    AND
PR reviewed
    AND
CI passes
    AND
merge authorized
    AND
post-merge verification passes
```

Only then may the project advance to the next phase.

---

# 31. Final Principle

> **Every phase has its own branch. Every phase leaves an auditable trail. Later phases may improve earlier code, but never silently. Before merge, code, tests, documentation, logbook, review, and verification must agree about what Nārada actually is.**
