<p align="center">
  <svg width="150" height="150" viewBox="0 0 501 501" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M303.85 459.906L250.327 500.049L196.804 459.906C188.588 441.596 187.789 389.341 250.327 326.803C312.864 389.341 312.066 441.596 303.85 459.906Z" fill="#3ECC84"/>
    <path d="M303.85 40.1912L250.327 0.0488281L196.804 40.1912C188.588 58.5017 187.789 110.757 250.327 173.294C312.864 110.757 312.066 58.5017 303.85 40.1912Z" fill="#EE585E"/>
    <path d="M40.4688 303.571L0.326451 250.048L40.4688 196.526C58.7793 188.309 111.035 187.511 173.572 250.048C111.035 312.586 58.7793 311.788 40.4688 303.571Z" fill="#38B0F9"/>
    <path d="M460.184 303.571L500.326 250.048L460.184 196.526C441.874 188.309 389.618 187.511 327.081 250.048C389.618 312.586 441.874 311.788 460.184 303.571Z" fill="#F7C100"/>
    <path d="M436.565 139.503L427.103 73.2713L360.872 63.8099C342.115 70.9476 304.6 107.333 304.6 195.774C393.041 195.774 429.427 158.26 436.565 139.503Z" fill="#F47D28"/>
    <path d="M139.782 436.286L73.5505 426.824L64.089 360.593C71.2267 341.836 107.613 304.321 196.054 304.321C196.054 392.762 158.539 429.148 139.782 436.286Z" fill="#34CBEA"/>
    <path d="M139.782 63.8111L73.5506 73.2726L64.0892 139.504C71.2269 158.261 107.613 195.776 196.054 195.776C196.054 107.335 158.539 70.9489 139.782 63.8111Z" fill="#6D77FA"/>
    <path d="M436.565 360.594L427.104 426.826L360.872 436.287C342.115 429.149 304.6 392.763 304.6 304.322C393.042 304.322 429.427 341.837 436.565 360.594Z" fill="#9AE314"/>
  </svg>
</p>

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
