# Branch Protection Configuration - Updated with Expected Status Check Names

## Status Check Name Format

Based on GitHub Actions behavior with matrix strategy and explicit job names:

**Workflow file**: `.github/workflows/test.yml`
- Workflow name: `Tests`
- Job name (with `name:` field): `tests (py${{ matrix.python-version }})`
- Matrix values: `["3.11", "3.12"]`

**Expected Status Check Names** (common formats, to be verified):
- Format 1: `tests (py3.11)`, `tests (py3.12)` (job name alone - most common with explicit `name:` field)
- Format 2: `Tests / tests (py3.11)`, `Tests / tests (py3.12)` (workflow / job name)
- Format 3: `tests / tests (py3.11)`, `tests / tests (py3.12)` (job / job name - rare)

**Note**: The explicit `name: tests (py${{ matrix.python-version }})` field in the workflow file ensures stable naming.

## Recommended Approach

Since we can't verify the exact format without a CI run, we have two options:

### Option A: Wait for First CI Run (Recommended)

1. **Wait for next push/PR to trigger CI**
   - Any commit to main will trigger CI
   - Or create a test PR from any branch
   
2. **Copy exact names from GitHub UI**
   - Go to repository → Actions tab
   - Or PR → Checks tab
   - Copy exact status check names

3. **Update branch protection with exact names**

### Option B: Configure with Most Likely Format (Can Update Later)

Based on GitHub Actions behavior with explicit `name:` field, the most likely format is:
- `tests (py3.11)`
- `tests (py3.12)`

You can configure branch protection with these names, and if they don't match, GitHub will show you the available check names when you try to set them.

## GitHub CLI Command (Using Expected Names)

```bash
# Using expected format (will need verification)
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

**Note**: If the names don't match, GitHub will return an error with available check names, which you can then use.

## Alternative: Web UI Configuration (Shows Available Names)

1. Go to repository Settings → Branches
2. Click "Add rule" or edit `main` branch
3. In "Require status checks to pass before merging":
   - GitHub will show you the available status check names
   - Select the two Python version checks
   - Copy the exact names shown

This is the safest approach as GitHub shows you the exact available names.

## Verification Steps

After configuring (regardless of method):

1. **Check protection is enabled**:
   ```bash
   gh api repos/dopexthrone/motherlabsAI/branches/main/protection | jq .
   ```

2. **Try to force-push** (should fail):
   ```bash
   git push --force origin main
   # Expected: "remote: error: Cannot force-push to a protected branch"
   ```

3. **Create test PR** and verify:
   - Status checks are required
   - Cannot merge until both checks pass
   - Force-push is blocked

## Current Workflow Configuration

The workflow file (`.github/workflows/test.yml`) uses:
- Explicit `name:` field: `tests (py${{ matrix.python-version }})`
- This ensures stable, predictable status check names
- The format should be consistent: `tests (py3.11)`, `tests (py3.12)`

However, GitHub sometimes adds workflow name prefix, so verification is recommended.

## Recommended Action

**For maximum accuracy**: Use GitHub web UI to configure branch protection, as it shows available status check names directly.

**For automation**: Try the CLI command with expected names, and if it fails, use the error message to get correct names.
