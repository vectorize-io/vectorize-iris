#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Vectorize Iris - Running All Tests  ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Check for test file
TEST_FILE="examples/sample.md"
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}✗ Test file not found: $TEST_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Test file found: $TEST_FILE${NC}"
echo

# Test 1: Python API
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  Testing Python API${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd python-api

if command -v uv &> /dev/null; then
    # Run Python unit tests (in parallel)
    echo "Running Python unit tests..."
    uv run pytest tests/test_models.py -v -n auto

    # Run Python integration tests (in parallel)
    if [ -n "$VECTORIZE_TOKEN" ] && [ -n "$VECTORIZE_ORG_ID" ]; then
        echo -e "\n${BLUE}Running Python integration tests...${NC}"
        VECTORIZE_TOKEN="$VECTORIZE_TOKEN" VECTORIZE_ORG_ID="$VECTORIZE_ORG_ID" uv run pytest tests/test_integration.py -v -s -n auto
    else
        echo -e "${YELLOW}⚠ Skipping Python integration tests (no credentials)${NC}"
    fi
else
    echo -e "${RED}✗ uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python API tests passed${NC}"
cd ..
echo

# Test 2: Node.js/TypeScript API
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  Testing Node.js/TypeScript API${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd nodejs-api

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install > /dev/null 2>&1
fi

# Build TypeScript
echo "Building TypeScript..."
npm run build > /dev/null 2>&1

# Run Node.js unit tests
echo "Running Node.js unit tests..."
npm test -- tests/types.test.ts

# Run Node.js integration tests (if credentials are available)
if [ -n "$VECTORIZE_TOKEN" ] && [ -n "$VECTORIZE_ORG_ID" ]; then
    echo -e "\n${BLUE}Running Node.js integration tests...${NC}"
    VECTORIZE_TOKEN="$VECTORIZE_TOKEN" VECTORIZE_ORG_ID="$VECTORIZE_ORG_ID" npm test -- tests/integration.test.ts
else
    echo -e "${YELLOW}⚠ Skipping Node.js integration tests (no credentials)${NC}"
fi

echo -e "${GREEN}✓ Node.js/TypeScript API tests passed${NC}"
cd ..
echo

# Test 3: Rust CLI
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}  Testing Rust CLI${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd rust-cli

# Build the CLI
echo "Building Rust CLI..."
cargo build --release

# Run unit tests
echo -e "\n${BLUE}Running Rust unit tests...${NC}"
cargo test

# Run integration tests
echo -e "\n${BLUE}Running Rust integration tests...${NC}"

# Test 1: Pretty output (default)
echo "Test 1: Pretty output..."
./target/release/vectorize-iris ../examples/sample.md -o pretty > /tmp/output_pretty.txt
if [ -s /tmp/output_pretty.txt ]; then
    echo -e "${GREEN}  ✓ Pretty output test passed${NC}"
else
    echo -e "${RED}  ✗ Pretty output test failed${NC}"
    exit 1
fi

# Test 2: JSON output
echo "Test 2: JSON output..."
./target/release/vectorize-iris ../examples/sample.md -o json > /tmp/output_json.json
if command -v jq &> /dev/null; then
    if jq empty /tmp/output_json.json 2>/dev/null; then
        echo -e "${GREEN}  ✓ JSON output test passed (valid JSON)${NC}"
    else
        echo -e "${RED}  ✗ JSON output test failed (invalid JSON)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq not found, skipping JSON validation${NC}"
fi

# Test 3: YAML output
echo "Test 3: YAML output..."
./target/release/vectorize-iris ../examples/sample.md -o yaml > /tmp/output_yaml.yaml
if [ -s /tmp/output_yaml.yaml ]; then
    echo -e "${GREEN}  ✓ YAML output test passed${NC}"
else
    echo -e "${RED}  ✗ YAML output test failed${NC}"
    exit 1
fi

# Test 4: With chunking
echo "Test 4: With chunking..."
./target/release/vectorize-iris ../examples/sample.md --chunk-size 512 -o json > /tmp/output_chunks.json
if command -v jq &> /dev/null; then
    CHUNKS=$(jq '.chunks // [] | length' /tmp/output_chunks.json)
    if [ "$CHUNKS" -gt 0 ]; then
        echo -e "${GREEN}  ✓ Chunking test passed ($CHUNKS chunks)${NC}"
    else
        echo -e "${RED}  ✗ Chunking test failed (no chunks found)${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq not found, skipping chunk validation${NC}"
fi

# Test 5: With metadata extraction
echo "Test 5: With metadata extraction..."
./target/release/vectorize-iris ../examples/sample.md --metadata-schema 'doc-info:{"title":"string","summary":"string"}' -o json > /tmp/output_metadata.json
if command -v jq &> /dev/null; then
    if jq -e '.success' /tmp/output_metadata.json > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Metadata extraction test passed${NC}"
        METADATA=$(jq -r '.metadata // "null"' /tmp/output_metadata.json)
        if [ "$METADATA" != "null" ]; then
            echo -e "${BLUE}    Metadata: ${METADATA:0:100}...${NC}"
        fi
    else
        echo -e "${RED}  ✗ Metadata extraction test failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  ⚠ jq not found, skipping metadata validation${NC}"
fi

# Cleanup
rm -f /tmp/output_*.txt /tmp/output_*.json /tmp/output_*.yaml

echo -e "${GREEN}✓ Rust CLI tests passed${NC}"
cd ..
echo

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ All tests passed successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
