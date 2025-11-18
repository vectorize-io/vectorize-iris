# Vectorize Iris CLI

**⚡ Lightning-fast AI document extraction from your terminal**

A beautiful, cross-platform CLI for extracting text, tables, and structured data from PDFs, images, and documents. Powered by Vectorize Iris AI.

[![Crates.io](https://img.shields.io/crates/v/vectorize-iris.svg)](https://crates.io/crates/vectorize-iris)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Use the CLI?

- 🎨 **Beautiful output** - Color-coded, formatted terminal display
- ⚡ **Blazing fast** - Native Rust performance
- 🔧 **Scriptable** - JSON/YAML output for automation
- 📦 **Zero dependencies** - Single binary, no runtime needed
- 🌍 **Cross-platform** - Works on Linux, macOS, and Windows
- 🔌 **Pipeline-ready** - Perfect for shell scripts and CI/CD

## Quick Start

### Installation

```bash
curl -fsSL https://raw.githubusercontent.com/vectorize-io/vectorize-iris/refs/heads/main/install.sh | sh
```

**Alternative methods:**
- Download from [GitHub Releases](https://github.com/vectorize-io/vectorize-iris/releases)
- Install with `cargo install vectorize-iris` (requires Rust)

### Authentication

Set your credentials (get them at [vectorize.io](https://vectorize.io)):

```bash
export VECTORIZE_API_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

### Basic Usage

```bash
vectorize-iris document.pdf
```

That's it! Get beautiful, formatted output in your terminal.

## Output Formats

The CLI supports multiple output formats for different use cases:

| Format | Use Case | Command |
|--------|----------|---------|
| **Pretty** (default) | Interactive use, beautiful terminal output | `vectorize-iris doc.pdf` |
| **JSON** | Scripting, piping to `jq` | `vectorize-iris doc.pdf -o json` |
| **YAML** | Config files, human-readable data | `vectorize-iris doc.pdf -o yaml` |
| **Text** | Plain text only, no formatting | `vectorize-iris doc.pdf -o text` |

## Examples

### Basic Text Extraction

```bash
vectorize-iris document.pdf
```

**Output:**
```
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────

✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 7s

─────────────────────────────────────────────────────────
📄 Extracted Text
─────────────────────────────────────────────────────────

Stats: 5536 chars • 1245 words • 89 lines

This is the extracted text from your PDF document.
All formatting and structure is preserved.

Tables, lists, and other elements are properly extracted.
```

## Plain Text Output

```bash
vectorize-iris document.pdf -o text
```

**Output:**
```
This is the extracted text from your PDF document.
All formatting and structure is preserved.

Tables, lists, and other elements are properly extracted.
```

**Pipe to file:**
```bash
vectorize-iris document.pdf -o text > output.txt
```

## JSON Output (for piping)

```bash
vectorize-iris document.pdf -o json
```

**Output:**
```json
{
  "success": true,
  "text": "This is the extracted text from your PDF document...",
  "chunks": null,
  "metadata": null,
  "metadataSchema": null,
  "chunksMetadata": null,
  "chunksSchema": null,
  "error": null
}
```

**Pipe to jq:**
```bash
vectorize-iris document.pdf -o json | jq -r '.text' > output.txt
```

## YAML Output

```bash
vectorize-iris document.pdf -o yaml
```

**Output:**
```yaml
success: true
text: |
  This is the extracted text from your PDF document.
  All formatting and structure is preserved.

  Tables, lists, and other elements are properly extracted.
chunks: null
metadata: null
error: null
```

## Chunking for RAG

```bash
vectorize-iris long-document.pdf --chunk-size 512
```

**Output:**
```
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────

✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 12s

─────────────────────────────────────────────────────────
📊 Document Chunks (16 total)
─────────────────────────────────────────────────────────

Chunk 1 (487 chars)

  # Introduction

  This document covers the basics of machine learning and neural
  networks. We'll explore fundamental concepts and practical
  applications.

Chunk 2 (523 chars)

  ## Neural Networks

  Neural networks are computational models inspired by biological
  neural networks. They consist of interconnected nodes that process
  information.

Chunk 3 (445 chars)

  ### Training Process

  The training process involves adjusting weights through
  backpropagation to minimize loss and improve accuracy.

... (13 more chunks)
```

## JSON Output with Chunks

```bash
vectorize-iris document.pdf --chunk-size 512 -o json | jq '.chunks | length'
```

**Output:**
```
16
```

## Custom Parsing Instructions

```bash
vectorize-iris report.pdf --parsing-instructions "Extract only tables and numerical data, ignore narrative text"
```

**Output:**
```
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────

✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 8s

─────────────────────────────────────────────────────────
📄 Extracted Text
─────────────────────────────────────────────────────────

Stats: 892 chars • 145 words • 24 lines

Q1 2024 Revenue: $1,250,000
Q2 2024 Revenue: $1,450,000
Q3 2024 Revenue: $1,680,000

Region    | Sales  | Growth
----------|--------|-------
North     | $500K  | +12%
South     | $380K  | +8%
East      | $420K  | +15%
West      | $380K  | +10%
```

## Batch Processing Script

```bash
#!/bin/bash

for file in documents/*.pdf; do
  echo "Processing $file..."
  vectorize-iris "$file" -o json > "${file%.pdf}.json"

  if [ $? -eq 0 ]; then
    echo "  ✓ Success: ${file%.pdf}.json"
  else
    echo "  ✗ Failed: $file"
  fi
done
```

**Output:**
```
Processing documents/report-q1.pdf...
  ✓ Success: documents/report-q1.json
Processing documents/report-q2.pdf...
  ✓ Success: documents/report-q2.json
Processing documents/report-q3.pdf...
  ✓ Success: documents/report-q3.json
```

## Extract Text Only (Silent Mode)

```bash
# Suppress progress output, get only text
vectorize-iris document.pdf -o json 2>/dev/null | jq -r '.text'
```

**Output:**
```
This is the extracted text from your PDF document.
All formatting and structure is preserved.

Tables, lists, and other elements are properly extracted.
```

## Save to File

```bash
# Progress shows on terminal, JSON goes to file
vectorize-iris document.pdf -o json > output.json
```

**Terminal shows:**
```
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────

✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 7s
```

**File `output.json` contains:**
```json
{
  "success": true,
  "text": "...",
  ...
}
```

## Pipeline Example

```bash
# Extract, filter, count words
vectorize-iris document.pdf -o json 2>/dev/null | \
  jq -r '.text' | \
  wc -w
```

**Output:**
```
1245
```

## Error Handling

```bash
vectorize-iris nonexistent.pdf
```

**Output:**
```
Error: File not found: nonexistent.pdf
```

## Help

```bash
vectorize-iris --help
```

**Output:**
```
Extract text from files using Vectorize Iris

Usage: vectorize-iris <FILE> [OPTIONS]

Arguments:
  <FILE>  Path to the file to extract text from

Options:
  -o, --output <FORMAT>
          Output format [default: pretty] [possible values: pretty, json, yaml, text]
      --chunk-size <SIZE>
          Chunk size (default: 256)
      --metadata-schema <ID:SCHEMA>
          Metadata schema (format: id:schema, can be repeated)
      --infer-metadata-schema
          Infer metadata schema automatically
      --parsing-instructions <INSTRUCTIONS>
          Parsing instructions for the AI model
      --poll-interval <SECONDS>
          Seconds between status checks [default: 2]
      --timeout <SECONDS>
          Maximum seconds to wait for extraction [default: 300]
      --api-token <TOKEN>
          API token (defaults to VECTORIZE_API_TOKEN env var)
      --org-id <ID>
          Organization ID (defaults to VECTORIZE_ORG_ID env var)
  -h, --help
          Print help
  -V, --version
          Print version
```

## Advanced Examples

### Extract with Multiple Chunks and Metadata

```bash
vectorize-iris document.pdf \
  --chunk-size 256 \
  --infer-metadata-schema \
  --parsing-instructions "Focus on extracting structured data" \
  -o yaml
```

### Custom Credentials

```bash
vectorize-iris document.pdf \
  --api-token "your-token" \
  --org-id "your-org-id"
```

### Longer Timeout

```bash
vectorize-iris large-document.pdf \
  --timeout 600 \
  --poll-interval 5
```

## Output Formats

### Pretty (default)
- Beautiful terminal output with colors and formatting
- Shows progress indicators
- Displays stats and formatted text
- Best for interactive use

### JSON
- Valid JSON output to stdout
- Progress messages to stderr
- Perfect for piping and scripting
- Easily parsed with `jq`

### YAML
- YAML format output to stdout
- Progress messages to stderr
- Human-readable structured data
- Good for config files

### Text
- Plain extracted text only to stdout
- Progress messages to stderr
- No formatting or structure
- Perfect for direct piping to files or other tools

## CLI Options

```
FILE                          Path to file (required)
-o, --output                  Output format: pretty, json, yaml, text (default: pretty)
--chunk-size                  Chunk size in characters (default: 256)
--metadata-schema             Metadata schema (repeatable)
--infer-metadata-schema       Auto-detect metadata structure
--parsing-instructions        Custom parsing instructions
--poll-interval               Seconds between checks (default: 2)
--timeout                     Max seconds to wait (default: 300)
--api-token                   Override VECTORIZE_API_TOKEN
--org-id                      Override VECTORIZE_ORG_ID
```

---

📚 **[Full Documentation](https://docs.vectorize.io)** | 🏠 **[Back to Main README](../README.md)**
