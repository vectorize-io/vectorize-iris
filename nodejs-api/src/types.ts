/**
 * Type definitions for Vectorize Iris API
 */

// Request Types

export interface StartFileUploadRequest {
  name: string;
  contentType: string;
}

export interface MetadataExtractionStrategySchema {
  id: string;
  schema: string;
}

export interface MetadataExtractionStrategy {
  schemas?: MetadataExtractionStrategySchema[];
  inferSchema?: boolean;
}

export type ExtractionType = 'iris';

export interface StartExtractionRequest {
  fileId: string;
  type?: ExtractionType;
  chunkSize?: number;
  metadata?: MetadataExtractionStrategy;
  parsingInstructions?: string;
}

// Response Types

export interface StartFileUploadResponse {
  fileId: string;
  uploadUrl: string;
}

export interface StartExtractionResponse {
  message: string;
  extractionId: string;
}

export interface ExtractionResultData {
  success: boolean;
  chunks?: string[];
  text?: string;
  metadata?: string;  // JSON string
  metadataSchema?: string;
  chunksMetadata?: (string | null)[];  // JSON strings, may contain nulls
  chunksSchema?: (string | null)[];  // May contain nulls
  error?: string;
}

export interface ExtractionResult {
  ready: boolean;
  data?: ExtractionResultData;
}

// Options for extract functions

export interface ExtractionOptions {
  /** Vectorize API token (defaults to VECTORIZE_API_TOKEN env var) */
  apiToken?: string;
  /** Organization ID (defaults to VECTORIZE_ORG_ID env var) */
  orgId?: string;
  /** Milliseconds between status checks (default: 2000) */
  pollInterval?: number;
  /** Maximum milliseconds to wait for extraction (default: 300000) */
  timeout?: number;
  /** Extraction type (default: 'iris') */
  type?: ExtractionType;
  /** Chunk size (default: 256) */
  chunkSize?: number;
  /** Metadata extraction schemas */
  metadataSchemas?: MetadataExtractionStrategySchema[];
  /** Whether to infer metadata schema automatically (default: true) */
  inferMetadataSchema?: boolean;
  /** Optional parsing instructions for the AI model */
  parsingInstructions?: string;
}
