/**
 * Vectorize Iris - Simple Text Extraction API
 * Extract text from files using Vectorize Iris with a single function call.
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import fetch from 'node-fetch';
import type {
  StartFileUploadRequest,
  StartFileUploadResponse,
  StartExtractionRequest,
  StartExtractionResponse,
  ExtractionResult,
  ExtractionResultData,
  ExtractionOptions,
  MetadataExtractionStrategySchema,
} from './types';

export type {
  ExtractionOptions,
  ExtractionResultData,
  MetadataExtractionStrategySchema,
};

export class VectorizeIrisError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'VectorizeIrisError';
  }
}

/**
 * Internal function to extract from file buffer
 */
async function _extractFromBuffer(
  fileBuffer: Buffer,
  fileName: string,
  apiToken: string,
  orgId: string,
  pollInterval: number,
  timeout: number,
  options: ExtractionOptions
): Promise<ExtractionResultData> {
  const baseUrl = `https://api.vectorize.io/v1/org/${orgId}`;
  const headers = {
    'Authorization': `Bearer ${apiToken}`,
    'Content-Type': 'application/json'
  };

  const fileSize = fileBuffer.length;

  // Step 1: Start file upload and get presigned URL
  const uploadRequest: StartFileUploadRequest = {
    name: fileName,
    contentType: 'application/octet-stream'
  };

  const uploadResponse = await fetch(`${baseUrl}/files`, {
    method: 'POST',
    headers,
    body: JSON.stringify(uploadRequest)
  });

  if (!uploadResponse.ok) {
    const errorText = await uploadResponse.text();
    throw new VectorizeIrisError(
      `Failed to start upload: ${uploadResponse.status} - ${errorText}`
    );
  }

  const uploadData = await uploadResponse.json() as StartFileUploadResponse;

  // Step 2: Upload file to presigned URL
  const putResponse = await fetch(uploadData.uploadUrl, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/octet-stream',
      'Content-Length': fileSize.toString()
    },
    body: fileBuffer
  });

  if (![200, 201, 204].includes(putResponse.status)) {
    const errorText = await putResponse.text();
    throw new VectorizeIrisError(
      `Failed to upload file: ${putResponse.status} - ${errorText}`
    );
  }

  // Step 3: Start extraction
  const extractionRequest: StartExtractionRequest = {
    fileId: uploadData.fileId,
    type: options.type,
    chunkSize: options.chunkSize,
    parsingInstructions: options.parsingInstructions
  };

  // Add metadata (default inferSchema to true)
  const inferSchema = options.inferMetadataSchema !== undefined ? options.inferMetadataSchema : true;
  if (options.metadataSchemas || inferSchema) {
    extractionRequest.metadata = {
      schemas: options.metadataSchemas,
      inferSchema: inferSchema
    };
  }

  // Remove undefined fields
  Object.keys(extractionRequest).forEach(key => {
    if (extractionRequest[key as keyof StartExtractionRequest] === undefined) {
      delete extractionRequest[key as keyof StartExtractionRequest];
    }
  });

  const extractionResponse = await fetch(`${baseUrl}/extraction`, {
    method: 'POST',
    headers,
    body: JSON.stringify(extractionRequest)
  });

  if (!extractionResponse.ok) {
    const errorText = await extractionResponse.text();
    throw new VectorizeIrisError(
      `Failed to start extraction: ${extractionResponse.status} - ${errorText}`
    );
  }

  const extractionData = await extractionResponse.json() as StartExtractionResponse;

  // Step 4: Poll for completion
  const startTime = Date.now();

  while (true) {
    if (Date.now() - startTime > timeout) {
      throw new VectorizeIrisError(`Extraction timed out after ${timeout}ms`);
    }

    const statusResponse = await fetch(`${baseUrl}/extraction/${extractionData.extractionId}`, {
      method: 'GET',
      headers
    });

    if (!statusResponse.ok) {
      const errorText = await statusResponse.text();
      throw new VectorizeIrisError(
        `Failed to check status: ${statusResponse.status} - ${errorText}`
      );
    }

    const result = await statusResponse.json() as ExtractionResult;

    if (result.ready) {
      if (!result.data) {
        throw new VectorizeIrisError('Extraction completed but no data was returned');
      }

      if (!result.data.success) {
        const errorMsg = result.data.error || 'Unknown error';
        throw new VectorizeIrisError(`Extraction failed: ${errorMsg}`);
      }

      return result.data;
    }

    // Still processing, wait and retry
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
}

