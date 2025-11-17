# Vectorize Iris - Simple Text Extraction

**Extract text from any document with AI-powered precision.**

Vectorize Iris is an advanced document extraction service that uses AI to accurately extract text, structure, and metadata from PDFs, images, and other document formats. Unlike traditional OCR tools, Iris understands document structure, preserves formatting, and can extract specific information using natural language instructions.

## Why Iris?

Traditional text extraction tools struggle with:
- Complex layouts (multi-column documents, tables, forms)
- Poor quality scans or images
- Mixed content types (text, tables, images)
- Structured data extraction
- Preserving document semantics

**Iris solves these problems** by using advanced AI models that understand document structure and context, delivering:
- ✨ **High accuracy** - Even with poor quality or complex documents
- 📊 **Structure preservation** - Maintains tables, lists, and formatting
- 🎯 **Smart chunking** - Splits documents at semantic boundaries
- 🔍 **Metadata extraction** - Extract specific fields using natural language
- 🚀 **Simple API** - One function call to extract text

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
import { extractTextFromFile } from 'vectorize-iris';

const result = await extractTextFromFile('document.pdf');
console.log(result.text);
```

[→ See Node.js examples](nodejs-api/)

### ⚡ Rust CLI
```bash
vectorize-iris document.pdf
```

[→ See CLI examples](rust-cli/)

## Installation

**Python:**
```bash
pip install vectorize-iris
```

**Node.js:**
```bash
npm install vectorize-iris
```

**Rust CLI:**
```bash
curl -fsSL https://install.vectorize.io/iris | sh
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
Extract structured data using natural language:
```python
result = extract_text_from_file('invoice.pdf', options=ExtractionOptions(
    metadata_schemas=[{
        'id': 'invoice-data',
        'schema': 'Extract: invoice_number, date, total_amount, vendor_name'
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

## Configuration

Set your API credentials:

```bash
export VECTORIZE_API_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

Get your credentials at [Vectorize Console](https://vectorize.io).

## Documentation

For detailed documentation, API reference, and advanced features:

📚 **[docs.vectorize.io](https://docs.vectorize.io)**

## Examples

See the [examples](examples/) directory for sample documents and complete usage examples.

## License

MIT

## Support

- 📖 [Documentation](https://docs.vectorize.io)
- 💬 [Community](https://vectorize.io/community)
- 🐛 [Issues](https://github.com/vectorize/vectorize-iris/issues)
