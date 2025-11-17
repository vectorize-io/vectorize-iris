#!/bin/bash

# Install script for vectorize-iris CLI
# Usage: curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/vectorize-iris/main/install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub repository
REPO="YOUR_USERNAME/vectorize-iris"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/bin}"

echo -e "${BLUE}Installing vectorize-iris CLI...${NC}"
echo ""

# Detect OS and architecture
detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)

    case "$os" in
        linux*)
            OS="linux"
            ;;
        darwin*)
            OS="macos"
            ;;
        mingw*|msys*|cygwin*)
            OS="windows"
            ;;
        *)
            echo -e "${RED}Error: Unsupported operating system: $os${NC}"
            exit 1
            ;;
    esac

    case "$arch" in
        x86_64|amd64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            ;;
        *)
            echo -e "${RED}Error: Unsupported architecture: $arch${NC}"
            exit 1
            ;;
    esac

    echo -e "Detected platform: ${GREEN}$OS-$ARCH${NC}"
}

# Get latest release version
get_latest_release() {
    echo -e "${YELLOW}Fetching latest release...${NC}"

    # Try to get the latest release from GitHub API
    LATEST_RELEASE=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

    if [ -z "$LATEST_RELEASE" ]; then
        echo -e "${RED}Error: Could not fetch latest release${NC}"
        exit 1
    fi

    echo -e "Latest version: ${GREEN}$LATEST_RELEASE${NC}"
}

# Download and install binary
install_binary() {
    local binary_name="vectorize-iris"
    local extension=""

    if [ "$OS" = "windows" ]; then
        binary_name="vectorize-iris-${OS}-${ARCH}.exe"
        extension=".zip"
    else
        binary_name="vectorize-iris-${OS}-${ARCH}"
        extension=".tar.gz"
    fi

    local download_url="https://github.com/$REPO/releases/download/$LATEST_RELEASE/${binary_name}${extension}"
    local temp_dir=$(mktemp -d)

    echo -e "${YELLOW}Downloading from: $download_url${NC}"

    if ! curl -sSL -o "$temp_dir/archive${extension}" "$download_url"; then
        echo -e "${RED}Error: Failed to download binary${NC}"
        rm -rf "$temp_dir"
        exit 1
    fi

    # Extract archive
    echo -e "${YELLOW}Extracting archive...${NC}"
    cd "$temp_dir"

    if [ "$OS" = "windows" ]; then
        unzip -q "archive${extension}"
    else
        tar -xzf "archive${extension}"
    fi

    # Create install directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"

    # Install binary
    local install_name="vectorize-iris"
    if [ "$OS" = "windows" ]; then
        install_name="vectorize-iris.exe"
    fi

    echo -e "${YELLOW}Installing to $INSTALL_DIR/$install_name${NC}"

    if [ -f "$binary_name" ]; then
        mv "$binary_name" "$INSTALL_DIR/$install_name"
        chmod +x "$INSTALL_DIR/$install_name"
    else
        echo -e "${RED}Error: Binary not found in archive${NC}"
        rm -rf "$temp_dir"
        exit 1
    fi

    # Cleanup
    rm -rf "$temp_dir"

    echo -e "${GREEN}✓ Installation successful!${NC}"
}

# Check if install directory is in PATH
check_path() {
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo ""
        echo -e "${YELLOW}Warning: $INSTALL_DIR is not in your PATH${NC}"
        echo "Add the following line to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
        echo ""
        echo -e "${GREEN}export PATH=\"\$PATH:$INSTALL_DIR\"${NC}"
        echo ""
    fi
}

# Print usage info
print_usage() {
    echo ""
    echo -e "${GREEN}vectorize-iris CLI has been installed successfully!${NC}"
    echo ""
    echo "Run the following command to get started:"
    echo -e "  ${BLUE}vectorize-iris --help${NC}"
    echo ""
}

# Main installation flow
main() {
    detect_platform
    get_latest_release
    install_binary
    check_path
    print_usage
}

main
