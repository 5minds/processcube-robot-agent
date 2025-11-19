# Releasing ProcessCube Robot Agent

This document describes the release process for ProcessCube Robot Agent.

## Prerequisites

- Git repository access
- GitHub repository with push permissions
- Commit rights to the repository

## Release Workflow

### 1. Update CHANGELOG.md

Add a new section at the top of `CHANGELOG.md` for the new version:

```markdown
## [0.1.0] - 2025-12-01

### 🎉 Major Features
- Feature 1
- Feature 2

### 🔒 Security
- Security improvement 1

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 📚 Documentation
- Doc update 1
```

**Guidelines:**
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Use semantic versioning: `[MAJOR.MINOR.PATCH]`
- Categories: Features, Security, Bug Fixes, Documentation, Performance, etc.
- Keep latest version at the top

### 2. Update version in pyproject.toml

```toml
[project]
name = "processcube-robot-agent"
version = "0.1.0"  # Update this
```

### 3. Commit changes

```bash
git add CHANGELOG.md pyproject.toml
git commit -m "chore: Prepare release v0.1.0"
```

### 4. Create git tag

```bash
git tag v0.1.0
```

**Tag naming:**
- Always prefix with `v`: `v0.1.0`
- Must match version in CHANGELOG.md and pyproject.toml
- Use semantic versioning

### 5. Push to GitHub

```bash
git push origin main          # or master/develop depending on your branch
git push origin v0.1.0        # Push the tag
```

## What Happens Automatically

Once you push the tag, GitHub Actions automatically:

1. **Validates**: Runs all tests (Python, TypeScript, integration)
2. **Builds**: Creates Docker image with version tag
3. **Extracts**: Parses CHANGELOG.md for release notes
4. **Creates**: GitHub Release with:
   - Release title: `Release v0.1.0`
   - Release body: Extracted from CHANGELOG.md
   - Docker image reference
   - Link to full CHANGELOG.md
   - Auto-detected pre-release flag (for alpha/beta versions)

## Release Notes Extraction

The release process uses an automated script: `scripts/extract_release_notes.py`

### How it works

1. GitHub Actions extracts version from git tag (e.g., `v0.1.0`)
2. Script searches CHANGELOG.md for `## [0.1.0]` section
3. Extracts everything until the next version or EOF
4. Formats as GitHub Release body

### Manual testing

```bash
# Extract notes for a specific version
python scripts/extract_release_notes.py 0.0.1

# Works with or without 'v' prefix
python scripts/extract_release_notes.py v0.0.1
```

## Pre-release Versions

For alpha/beta/rc versions, use semantic versioning:

```
v0.1.0-alpha
v0.1.0-beta.1
v0.1.0-rc.1
```

The workflow automatically marks these as "Pre-release" on GitHub.

## Rollback (if something goes wrong)

If you need to delete a release:

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0
```

Then re-run the release process.

## Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (v1.0.0): Breaking changes, major features
- **MINOR** (v0.1.0): New features, backwards compatible
- **PATCH** (v0.0.1): Bug fixes, minor improvements

## Release Checklist

- [ ] Create/update CHANGELOG.md with new version
- [ ] Update version in `pyproject.toml`
- [ ] Commit changes with `chore: Prepare release vX.Y.Z`
- [ ] Create git tag: `git tag vX.Y.Z`
- [ ] Push commits: `git push origin [branch]`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Wait for GitHub Actions to complete (check Actions tab)
- [ ] Verify GitHub Release was created with correct notes
- [ ] Verify Docker image was built and pushed
- [ ] Announce release if needed

## CI/CD Pipeline Overview

```
Push tag v0.1.0
    ↓
GitHub Actions triggered
    ├─→ test-python (3.11, 3.12)
    ├─→ test-typescript
    ├─→ quality checks
    ├─→ integration tests
    ├─→ build-docker
    └─→ create-release
        ├─ Extract version
        ├─ Parse CHANGELOG.md
        ├─ Create GitHub Release
        └─ Push Docker image
```

## Troubleshooting

### Release not created

Check GitHub Actions:
1. Go to `https://github.com/5minds/processcube-robot-agent/actions`
2. Find the workflow run for your tag
3. Check the "release" job for errors

### CHANGELOG.md extraction failed

Verify format:
```markdown
## [VERSION] - YYYY-MM-DD
### Section
Content...

## [PREVIOUS_VERSION] - YYYY-MM-DD
```

The script looks for `## [0.1.0]` sections.

### Tag not pushed

Verify with:
```bash
git tag -l                    # List all tags
git push origin v0.1.0 -v     # Push with verbose output
```

## Questions?

See the main [README.md](./README.md) for project information.