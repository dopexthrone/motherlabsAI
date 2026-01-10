# CI Status Check Verification

## Purpose

This document tracks the process of verifying exact CI status check names before configuring branch protection.

## Problem

GitHub Actions status check names can differ from workflow/job name definitions. Even with stable `name:` values, GitHub may present check names as:
- Job name alone: `tests (py3.11)`
- Workflow / Job: `Tests / tests (py3.11)`
- Or other variations

Branch protection must use the **exact** strings that appear in GitHub's UI, or checks will never match.

## Solution

1. **Create test branch and no-op commit**
2. **Push branch and create PR**
3. **Wait for CI to run**
4. **Copy exact check names from GitHub UI**
5. **Update BRANCH_PROTECTION.md with exact names**
6. **Configure branch protection with exact strings**

## Current Workflow Configuration

File: `.github/workflows/test.yml`

```yaml
jobs:
  tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    name: tests (py${{ matrix.python-version }})
```

**Expected status check names** (to be verified):
- `tests (py3.11)`
- `tests (py3.12)`

**Actual status check names** (to be filled after CI run):
- TBD: Check GitHub UI after first CI run
- TBD: Update BRANCH_PROTECTION.md with actual names
- TBD: Update branch protection configuration

## Steps to Verify

### Step 1: Trigger CI Run

```bash
# Create branch (already done)
git checkout -b ci-verify-status-checks

# Make no-op change (this file)
git add CI_STATUS_CHECK_VERIFICATION.md
git commit -m "docs: add CI status check verification doc (no-op to trigger CI)"

# Push branch
git push -u origin ci-verify-status-checks
```

### Step 2: Create PR

```bash
# Create PR via GitHub CLI (if available)
gh pr create --title "CI: Verify status check names" --body "No-op PR to verify exact CI status check names for branch protection configuration"

# OR create via GitHub web UI:
# https://github.com/dopexthrone/motherlabsAI/compare/main...ci-verify-status-checks
```

### Step 3: Wait for CI and Copy Names

After CI runs:
1. Go to PR page on GitHub
2. Click "Checks" tab or view status checks at bottom of PR
3. Find the status check names (they appear as badges/links)
4. Copy the **exact** strings as they appear

**Example locations**:
- PR page: Bottom of PR description (status check badges)
- PR Checks tab: List of check runs
- Commit page: Status check badges

### Step 4: Update Documentation

Update `BRANCH_PROTECTION.md` with actual status check names:

```markdown
- ✅ Status checks required:
  - `[ACTUAL_NAME_1]` (must pass)  # e.g., "tests (py3.11)" or "Tests / tests (py3.11)"
  - `[ACTUAL_NAME_2]` (must pass)  # e.g., "tests (py3.12)" or "Tests / tests (py3.12)"
```

Update GitHub CLI command in `BRANCH_PROTECTION.md`:

```bash
gh api repos/dopexthrone/motherlabsAI/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["[ACTUAL_NAME_1]","[ACTUAL_NAME_2]"]}' \
  ...
```

### Step 5: Configure Branch Protection

After verifying exact names:

```bash
# Use verified exact names
gh api repos/dopexthrone/motherlabsAI/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["[ACTUAL_NAME_1]","[ACTUAL_NAME_2]"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":0,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

### Step 6: Verify Protection Works

```bash
# Try to force-push (should fail)
git push --force origin main
# Expected: "remote: error: Cannot force-push to a protected branch"

# Try to push without PR (should require PR)
git checkout main
git commit --allow-empty -m "test: direct commit to main (should be blocked)"
git push origin main
# Expected: blocked or requires PR

# Create PR and verify status checks are required
# Expected: Cannot merge until status checks pass
```

## Verification Checklist

- [ ] Test branch created (`ci-verify-status-checks`)
- [ ] No-op commit pushed
- [ ] PR created
- [ ] CI runs and completes
- [ ] Exact status check names copied from GitHub UI
- [ ] BRANCH_PROTECTION.md updated with actual names
- [ ] Branch protection configured with exact names
- [ ] Protection verified (force-push blocked, PR required)

## Current Status

- Branch created: ✅ `ci-verify-status-checks`
- Next: Push no-op commit and create PR
- Then: Wait for CI and copy exact check names
