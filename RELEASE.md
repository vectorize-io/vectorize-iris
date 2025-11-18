# Release Process

This document describes how to release new versions of the vectorize-iris project.

## Quick Reference

```bash
# Release Python API
./release.sh py 0.1.0

# Release Node.js API
./release.sh node 0.2.0

# Release Rust CLI
./release.sh cli 1.0.0

# Dry run (preview changes)
./release.sh py 0.1.1 --dry-run
```

## Overview

Each component (Python, Node.js, Rust CLI) has an **independent release lifecycle** with its own version number:

- **Python API**: Tagged as `py-x.y.z` → Published to PyPI
- **Node.js API**: Tagged as `node-x.y.z` → Published to npm
- **Rust CLI**: Tagged as `cli-x.y.z` → Released as GitHub binaries

Use the `release.sh` script to easily release any component.

## Prerequisites

Before you can create releases, you need to configure the following:

### 1. PyPI Trusted Publishing (for Python releases)

PyPI uses **Trusted Publishing** (OIDC), which requires no tokens or passwords:

1. Go to https://pypi.org/manage/account/publishing/ (or create the project first via manual upload)
2. Add a new "pending publisher" for your package:
   - **PyPI Project Name**: `vectorize-iris`
   - **Owner**: Your GitHub username or org (e.g., `vectorize-io`)
   - **Repository name**: `vectorize-iris`
   - **Workflow name**: `release.yml`
   - **Environment name**: (leave blank)
3. Save the publisher

**Note**: If the package doesn't exist on PyPI yet, you'll need to do a one-time manual upload first, then configure Trusted Publishing in the project settings.

For more info: https://docs.pypi.org/trusted-publishers/

### 2. npm Trusted Publishing (for Node.js releases)

npm uses **Provenance** (similar to PyPI's Trusted Publishing), which requires no tokens:

1. Make sure you have publishing rights to the `@vectorize-io/iris` package on npm
2. The package must already exist on npm (do a manual publish first if needed)
3. Once published, npm automatically trusts releases from GitHub Actions with `--provenance` flag

**No additional setup required** - npm will automatically verify the GitHub Actions identity using OIDC.

For more info: https://docs.npmjs.com/generating-provenance-statements

### 3. Update install.sh

Before the first release, update the `REPO` variable in `install.sh`:

```bash
REPO="YOUR_USERNAME/vectorize-iris"  # Change this to your actual GitHub username/org
```

## Creating a Release

Use the `release.sh` script to release any component:

```bash
# Release Python API
./release.sh py 0.1.0

# Release Node.js API
./release.sh node 0.2.0

# Release Rust CLI
./release.sh cli 1.0.0

# Preview changes without making them (dry run)
./release.sh py 0.1.1 --dry-run
```

### What the Script Does

The release script will:

1. Validate the version format (semantic versioning)
2. Check for uncommitted changes
3. Update the version in the appropriate file:
   - Python: `python-api/pyproject.toml`
   - Node.js: `nodejs-api/package.json`
   - Rust: `rust-cli/Cargo.toml`
4. Show you the changes and ask for confirmation
5. Create a git commit
6. Create and push a component-specific tag (`py-x.y.z`, `node-x.y.z`, or `cli-x.y.z`)
7. Push the commit to the remote repository

### GitHub Actions Workflow

When the tag is pushed, GitHub Actions will automatically:

- **Python (`py-*` tags)**: Build and publish to PyPI
- **Node.js (`node-*` tags)**: Build and publish to npm
- **Rust CLI (`cli-*` tags)**:
  - Build binaries for multiple platforms (Linux x86_64/ARM64, macOS Intel/Apple Silicon, Windows)
  - Create a GitHub release with downloadable binaries

## Version Numbering

This project uses semantic versioning (SemVer):

- **MAJOR** version (v1.0.0): Incompatible API changes
- **MINOR** version (v0.1.0): New functionality (backwards compatible)
- **PATCH** version (v0.0.1): Bug fixes (backwards compatible)

## Component Versions

Each component maintains its own version independently:

- **Python API** (`python-api/pyproject.toml`): Currently tracks the Python package version
- **Node.js API** (`nodejs-api/package.json`): Currently tracks the npm package version
- **Rust CLI** (`rust-cli/Cargo.toml`): Currently tracks the CLI binary version

**Note**: The `release.sh` script automatically updates the version in the appropriate file, so you don't need to manually edit these files before releasing.

## Installation Methods

After a release is created, users can install each package:

### Python
```bash
pip install vectorize-iris
```

### Node.js
```bash
npm install vectorize-iris
```

### Rust CLI (via install script)
```bash
curl -fsSL https://raw.githubusercontent.com/vectorize-io/vectorize-iris/refs/heads/main/install.sh | sh
```

Or download binaries directly from the [GitHub Releases page](https://github.com/YOUR_USERNAME/vectorize-iris/releases).

## Supported Platforms (Rust CLI)

The Rust CLI is built for the following platforms:

- **Linux**: x86_64, aarch64 (ARM64)
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)
- **Windows**: x86_64

## Troubleshooting

### Release workflow fails

1. Check the GitHub Actions logs for specific errors
2. Verify all secrets are correctly set up
3. Ensure version numbers are updated in all package files
4. Make sure you have permissions to publish to PyPI and npm

### Install script fails

1. Verify the REPO variable in `install.sh` is correct
2. Check that the GitHub release contains the expected binary assets
3. Ensure the platform is supported (see list above)

## Manual Release (if needed)

If the automated workflow fails, you can manually release individual components:

### Python
```bash
# Update version in python-api/pyproject.toml first
cd python-api
python -m build

# Manual upload (requires PyPI credentials)
python -m twine upload dist/*

# Or just create and push the tag to trigger automated release
git tag py-0.1.0
git push origin py-0.1.0
```

### Node.js
```bash
# Update version in nodejs-api/package.json first
cd nodejs-api
npm run build
npm publish --access public  # Required for scoped packages (@vectorize-io/iris)
# Note: Add --provenance flag when publishing from CI for trusted publishing

# Create and push tag
git tag node-0.2.0
git push origin node-0.2.0
```

### Rust CLI
```bash
# Update version in rust-cli/Cargo.toml first
cd rust-cli
cargo build --release

# Create and push tag (this will trigger GitHub Actions to build all platforms)
git tag cli-1.0.0
git push origin cli-1.0.0
```

## Examples

### Release a single component
```bash
# I just fixed a bug in the Python API
./release.sh py 0.1.1
```

### Release multiple components independently
```bash
# Python got a new feature
./release.sh py 0.2.0

# Node.js got the same feature
./release.sh node 0.3.0

# CLI doesn't need an update (stays at current version)
```

### Preview before releasing
```bash
# Check what will change
./release.sh py 0.2.0 --dry-run

# If it looks good, run without --dry-run
./release.sh py 0.2.0
```
