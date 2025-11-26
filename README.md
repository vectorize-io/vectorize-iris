<p align="center">
  <img src="iris.svg" alt="Vectorize Iris" width="200" />
</p>

# Vectorize Iris

Vectorize Iris is a model-based extraction solution that transforms how RAG systems handle PDFs. It combines extraction and chunking into one streamlined process, making it easier than ever to get clean, usable text from complex documents.

Documentation: [docs.vectorize.io](https://docs.vectorize.io/build-deploy/extract-information/extraction-tester/#vectorize-iris)

## Table of Contents

- [Why Iris?](#why-iris)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Features](#features)
  - [Basic Text Extraction](#basic-text-extraction)
  - [Smart Chunking](#smart-chunking)
  - [Metadata Extraction](#metadata-extraction)
  - [Parsing Instructions](#parsing-instructions)
- [CLI Examples](#cli-examples)
  - [Basic Extraction](#basic-extraction)
  - [Extract from URL](#extract-from-url)
  - [JSON Output](#json-output-for-piping)
  - [Plain Text Output](#plain-text-output)
  - [Save to File](#save-to-file)
  - [Process Directory](#process-directory)
  - [Chunking for RAG](#chunking-for-rag)
  - [Custom Parsing Instructions](#custom-parsing-instructions)
  - [Document Classification](#document-classification)
  - [Advanced Options](#advanced-options)
- [Configuration](#configuration)
  - [CLI Configuration](#cli-configuration)
  - [Python & Node.js Configuration](#python--nodejs-configuration)
- [Documentation](#documentation)
- [License](#license)
- [Support](#support)

## Why Iris?

Traditional OCR tools struggle with complex layouts, poor scans, and structured data. **Iris uses advanced AI** to understand document structure and context, delivering:

- 📄 **Universal format support** - Works with all unstructured document types (PDFs, images, scans, and more)
- ✨ **High accuracy** - Handles poor quality scans and complex layouts
- 📊 **Structure preservation** - Maintains tables, lists, and formatting
- 🎯 **Smart chunking** - Semantic splitting for RAG pipelines
- 🔍 **Metadata extraction** - Extract specific fields using natural language
- 🚀 **Simple API** - One function call to extract text
- ⚡ **Parallel processing** - Process multiple documents simultaneously
- 🌐 **URL support** - Extract directly from HTTP/HTTPS URLs
- 📂 **Batch processing** - Process entire directories automatically
- 🔧 **Multiple formats** - Output as JSON, YAML, or plain text
- 🪶 **Lightweight** - Single binary CLI with no dependencies
- ☁️ **Cloud-native** - Serverless-ready APIs
- 🌍 **Multi-lingual** - 100+ languages including Hindi, Arabic, Chinese
- 🔌 **Multi-platform** - Python, Node.js, and CLI support

## Quick Start

Choose your preferred tool:

### 🐍 Python API
```python
from vectorize_iris import extract_text_from_file

result = extract_text_from_file('document.pdf')
print(result.text)
```

[→ See Python examples](python-api/)

### 📦 Node.js/TypeScript API
```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('document.pdf');
console.log(result.text);
```

[→ See Node.js examples](nodejs-api/)

### ⚡ CLI

```bash
vectorize-iris document.pdf
```

## Installation

**CLI:**
```bash
curl -fsSL https://get-iris.vectorize.io | sh
```


**Python:**
```bash
pip install vectorize-iris
```

**Node.js:**
```bash
npm install @vectorize-io/iris
```



## Features

### Basic Text Extraction
Extract clean, structured text from any document format.

### Smart Chunking
Split documents into semantic chunks perfect for RAG pipelines:
- Markdown-aware chunking
- Configurable chunk sizes
- Preserves context across chunks

### Metadata Extraction
Extract structured data using JSON schemas (OpenAPI spec format recommended):
```python
result = extract_text_from_file('invoice.pdf', options=ExtractionOptions(
    metadata_schemas=[{
        'id': 'invoice-data',
        'schema': {
            'invoice_number': 'string',
            'date': 'string',
            'total_amount': 'number',
            'vendor_name': 'string'
        }
    }]
))
# Returns structured JSON metadata
```

### Parsing Instructions
Guide the extraction with custom instructions:
```python
result = extract_text_from_file('document.pdf', options=ExtractionOptions(
    parsing_instructions='Focus on extracting tables and ignore headers/footers'
))
```

## CLI Examples

### Basic Extraction

Beautiful terminal output with progress indicators:

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

### Extract from URL

Download and extract files directly from HTTP/HTTPS URLs:

```bash
vectorize-iris https://arxiv.org/pdf/2206.01062
```

### JSON Output (for piping)

```bash
vectorize-iris document.pdf -o json
```

**Output:**
```json
{
  "success": true,
  "text": "This is the extracted text from your PDF document...",
  "chunks": null,
  "metadata": null
}
```

**Pipe to jq:**
```bash
vectorize-iris document.pdf -o json | jq -r '.text' > output.txt
```

### Plain Text Output

Get only the extracted text:

```bash
vectorize-iris document.pdf -o text
```

**Pipe directly:**
```bash
vectorize-iris document.pdf -o text > output.txt
```

### Save to File

Use `-f` to save output directly:

```bash
vectorize-iris document.pdf -o json -f output.json
```

**Output:**
```
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────

✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 7s
✓ Output written to output.json
```

### Process Directory

Process all files in a directory automatically:

```bash
vectorize-iris ./documents -f ./output
```

**Output:**
```
📦 Processing Directory
──────────────────────────────────────────────────

💡 Found 5 files to process

⚙️  Processing 1/5 - report-q1.pdf
✨ Vectorize Iris Extraction
──────────────────────────────────────────────────
✓ Upload prepared
✓ File uploaded successfully
✓ Extraction started
✓ Extraction completed in 8s
✓ Output written to output/report-q1.txt

⚙️  Processing 2/5 - report-q2.pdf
...

──────────────────────────────────────────────────
✨ Batch Processing Complete

  ✓ Successful: 5
```

**With custom output format:**
```bash
# Extract all PDFs to JSON
vectorize-iris ./documents -o json -f ./output

# Extract all files to plain text
vectorize-iris ./scans -o text -f ./extracted
```

### Chunking for RAG

```bash
vectorize-iris long-document.pdf --chunk-size 512
```

Splits documents at semantic boundaries, perfect for RAG pipelines.

### Custom Parsing Instructions

```bash
vectorize-iris report.pdf --parsing-instructions "Extract only tables and numerical data, ignore narrative text"
```

### Document Classification

Pass multiple metadata schemas and Iris will automatically classify which schema matches best:

```bash
vectorize-iris invoice.pdf \
  --metadata-schema 'invoice:{"invoice_number":"string","date":"string","total_amount":"number","vendor":"string"}' \
  --metadata-schema 'receipt:{"store_name":"string","date":"string","items":"array","total":"number"}' \
  --metadata-schema 'contract:{"parties":"array","effective_date":"string","terms":"string"}' \
  --metadata-schema 'cv:{"name":"string","contact_info":"object","skills":"array","experience":"array"}' \
  -o json
```

**Output:**
```json
{
  "success": true,
  "text": "...",
  "metadata": "{\"invoice_number\":\"INV-2024-001\",\"date\":\"2024-01-15\",\"total_amount\":1250.00,\"vendor\":\"Acme Corp\"}",
  "metadataSchema": "invoice"
}
```

Iris automatically detected this was an invoice and extracted the relevant fields using the matching schema.

### Advanced Options

```bash
# Custom chunk size with metadata extraction
vectorize-iris document.pdf \
  --chunk-size 256 \
  --infer-metadata-schema \
  --parsing-instructions "Focus on extracting structured data" \
  -o yaml -f output.yaml

# Longer timeout for large documents
vectorize-iris large-document.pdf \
  --timeout 600 \
  --poll-interval 5
```

## Configuration

### CLI Configuration

The CLI offers multiple ways to configure your credentials:

#### Interactive Configuration (Recommended)

The easiest way to get started - opens your browser for authentication:

```bash
vectorize-iris configure
```

**What happens:**
1. Opens your browser to the Vectorize platform
2. Click "Authorize" to grant access
3. Credentials are automatically saved to `~/.vectorize-iris/credentials`
4. Done! You're ready to extract

#### Manual Configuration

If you prefer not to use the browser, prompt for credentials manually:

```bash
vectorize-iris configure --manual
```

You'll be asked to enter:
- Access Token
- Organization ID

Get these from [platform.vectorize.io](https://platform.vectorize.io) → Account → Org Settings → Access Tokens

#### Non-Interactive Configuration

For scripts and automation, pass credentials directly:

```bash
vectorize-iris configure --api-token "your-token" --org-id "your-org-id"
```

#### Environment Variables

Alternatively, set credentials via environment variables (works for all clients):

```bash
export VECTORIZE_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

### Python & Node.js Configuration

For Python and Node.js clients, use environment variables or pass credentials programmatically:

**Environment variables:**
```bash
export VECTORIZE_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

**Python:**
```python
from vectorize_iris import VectorizeIrisClient

client = VectorizeIrisClient(
    api_token="your-token",
    org_id="your-org-id"
)
```

**Node.js:**
```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('document.pdf', {
    apiToken: 'your-token',
    orgId: 'your-org-id'
});
```

## Documentation

For detailed documentation, API reference, and advanced features:

📚 **[docs.vectorize.io](https://docs.vectorize.io)**

## License

MIT

## Support

- 📖 [Documentation](https://docs.vectorize.io)
- 💬 [Community](https://vectorize.io/community)
- 🐛 [Issues](https://github.com/vectorize/vectorize-iris/issues)
