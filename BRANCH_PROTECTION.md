# Branch Protection Configuration

This document describes the recommended branch protection rules for the Motherlabs Kernel repository.

## Main Branch Protection

The `main` branch must be protected to prevent silent invariant violations.

### Required Settings (GitHub Repository Settings → Branches)

1. **Require a pull request before merging**
   - ✅ Required: Yes
   - ✅ Require approvals: 1 (or 0 if solo - still enforces CI check)
   - ✅ Dismiss stale pull request approvals when new commits are pushed: Yes
   - ✅ Require review from Code Owners: Optional (if CODEOWNERS file exists)

2. **Require status checks to pass before merging**
   - ✅ Required: Yes
   - ✅ Require branches to be up to date before merging: Yes
   - ✅ Status checks required:
     - `tests (py3.11)` (must pass)
     - `tests (py3.12)` (must pass)
     - Both test jobs must pass (golden test is included in each)
   - **Note**: These job names are defined in `.github/workflows/test.yml` with `name: tests (py${{ matrix.python-version }})`. If the workflow is updated, these names must be updated here as well.

3. **Require conversation resolution before merging**
   - ✅ Required: Yes (prevents merging with unresolved review comments)

4. **Require linear history**
   - ✅ Required: Yes (enforces rebase-only, helps audit trail)
   - Alternative: Allow squash merges (maintains linear history)

5. **Require signed commits**
   - ⚠️ Optional but recommended for security
   - If enabled: all commits must be GPG signed

6. **Require deployments to succeed before merging**
   - ❌ Not applicable (no deployments configured)

7. **Do not allow bypassing the above settings**
   - ✅ Enforce for administrators: Yes (even admins must follow rules)
   - ⚠️ **Critical**: Prevents accidental force-push that would break history

8. **Allow force pushes**
   - ❌ Never (protects history integrity)

9. **Allow deletions**
   - ❌ Never (protects main branch)

### Rationale

**Why protect main even when solo?**
- Future-you is "another contributor"
- Prevents accidental force-push or direct commits that bypass CI
- Enforces discipline: all changes go through PR + CI check
- Creates audit trail: every change is a PR with test results

**Why require linear history?**
- Makes audit trail clearer
- Easier to track "what changed when"
- Prevents merge commits that obscure semantic changes

**Why require CI to pass?**
- Golden test must run and pass on every change
- Prevents semantic drift
- Catches breaking changes before merge

## How to Configure (GitHub Web UI)

1. Go to repository Settings → Branches
2. Click "Add rule" or "Edit" next to `main` branch
3. Configure settings as described above
4. Click "Save changes"

## How to Configure (GitHub CLI)

```bash
# Install GitHub CLI if not installed
brew install gh

# Authenticate
gh auth login

# Set branch protection rules
gh api repos/dopexthrone/motherlabsAI/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["tests (py3.11)","tests (py3.12)"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":0,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

**Note**: Adjust `required_approving_review_count` based on whether you want to require approvals (0 = CI check only, 1+ = requires approval).

## Workflow for Changes

Even as a solo developer:

1. Create feature branch:
   ```bash
   git checkout -b feature/my-change
   ```

2. Make changes and commit:
   ```bash
   git add ...
   git commit -m "feat: ..."
   ```

3. Push branch:
   ```bash
   git push -u origin feature/my-change
   ```

4. Create PR via GitHub web UI or CLI:
   ```bash
   gh pr create --title "feat: ..." --body "Description..."
   ```

5. Wait for CI to pass (both Python 3.11 and 3.12, including golden test)

6. Merge PR (or self-approve if approval required)

7. Delete feature branch after merge

This workflow ensures:
- ✅ All changes go through CI
- ✅ Golden test runs on every change
- ✅ Linear history maintained
- ✅ Force-push prevented
- ✅ Audit trail for all changes

## Exception Handling

**When you might need to bypass protection (rare):**
- Emergency hotfix (still should go through PR, but can fast-track)
- Repository initialization (one-time setup - already done)
- GitHub Actions configuration fixes (chicken-and-egg problem)

**For emergencies:**
- Use GitHub CLI or web UI to temporarily disable protection
- Make the change
- Re-enable protection immediately
- Document the exception in CHANGELOG.md or a commit message

## Verification

After configuring branch protection:

```bash
# Verify protection is enabled
gh api repos/dopexthrone/motherlabsAI/branches/main/protection | jq .

# Try to force-push (should fail)
git push --force origin main
# Expected: "remote: error: Cannot force-push to a protected branch"
```
