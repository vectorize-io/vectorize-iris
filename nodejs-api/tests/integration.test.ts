/**
 * Integration tests for Vectorize Iris Node.js API
 * These tests require real API credentials and network access
 */

import * as fs from 'fs';
import * as path from 'path';
import { extractText, extractTextFromFile, VectorizeIrisError } from '../src/index';
import type { ExtractionOptions } from '../src/index';

// Skip tests if credentials not available
const hasCredentials = process.env.VECTORIZE_API_TOKEN && process.env.VECTORIZE_ORG_ID;
const describeIfCredentials = hasCredentials ? describe : describe.skip;

const TEST_FILE = path.join(__dirname, '../../examples/sample.md');

describeIfCredentials('Integration Tests', () => {
  describe('extractTextFromFile', () => {
    it('should extract text from file', async () => {
      const result = await extractTextFromFile(TEST_FILE);

      expect(result.success).toBe(true);
      expect(result.text).toBeDefined();
      expect(result.text!.length).toBeGreaterThan(0);
      console.log(`\n✓ Extracted ${result.text!.length} characters`);
    }, 120000); // 2 minute timeout

    it('should extract with chunking', async () => {
      const options: ExtractionOptions = {
        chunkingStrategy: 'markdown',
        chunkSize: 512
      };

      const result = await extractTextFromFile(TEST_FILE, options);

      expect(result.success).toBe(true);
      expect(result.chunks).toBeDefined();
      expect(result.chunks!.length).toBeGreaterThan(0);
      console.log(`\n✓ Generated ${result.chunks!.length} chunks`);
    }, 120000);

    it('should extract with metadata schema', async () => {
      const options: ExtractionOptions = {
        metadataSchemas: [
          {
            id: 'doc-info',
            schema: 'Extract title, author, and main topics'
          }
        ]
      };

      const result = await extractTextFromFile(TEST_FILE, options);

      expect(result.success).toBe(true);
      // Metadata may or may not be present
      console.log(`\n✓ Metadata: ${result.metadata}`);
    }, 120000);

    it('should extract with inferred metadata', async () => {
      const options: ExtractionOptions = {
        inferMetadataSchema: true
      };

      const result = await extractTextFromFile(TEST_FILE, options);

      expect(result.success).toBe(true);
    }, 120000);

    it('should extract with parsing instructions', async () => {
      const options: ExtractionOptions = {
        parsingInstructions: 'Focus on extracting code examples and technical content'
      };

      const result = await extractTextFromFile(TEST_FILE, options);

      expect(result.success).toBe(true);
      expect(result.text).toBeDefined();
    }, 120000);

    it('should extract with all options', async () => {
      const options: ExtractionOptions = {
        chunkingStrategy: 'markdown',
        chunkSize: 256,
        metadataSchemas: [
          {
            id: 'content-analysis',
            schema: 'Extract document type, language, and key topics'
          }
        ],
        parsingInstructions: 'Pay special attention to code blocks and technical terminology'
      };

      const result = await extractTextFromFile(TEST_FILE, options);

      expect(result.success).toBe(true);
      expect(result.chunks).toBeDefined();
      expect(result.chunks!.length).toBeGreaterThan(0);
    }, 120000);

    it('should fail for non-existent file', async () => {
      await expect(
        extractTextFromFile('/nonexistent/file.pdf')
      ).rejects.toThrow('File not found');
    });
  });

  describe('extractText', () => {
    it('should extract text from buffer', async () => {
      const fileBuffer = fs.readFileSync(TEST_FILE);
      const fileName = path.basename(TEST_FILE);

      const result = await extractText(fileBuffer, fileName);

      expect(result.success).toBe(true);
      expect(result.text).toBeDefined();
      expect(result.text!.length).toBeGreaterThan(0);
    }, 120000);

    it('should extract from buffer with chunking', async () => {
      const fileBuffer = fs.readFileSync(TEST_FILE);
      const fileName = path.basename(TEST_FILE);

      const options: ExtractionOptions = {
        chunkingStrategy: 'markdown',
        chunkSize: 512
      };

      const result = await extractText(fileBuffer, fileName, options);

      expect(result.success).toBe(true);
      expect(result.chunks).toBeDefined();
      expect(result.chunks!.length).toBeGreaterThan(0);
    }, 120000);

    it('should extract from buffer with metadata', async () => {
      const fileBuffer = fs.readFileSync(TEST_FILE);
      const fileName = path.basename(TEST_FILE);

      const options: ExtractionOptions = {
        metadataSchemas: [
          {
            id: 'doc-meta',
            schema: 'Extract key information from the document'
          }
        ]
      };

      const result = await extractText(fileBuffer, fileName, options);

      expect(result.success).toBe(true);
    }, 120000);
  });

  describe('Error Handling', () => {
    it('should fail without credentials', async () => {
      const options: ExtractionOptions = {
        apiToken: '',
        orgId: ''
      };

      await expect(
        extractTextFromFile(TEST_FILE, options)
      ).rejects.toThrow(VectorizeIrisError);
    });
  });
});
