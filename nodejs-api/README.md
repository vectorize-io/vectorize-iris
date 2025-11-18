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

# Vectorize Iris Node.js SDK

**Document text extraction for Node.js & TypeScript**

Extract text, tables, and structured data from PDFs, images, and documents with a single async function. Built on Vectorize Iris, the industry-leading AI extraction service.

[![npm version](https://badge.fury.io/js/@vectorize-io%2Firis.svg)](https://badge.fury.io/js/@vectorize-io%2Firis)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Iris?

Traditional OCR tools struggle with complex layouts, poor scans, and structured data. Iris uses advanced AI to deliver:

- ✨ **High accuracy** - Even with poor quality or complex documents
- 📊 **Structure preservation** - Maintains tables, lists, and formatting
- 🎯 **Smart chunking** - Semantic splitting perfect for RAG pipelines
- 🔍 **Metadata extraction** - Extract specific fields using natural language
- 🚀 **TypeScript native** - Full type safety with built-in types
- ⚡ **Async-first** - Promise-based API for modern Node.js

## Quick Start

### Installation

```bash
npm install @vectorize-io/iris
```

### Authentication

Set your credentials (get them at [vectorize.io](https://vectorize.io)):

```bash
export VECTORIZE_API_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

### Basic Usage

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('document.pdf');
console.log(result.text);
```

That's it! Iris handles file upload, extraction, and polling automatically.

## Features

### Basic Text Extraction

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('document.pdf');
console.log(result.text);
```

**Output:**
```
This is the extracted text from your PDF document.
All formatting and structure is preserved.

Tables, lists, and other elements are properly extracted.
```

## Extract from Buffer

```typescript
import { extractText } from '@vectorize-io/iris';
import * as fs from 'fs';

const fileBuffer = fs.readFileSync('document.pdf');
const result = await extractText(fileBuffer, 'document.pdf');

console.log(`Extracted ${result.text.length} characters`);
```

**Output:**
```
Extracted 5536 characters
```

## Chunking for RAG

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';
import type { ExtractionOptions } from '@vectorize-io/iris';

const options: ExtractionOptions = {
  chunkSize: 512
};

const result = await extractTextFromFile('long-document.pdf', options);

result.chunks?.forEach((chunk, i) => {
  console.log(`Chunk ${i+1}: ${chunk.substring(0, 100)}...`);
});
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

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('report.pdf', {
  parsingInstructions: 'Extract only tables and numerical data, ignore narrative text'
});

console.log(result.text);
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

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const result = await extractTextFromFile('invoice.pdf', {
  inferMetadataSchema: true
});

const metadata = JSON.parse(result.metadata!);
console.log(JSON.stringify(metadata, null, 2));
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

## Express.js Integration

```typescript
import express from 'express';
import multer from 'multer';
import { extractText } from '@vectorize-io/iris';
import * as fs from 'fs';

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/extract', upload.single('file'), async (req, res) => {
  try {
    const fileBuffer = fs.readFileSync(req.file!.path);
    const result = await extractText(fileBuffer, req.file!.originalname);

    res.json({
      success: true,
      text: result.text,
      charCount: result.text?.length || 0
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

**Request:**
```bash
curl -F "file=@document.pdf" http://localhost:3000/extract
```

**Response:**
```json
{
  "success": true,
  "text": "This is the extracted text...",
  "charCount": 5536
}
```

## Batch Processing

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';
import * as fs from 'fs/promises';
import * as path from 'path';

async function processDirectory(dirPath: string) {
  const files = await fs.readdir(dirPath);
  const pdfFiles = files.filter(f => f.endsWith('.pdf'));

  for (const file of pdfFiles) {
    const filePath = path.join(dirPath, file);
    console.log(`Processing ${file}...`);

    const result = await extractTextFromFile(filePath);
    const outputPath = filePath.replace('.pdf', '.txt');

    await fs.writeFile(outputPath, result.text!);
    console.log(`  ✓ Saved to ${path.basename(outputPath)}`);
  }
}

processDirectory('./documents');
```

**Output:**
```
Processing report-q1.pdf...
  ✓ Saved to report-q1.txt
Processing report-q2.pdf...
  ✓ Saved to report-q2.txt
Processing report-q3.pdf...
  ✓ Saved to report-q3.txt
```

## Parallel Processing

```typescript
import { extractTextFromFile } from '@vectorize-io/iris';

const files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf'];

const results = await Promise.all(
  files.map(file => extractTextFromFile(file))
);

results.forEach((result, i) => {
  console.log(`${files[i]}: ${result.text?.length || 0} chars`);
});
```

**Output:**
```
doc1.pdf: 3421 chars
doc2.pdf: 5892 chars
doc3.pdf: 2156 chars
```

## Error Handling

```typescript
import { extractTextFromFile, VectorizeIrisError } from '@vectorize-io/iris';

try {
  const result = await extractTextFromFile('document.pdf');
  console.log(result.text);
} catch (error) {
  if (error instanceof VectorizeIrisError) {
    console.error('Extraction failed:', error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

**Output:**
```
Extraction failed: File not found: document.pdf
```

## TypeScript Types

```typescript
import type {
  ExtractionOptions,
  ExtractionResultData,
  MetadataExtractionStrategySchema
} from '@vectorize-io/iris';

// Type-safe options with structured schema (OpenAPI spec format)
const options: ExtractionOptions = {
  chunkSize: 512,
  parsingInstructions: 'Extract code blocks',
  metadataSchemas: [{
    id: 'doc-meta',
    schema: {
      title: 'string',
      author: 'string',
      date: 'string'
    }
  }],
  pollInterval: 2000,
  timeout: 300000
};

// Type-safe result
const result: ExtractionResultData = await extractTextFromFile('doc.pdf', options);

if (result.success) {
  console.log('Text:', result.text);
  console.log('Chunks:', result.chunks?.length);
  console.log('Metadata:', result.metadata);
}
```

## API Reference

### `extractTextFromFile(filePath, options?)`

Extract text from a file.

**Parameters:**
- `filePath` (string): Path to the file
- `options` (ExtractionOptions, optional): Extraction options

**Returns:** `Promise<ExtractionResultData>`

### `extractText(fileBuffer, fileName, options?)`

Extract text from a buffer.

**Parameters:**
- `fileBuffer` (Buffer): File content
- `fileName` (string): File name
- `options` (ExtractionOptions, optional): Extraction options

**Returns:** `Promise<ExtractionResultData>`

## ExtractionOptions

```typescript
interface ExtractionOptions {
  apiToken?: string;              // Override env var
  orgId?: string;                 // Override env var
  pollInterval?: number;          // ms between checks (default: 2000)
  timeout?: number;               // max ms to wait (default: 300000)
  type?: 'iris';                  // Extraction type
  chunkSize?: number;             // Chunk size (default: 256)
  metadataSchemas?: Array<{       // Metadata schemas
    id: string;
    schema: string;
  }>;
  inferMetadataSchema?: boolean;  // Auto-detect metadata
  parsingInstructions?: string;   // Custom instructions
}
```

## ExtractionResultData

```typescript
interface ExtractionResultData {
  success: boolean;
  text?: string;                  // Extracted text
  chunks?: string[];              // Text chunks
  metadata?: string;              // JSON metadata
  metadataSchema?: string;        // Schema ID
  chunksMetadata?: (string|null)[]; // Per-chunk metadata
  chunksSchema?: (string|null)[];   // Per-chunk schemas
  error?: string;                 // Error message
}
```

---

📚 **[Full Documentation](https://docs.vectorize.io)** | 🏠 **[Back to Main README](../README.md)**
