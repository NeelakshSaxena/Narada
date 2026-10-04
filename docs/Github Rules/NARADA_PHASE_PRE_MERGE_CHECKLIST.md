# NĀRADA — Phase Pre-Merge Checklist

> Use this checklist for **every phase pull request**.
>
> A phase MUST NOT be merged until all applicable blocking checks pass and merge is explicitly authorized.

## Phase Identity

- Phase: `XX — <name>`
- Branch: `phase/XX-<name>`
- Base branch: `<integration branch>`
- Base commit: `<sha>`
- PR: `#<number>`

---

## 1. Scope

- [ ] Phase objective is satisfied.
- [ ] Every phase exit criterion passes.
- [ ] No unrelated feature has been smuggled into the phase.
- [ ] Deferred work has been recorded as an issue/task.

---

## 2. Cross-Phase Changes

- [ ] No earlier-phase code was changed.

**OR**

- [ ] Earlier-phase code was changed because the current phase required it.
- [ ] Original phase/file is recorded.
- [ ] Reason is recorded.
- [ ] Behavioral impact is recorded.
- [ ] Regression coverage is added/updated.
- [ ] The change is not unrelated cleanup.

---

## 3. Code Quality

- [ ] Implementation has been inspected for correctness.
- [ ] No debug code remains.
- [ ] No temporary credentials remain.
- [ ] No accidental generated files are committed.
- [ ] Formatting passes.
- [ ] Lint passes.
- [ ] Type checks pass where applicable.
- [ ] Dependency changes are intentional and documented.

---

## 4. Tests

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Regression tests pass.
- [ ] Failure paths are tested where relevant.
- [ ] Permission/approval behavior is tested where relevant.
- [ ] Restart/recovery behavior is tested where relevant.
- [ ] Docker/container verification passes where relevant.
- [ ] Full phase verification suite passes.

Record exact commands and results in the phase logbook.

---

## 5. Security

- [ ] No secrets are committed.
- [ ] Secret scanning passes.
- [ ] Permissions remain enforced by runtime policy.
- [ ] New tools have risk classification.
- [ ] New consequential actions have approval behavior.
- [ ] Sandbox boundaries remain intact.
- [ ] No new privileged access was introduced without justification.

---

## 6. Documentation Update After Successful Phase Verification

Only perform this section after the technical phase exit criteria pass.

- [ ] Phase logbook updated with implementation work.
- [ ] Phase logbook updated with final verification results.
- [ ] Phase completion summary appended to the same logbook.
- [ ] Project status/roadmap updated.
- [ ] Architecture/design docs updated if behavior changed.
- [ ] README/setup docs updated if setup/commands changed.
- [ ] API/tool/config docs updated if interfaces changed.
- [ ] Changelog/release notes updated if applicable.
- [ ] Verification evidence updated if the repository keeps it.
- [ ] Any category intentionally not updated is explained in the logbook.

---

## 7. Git Review

- [ ] `git status` inspected.
- [ ] Full diff inspected.
- [ ] Staged diff inspected.
- [ ] No unexplained file changes remain.
- [ ] Commit history is understandable.
- [ ] Commit messages identify meaningful changes.
- [ ] Branch name identifies the phase.
- [ ] No secrets or credentials appear in history/diff.

---

## 8. Pull Request Review

- [ ] PR title identifies the phase.
- [ ] Objective is stated.
- [ ] Implementation summary is stated.
- [ ] Cross-phase changes are explicitly listed.
- [ ] Tests and exact verification commands are listed.
- [ ] Documentation changes are listed.
- [ ] Known limitations are listed.
- [ ] Required reviewers have reviewed.
- [ ] Blocking review comments are resolved.
- [ ] CI is green.
- [ ] Required security checks are green.
- [ ] Merge is explicitly authorized.

---

## 9. Merge

- [ ] Approved PR is merged using the repository's approved strategy.
- [ ] Merge commit / resulting commit SHA is recorded.
- [ ] Phase branch is no longer treated as active development.

---

## 10. Post-Merge Verification

- [ ] Integration branch updated locally.
- [ ] Merged commit verified.
- [ ] Smoke tests pass.
- [ ] Relevant regression suite passes.
- [ ] Documentation is present on the integration branch.
- [ ] Phase logbook records merge and post-merge verification.
- [ ] Phase is marked `COMPLETE`.
- [ ] Only after this: create the next phase branch.

---

# STOP CONDITIONS

Stop the merge if ANY of the following is true:

- phase exit criteria are incomplete
- tests are failing
- CI is failing
- secrets are detected
- unexplained files changed
- documentation materially contradicts implementation
- cross-phase changes are unexplained
- blocking review comments remain
- required approval is missing
- post-merge verification is expected to be skipped

When stopped:

```text
STOP
 ↓
record the problem
 ↓
diagnose
 ↓
fix
 ↓
retest
 ↓
update documentation/logbook
 ↓
resume the merge gate
```
