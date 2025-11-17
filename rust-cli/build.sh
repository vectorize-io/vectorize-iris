#!/bin/bash

# Build script for vectorize-iris CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default build mode
BUILD_MODE="debug"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--release)
            BUILD_MODE="release"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -r, --release    Build in release mode (optimized)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Build in debug mode"
            echo "  $0 --release    # Build in release mode"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${YELLOW}Building vectorize-iris CLI in ${BUILD_MODE} mode...${NC}"

# Check if cargo is installed
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}Error: cargo is not installed${NC}"
    echo "Please install Rust from https://rustup.rs/"
    exit 1
fi

# Build the project
if [ "$BUILD_MODE" = "release" ]; then
    cargo build --release
    BINARY_PATH="target/release/vectorize-iris"
else
    cargo build
    BINARY_PATH="target/debug/vectorize-iris"
fi

# Check if build was successful
if [ -f "$BINARY_PATH" ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    echo "Binary location: $BINARY_PATH"
    echo ""
    echo "To run the CLI:"
    echo "  ./$BINARY_PATH --help"
    echo ""
    if [ "$BUILD_MODE" = "debug" ]; then
        echo "Tip: Use --release flag for optimized production builds"
    fi
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