/**
 * Extract text from file bytes using Vectorize Iris
 *
 * @param fileBuffer - File content as Buffer
 * @param fileName - Name of the file (default: "document.pdf")
 * @param options - Extraction options
 * @returns Promise that resolves to extraction result data
 * @throws {VectorizeIrisError} If extraction fails or times out
 *
 * @example
 * ```typescript
 * import * as fs from 'fs';
 * import { extractText } from 'vectorize-iris';
 *
 * const fileBuffer = fs.readFileSync('document.pdf');
 * const result = await extractText(fileBuffer, 'document.pdf');
 * console.log(result.text);
 * console.log(result.chunks);  // If chunking was requested
 * ```
 */
export async function extractText(
  fileBuffer: Buffer,
  fileName: string = 'document.pdf',
  options: ExtractionOptions = {}
): Promise<ExtractionResultData> {
  const {
    apiToken = process.env.VECTORIZE_TOKEN,
    orgId = process.env.VECTORIZE_ORG_ID,
    pollInterval = 2000,
    timeout = 300000,
    type = 'iris',
    ...extractionOptions
  } = options;

  // Validate credentials
  if (!apiToken || !orgId) {
    throw new VectorizeIrisError(
      'Missing credentials. Set VECTORIZE_TOKEN and VECTORIZE_ORG_ID ' +
      'environment variables or pass them in options.'
    );
  }

  return _extractFromBuffer(
    fileBuffer,
    fileName,
    apiToken,
    orgId,
    pollInterval,
    timeout,
    { type, ...extractionOptions }
  );
}

/**
 * Extract text from a file using Vectorize Iris
 *
 * @param filePath - Path to the file to extract text from
 * @param options - Extraction options
 * @returns Promise that resolves to extraction result data
 * @throws {VectorizeIrisError} If extraction fails or times out
 * @throws {Error} If file doesn't exist
 *
 * @example
 * ```typescript
 * import { extractTextFromFile } from 'vectorize-iris';
 *
 * // Simple extraction
 * const result = await extractTextFromFile('document.pdf');
 * console.log(result.text);
 *
 * // With custom chunk size
 * const result = await extractTextFromFile('document.pdf', {
 *   chunkSize: 512
 * });
 * for (const chunk of result.chunks || []) {
 *   console.log(chunk);
 * }
 *
 * // With metadata extraction
 * const result = await extractTextFromFile('document.pdf', {
 *   metadataSchemas: [{
 *     id: 'doc-meta',
 *     schema: 'Extract: title, author, date'
 *   }]
 * });
 * console.log(result.metadata);  // JSON string
 * ```
 */
export async function extractTextFromFile(
  filePath: string,
  options: ExtractionOptions = {}
): Promise<ExtractionResultData> {
  const {
    apiToken = process.env.VECTORIZE_TOKEN,
    orgId = process.env.VECTORIZE_ORG_ID,
    pollInterval = 2000,
    timeout = 300000,
    type = 'iris',
    ...extractionOptions
  } = options;

  // Validate credentials
  if (!apiToken || !orgId) {
    throw new VectorizeIrisError(
      'Missing credentials. Set VECTORIZE_TOKEN and VECTORIZE_ORG_ID ' +
      'environment variables or pass them in options.'
    );
  }

  // Validate file exists
  try {
    await fs.access(filePath);
  } catch (err) {
    throw new Error(`File not found: ${filePath}`);
  }

  // Read file
  const fileName = path.basename(filePath);
  const fileBuffer = await fs.readFile(filePath);

  return _extractFromBuffer(
    fileBuffer,
    fileName,
    apiToken,
    orgId,
    pollInterval,
    timeout,
    { type, ...extractionOptions }
  );
}
