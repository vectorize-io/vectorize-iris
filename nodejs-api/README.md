# Node.js/TypeScript API - Examples

Simple TypeScript library for extracting text from documents using Vectorize Iris.

## Installation

```bash
npm install @vectorize-io/iris
```

Set your credentials:
```bash
export VECTORIZE_API_TOKEN="your-token"
export VECTORIZE_ORG_ID="your-org-id"
```

## Basic Text Extraction

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

// Type-safe options
const options: ExtractionOptions = {
  chunkSize: 512,
  parsingInstructions: 'Extract code blocks',
  metadataSchemas: [{
    id: 'doc-meta',
    schema: 'Extract: title, author, date'
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
