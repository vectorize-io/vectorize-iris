# Vectorize Iris Python SDK

**Document text extraction for Python**

Extract text, tables, and structured data from PDFs, images, and documents with a single function call. Built on Vectorize Iris, the industry-leading AI extraction service.

[![PyPI version](https://badge.fury.io/py/vectorize-iris.svg)](https://badge.fury.io/py/vectorize-iris)
[![Python](https://img.shields.io/pypi/pyversions/vectorize-iris.svg)](https://pypi.org/project/vectorize-iris/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Iris?

Traditional OCR tools struggle with complex layouts, poor scans, and structured data. Iris uses advanced AI to deliver:

- ✨ **High accuracy** - Even with poor quality or complex documents
- 📊 **Structure preservation** - Maintains tables, lists, and formatting
- 🎯 **Smart chunking** - Semantic splitting perfect for RAG pipelines
- 🔍 **Metadata extraction** - Extract specific fields using natural language
- ⚡ **Simple API** - One line of code to extract text

## Quick Start

### Installation

```bash
pip install vectorize-iris
```

### Authentication

Set your credentials (get them at [vectorize.io](https://vectorize.io)):

```bash
export VECTORIZE_API_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

### Basic Usage

```python
from vectorize_iris import extract_text_from_file

result = extract_text_from_file('document.pdf')
print(result.text)
```

That's it! Iris handles file upload, extraction, and polling automatically.

## Features

### Basic Text Extraction

```python
from vectorize_iris import extract_text_from_file

result = extract_text_from_file('document.pdf')
print(result.text)
```

**Output:**
```
This is the extracted text from your PDF document.
All formatting and structure is preserved.

Tables, lists, and other elements are properly extracted.
```

## Extract from Bytes

```python
from vectorize_iris import extract_text

with open('document.pdf', 'rb') as f:
    file_bytes = f.read()

result = extract_text(file_bytes, 'document.pdf')
print(f"Extracted {len(result.text)} characters")
```

**Output:**
```
Extracted 5536 characters
```

## Chunking for RAG

```python
from vectorize_iris import extract_text_from_file, ExtractionOptions

result = extract_text_from_file(
    'long-document.pdf',
    options=ExtractionOptions(
        chunk_size=512
    )
)

for i, chunk in enumerate(result.chunks):
    print(f"Chunk {i+1}: {chunk[:100]}...")
```

**Output:**
```
Chunk 1: # Introduction
This document covers the basics of machine learning...

Chunk 2: ## Neural Networks
Neural networks are computational models inspired by...

Chunk 3: ### Training Process
The training process involves adjusting weights...
```

## Custom Parsing Instructions

```python
from vectorize_iris import extract_text_from_file, ExtractionOptions

result = extract_text_from_file(
    'report.pdf',
    options=ExtractionOptions(
        parsing_instructions='Extract only tables and numerical data, ignore narrative text'
    )
)

print(result.text)
```

**Output:**
```
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

## Inferred Metadata Schema

```python
from vectorize_iris import extract_text_from_file, ExtractionOptions

result = extract_text_from_file(
    'invoice.pdf',
    options=ExtractionOptions(
        infer_metadata_schema=True
    )
)

import json
metadata = json.loads(result.metadata)
print(json.dumps(metadata, indent=2))
```

**Output:**
```json
{
  "document_type": "invoice",
  "invoice_number": "INV-2024-001",
  "date": "2024-01-15",
  "total_amount": 1250.00,
  "currency": "USD",
  "vendor": "Acme Corp"
}
```

## Async API

```python
import asyncio
from vectorize_iris import extract_text_from_file_async

async def extract_multiple():
    files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']

    tasks = [extract_text_from_file_async(f) for f in files]
    results = await asyncio.gather(*tasks)

    for file, result in zip(files, results):
        print(f"{file}: {len(result.text)} chars extracted")

asyncio.run(extract_multiple())
```

**Output:**
```
doc1.pdf: 3421 chars extracted
doc2.pdf: 5892 chars extracted
doc3.pdf: 2156 chars extracted
```

## Error Handling

```python
from vectorize_iris import extract_text_from_file, VectorizeIrisError

try:
    result = extract_text_from_file('document.pdf')
    print(result.text)
except VectorizeIrisError as e:
    print(f"Extraction failed: {e}")
```

**Output:**
```
Extraction failed: File not found: document.pdf
```

## Batch Processing

```python
from vectorize_iris import extract_text_from_file
import glob

for pdf_file in glob.glob('documents/*.pdf'):
    print(f"Processing {pdf_file}...")
    result = extract_text_from_file(pdf_file)

    output_file = pdf_file.replace('.pdf', '.txt')
    with open(output_file, 'w') as f:
        f.write(result.text)

    print(f"  ✓ Saved to {output_file}")
```

**Output:**
```
Processing documents/report-q1.pdf...
  ✓ Saved to documents/report-q1.txt
Processing documents/report-q2.pdf...
  ✓ Saved to documents/report-q2.txt
Processing documents/report-q3.pdf...
  ✓ Saved to documents/report-q3.txt
```

## API Reference

### `extract_text_from_file(file_path, options=None)`

Extract text from a file.

**Parameters:**
- `file_path` (str): Path to the file
- `options` (ExtractionOptions, optional): Extraction options

**Returns:** `ExtractionResultData` with:
- `success` (bool): Whether extraction succeeded
- `text` (str): Extracted text
- `chunks` (list[str], optional): Text chunks if chunking enabled
- `metadata` (str, optional): JSON metadata if requested

### `extract_text(file_bytes, file_name, options=None)`

Extract text from bytes.

**Parameters:**
- `file_bytes` (bytes): File content
- `file_name` (str): File name
- `options` (ExtractionOptions, optional): Extraction options

**Returns:** `ExtractionResultData`

### Async versions

- `extract_text_from_file_async()` - Async version of `extract_text_from_file`
- `extract_text_async()` - Async version of `extract_text`

## ExtractionOptions

```python
ExtractionOptions(
    chunk_size=512,                # default: 256
    parsing_instructions='...',    # custom instructions
    infer_metadata_schema=True,    # auto-detect metadata
    api_token='...',              # override env var
    org_id='...',                 # override env var
    poll_interval=2,              # seconds between checks
    timeout=300                   # max seconds to wait
)
```

---

📚 **[Full Documentation](https://docs.vectorize.io)** | 🏠 **[Back to Main README](../README.md)**
