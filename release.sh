#!/bin/bash

# Release script for individual components
# Usage: ./release.sh <component> <version>
# Example: ./release.sh py 0.1.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <component> <version> [--dry-run]"
    echo ""
    echo "Components:"
    echo "  py      - Python API (pyproject.toml)"
    echo "  node    - Node.js API (package.json)"
    echo "  cli     - Rust CLI (Cargo.toml)"
    echo ""
    echo "Options:"
    echo "  --dry-run    Show what would be done without making changes"
    echo ""
    echo "Examples:"
    echo "  $0 py 0.1.0        # Release Python v0.1.0"
    echo "  $0 node 1.2.3      # Release Node.js v1.2.3"
    echo "  $0 cli 2.0.0       # Release Rust CLI v2.0.0"
    echo "  $0 py 0.1.1 --dry-run  # Preview changes"
    exit 1
}

# Check if we have the required arguments
if [ $# -lt 2 ]; then
    usage
fi

COMPONENT=$1
VERSION=$2
DRY_RUN=false

# Check for --dry-run flag
if [ "${3:-}" = "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Validate version format (semver)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
    echo -e "${RED}Error: Invalid version format. Use semantic versioning (e.g., 0.1.0, 1.2.3)${NC}"
    exit 1
fi

# Determine component details
case $COMPONENT in
    py)
        COMPONENT_NAME="Python API"
        FILE_PATH="python-api/pyproject.toml"
        TAG_PREFIX="py"
        VERSION_PATTERN='version = "'
        ;;
    node)
        COMPONENT_NAME="Node.js API"
        FILE_PATH="nodejs-api/package.json"
        TAG_PREFIX="node"
        VERSION_PATTERN='"version": "'
        ;;
    cli)
        COMPONENT_NAME="Rust CLI"
        FILE_PATH="rust-cli/Cargo.toml"
        TAG_PREFIX="cli"
        VERSION_PATTERN='version = "'
        ;;
    *)
        echo -e "${RED}Error: Unknown component '$COMPONENT'${NC}"
        echo ""
        usage
        ;;
esac

TAG="${TAG_PREFIX}-${VERSION}"

echo -e "${BLUE}Releasing ${COMPONENT_NAME} v${VERSION}${NC}"
echo -e "${BLUE}Tag: ${TAG}${NC}"
echo ""

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo -e "${RED}Error: File not found: $FILE_PATH${NC}"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    if [ "$DRY_RUN" = false ]; then
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Check if tag already exists
if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo -e "${RED}Error: Tag $TAG already exists${NC}"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep -m 1 "$VERSION_PATTERN" "$FILE_PATH" | sed -E 's/.*"([0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?)".*/\1/')
echo -e "Current version: ${YELLOW}${CURRENT_VERSION}${NC}"
echo -e "New version:     ${GREEN}${VERSION}${NC}"
echo ""

# Update version in file
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would update version in: $FILE_PATH${NC}"
    echo -e "${YELLOW}[DRY RUN] Would create commit: 'Release ${COMPONENT_NAME} ${VERSION}'${NC}"
    echo -e "${YELLOW}[DRY RUN] Would create tag: ${TAG}${NC}"
    echo -e "${YELLOW}[DRY RUN] Would push tag to remote${NC}"
    echo ""
    echo -e "${GREEN}Dry run completed successfully${NC}"
    exit 0
fi

echo -e "${YELLOW}Updating version in $FILE_PATH...${NC}"

case $COMPONENT in
    py|cli)
        # TOML format
        sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" "$FILE_PATH"
        ;;
    node)
        # JSON format - more careful replacement
        sed -i.bak "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$VERSION\"/" "$FILE_PATH"
        ;;
esac

# Remove backup file
rm -f "${FILE_PATH}.bak"

# Show the diff
echo -e "${GREEN}✓ Version updated${NC}"
echo ""
git diff "$FILE_PATH"
echo ""

# Confirm before proceeding
read -p "Create commit and tag? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted. Changes have been made but not committed.${NC}"
    echo -e "${YELLOW}To revert: git checkout $FILE_PATH${NC}"
    exit 1
fi

# Create commit
echo -e "${YELLOW}Creating commit...${NC}"
git add "$FILE_PATH"
git commit -m "Release ${COMPONENT_NAME} ${VERSION}"
echo -e "${GREEN}✓ Commit created${NC}"
echo ""

# Create tag
echo -e "${YELLOW}Creating tag ${TAG}...${NC}"
git tag -a "$TAG" -m "Release ${COMPONENT_NAME} ${VERSION}"
echo -e "${GREEN}✓ Tag created${NC}"
echo ""

# Push tag
echo -e "${YELLOW}Pushing tag to remote...${NC}"
git push origin "$TAG"
echo -e "${GREEN}✓ Tag pushed${NC}"
echo ""

# Push commit
echo -e "${YELLOW}Pushing commit to remote...${NC}"
git push
echo -e "${GREEN}✓ Commit pushed${NC}"
echo ""

# Show next steps
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Release ${COMPONENT_NAME} ${VERSION} completed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "GitHub Actions workflow started:"
echo "  https://github.com/$(git remote get-url origin | sed -E 's/.*[:/]([^/]+\/[^/]+)(\.git)?$/\1/')/actions"
echo ""

case $COMPONENT in
    py)
        echo "Once the workflow completes, the package will be available on PyPI:"
        echo "  pip install vectorize-iris==${VERSION}"
        ;;
    node)
        echo "Once the workflow completes, the package will be available on npm:"
        echo "  npm install vectorize-iris@${VERSION}"
        ;;
    cli)
        echo "Once the workflow completes, binaries will be available at:"
        echo "  https://github.com/$(git remote get-url origin | sed -E 's/.*[:/]([^/]+\/[^/]+)(\.git)?$/\1/')/releases/tag/${TAG}"
        ;;
esac

echo ""
