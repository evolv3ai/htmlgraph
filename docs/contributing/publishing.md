# Publishing Guide

How to publish new releases of HtmlGraph.

## Version Numbering

HtmlGraph uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.1.0 → 1.2.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.1.0 → 1.1.1)

## Files to Update

When bumping version, update **all four** of these files:

1. `pyproject.toml` - Python package version
2. `src/python/htmlgraph/__init__.py` - `__version__ = "X.Y.Z"`
3. `packages/claude-plugin/.claude-plugin/plugin.json` - Claude plugin version
4. `packages/gemini-extension/gemini-extension.json` - Gemini extension version

## Publishing Checklist

### Pre-Release

- [ ] All tests pass: `uv run pytest`
- [ ] Code is formatted: `ruff format src/`
- [ ] Code is linted: `ruff check src/`
- [ ] Type checks pass: `mypy src/python/htmlgraph`
- [ ] Documentation is up to date
- [ ] Changelog is updated
- [ ] Version bumped in all 4 files
- [ ] Changes committed to git

### Build

```bash
# Clean previous builds
rm -rf dist/

# Build distributions
uv build
```

This creates:

- `dist/htmlgraph-X.Y.Z.tar.gz` (source distribution)
- `dist/htmlgraph-X.Y.Z-py3-none-any.whl` (wheel)

### Publish to PyPI

```bash
# Ensure credentials are set
source .env

# Publish to PyPI
uv publish dist/htmlgraph-X.Y.Z* --token "$PyPI_API_TOKEN"
```

### Post-Release

- [ ] Create git tag: `git tag vX.Y.Z`
- [ ] Push tag: `git push origin vX.Y.Z`
- [ ] Create GitHub release
- [ ] Update plugin installations
- [ ] Announce release

## PyPI Credentials Setup

### Option 1: API Token in .env (Recommended)

Create `.env` file:

```bash
PyPI_API_TOKEN=pypi-YOUR_TOKEN_HERE
```

Then source it before publishing:

```bash
source .env
uv publish dist/htmlgraph-X.Y.Z* --token "$PyPI_API_TOKEN"
```

### Option 2: Environment Variable

```bash
export PYPI_TOKEN=pypi-YOUR_TOKEN_HERE
uv publish dist/htmlgraph-X.Y.Z* --token "$PYPI_TOKEN"
```

### Option 3: CLI Arguments

```bash
uv publish dist/htmlgraph-X.Y.Z* --token pypi-YOUR_TOKEN_HERE
```

## Complete Publishing Commands

```bash
# 1. Update version in all 4 files
# (Manual step - edit files)

# 2. Update changelog
# (Manual step - edit docs/changelog.md)

# 3. Commit version bump
git add .
git commit -m "chore: bump version to X.Y.Z"

# 4. Build distributions
rm -rf dist/
uv build

# 5. Publish to PyPI
source .env
uv publish dist/htmlgraph-X.Y.Z* --token "$PyPI_API_TOKEN"

# 6. Create and push git tag
git tag vX.Y.Z
git push origin vX.Y.Z

# 7. Create GitHub release
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Release notes here"

# 8. Verify publication
open https://pypi.org/project/htmlgraph/
pip install htmlgraph==X.Y.Z
```

## Automation Script

Save as `scripts/release.sh`:

```bash
#!/bin/bash
set -e

# Check for version argument
if [ -z "$1" ]; then
    echo "Usage: ./release.sh X.Y.Z"
    exit 1
fi

VERSION=$1

echo "Releasing version $VERSION..."

# Update versions (requires manual editing first)
echo "⚠️  Ensure versions are updated in all 4 files!"
read -p "Press enter to continue..."

# Run tests
echo "Running tests..."
uv run pytest

# Build
echo "Building distributions..."
rm -rf dist/
uv build

# Publish
echo "Publishing to PyPI..."
source .env
uv publish dist/htmlgraph-$VERSION* --token "$PyPI_API_TOKEN"

# Git tag
echo "Creating git tag..."
git tag v$VERSION
git push origin v$VERSION

# GitHub release
echo "Creating GitHub release..."
gh release create v$VERSION --title "v$VERSION" --generate-notes

echo "✅ Release $VERSION complete!"
echo "   PyPI: https://pypi.org/project/htmlgraph/$VERSION/"
echo "   GitHub: https://github.com/Shakes-tzd/htmlgraph/releases/tag/v$VERSION"
```

Usage:

```bash
chmod +x scripts/release.sh
./scripts/release.sh 0.3.0
```

## Post-Release Updates

### Update Claude Plugin

```bash
claude plugin update htmlgraph
```

### Update Gemini Extension

```bash
gemini extension update htmlgraph
```

### Update Codex Skill

```bash
codex skill update htmlgraph
```

## Verify Publication

```bash
# Check PyPI page
open https://pypi.org/project/htmlgraph/

# Install from PyPI to test
pip install htmlgraph==X.Y.Z

# Verify version
python -c "import htmlgraph; print(htmlgraph.__version__)"
```

## Safety & Rollback

### Safety

⚠️ **PyPI uploads are permanent!** You cannot:

- Delete a published version
- Re-upload the same version
- Modify published files

Always test in a staging environment first.

### Rollback

If a release has issues:

```bash
# Yank the bad version (hides from pip install)
uv publish --yank htmlgraph==X.Y.Z

# Publish a fixed version
# Increment version to X.Y.Z+1
uv build && uv publish dist/*
```

## Version History

- **0.3.0** (2024-12-22): TrackBuilder API, multi-agent support
- **0.2.2** (2024-12-20): Drift detection, session improvements
- **0.2.0** (2024-12-18): Track creation, specs and plans
- **0.1.x** (2024-12-15): Initial release, basic features

See [Changelog](../changelog.md) for details.

## Next Steps

- [Development Guide](development.md) - Development setup
- [Contributing Guide](index.md) - General guidelines
