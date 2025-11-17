/**
 * Unit tests for vectorize-iris module
 */

import * as fs from 'fs/promises';
import fetch, { Response } from 'node-fetch';
import { extractText, VectorizeIrisError } from '../src/index';

// Mock node-fetch
jest.mock('node-fetch');
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock fs
jest.mock('fs/promises');
const mockFs = fs as jest.Mocked<typeof fs>;

describe('extractText', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset environment variables
    delete process.env.VECTORIZE_API_TOKEN;
    delete process.env.VECTORIZE_ORG_ID;
  });

  it('should throw error when credentials are missing', async () => {
    await expect(extractText('test.pdf')).rejects.toThrow(VectorizeIrisError);
    await expect(extractText('test.pdf')).rejects.toThrow('Missing credentials');
  });

  it('should throw error when file does not exist', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    mockFs.access.mockRejectedValueOnce(new Error('File not found'));

    await expect(extractText('/nonexistent/file.pdf')).rejects.toThrow('File not found');
  });

  it('should successfully extract text from a file', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    // Mock file operations
    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);
    mockFs.readFile.mockResolvedValueOnce(Buffer.from('test file content'));

    // Mock upload start
    const uploadResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        fileId: 'file-123',
        uploadUrl: 'https://upload.example.com'
      })
    } as unknown as Response;

    // Mock file upload
    const putResponse = {
      ok: true,
      status: 200
    } as unknown as Response;

    // Mock extraction start
    const extractionResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        extractionId: 'extraction-123'
      })
    } as unknown as Response;

    // Mock status checks - processing then completed
    const statusResponse1 = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        status: 'processing'
      })
    } as unknown as Response;

    const statusResponse2 = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        status: 'completed',
        result: { text: 'Extracted text content' }
      })
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse)
      .mockResolvedValueOnce(putResponse)
      .mockResolvedValueOnce(extractionResponse)
      .mockResolvedValueOnce(statusResponse1)
      .mockResolvedValueOnce(statusResponse2);

    const result = await extractText('test.pdf', { pollInterval: 100 });

    expect(result).toBe('Extracted text content');
    expect(mockFetch).toHaveBeenCalledTimes(5);
  });

  it('should handle upload failure', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);

    const uploadResponse = {
      ok: false,
      status: 400,
      text: jest.fn().mockResolvedValueOnce('Bad request')
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse);

    await expect(extractText('test.pdf')).rejects.toThrow(VectorizeIrisError);
    await expect(extractText('test.pdf')).rejects.toThrow('Failed to start upload');
  });

  it('should handle file upload failure', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);
    mockFs.readFile.mockResolvedValueOnce(Buffer.from('test file content'));

    const uploadResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        fileId: 'file-123',
        uploadUrl: 'https://upload.example.com'
      })
    } as unknown as Response;

    const putResponse = {
      ok: false,
      status: 403,
      text: jest.fn().mockResolvedValueOnce('Forbidden')
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse)
      .mockResolvedValueOnce(putResponse);

    await expect(extractText('test.pdf')).rejects.toThrow(VectorizeIrisError);
    await expect(extractText('test.pdf')).rejects.toThrow('Failed to upload file');
  });

  it('should handle extraction failure', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);
    mockFs.readFile.mockResolvedValueOnce(Buffer.from('test file content'));

    const uploadResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        fileId: 'file-123',
        uploadUrl: 'https://upload.example.com'
      })
    } as unknown as Response;

    const putResponse = {
      ok: true,
      status: 200
    } as unknown as Response;

    const extractionResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        extractionId: 'extraction-123'
      })
    } as unknown as Response;

    const statusResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        status: 'failed',
        error: 'Invalid file format'
      })
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse)
      .mockResolvedValueOnce(putResponse)
      .mockResolvedValueOnce(extractionResponse)
      .mockResolvedValueOnce(statusResponse);

    await expect(extractText('test.pdf', { pollInterval: 100 })).rejects.toThrow(VectorizeIrisError);
    await expect(extractText('test.pdf', { pollInterval: 100 })).rejects.toThrow('Invalid file format');
  });

  it('should handle extraction timeout', async () => {
    process.env.VECTORIZE_API_TOKEN = 'test-token';
    process.env.VECTORIZE_ORG_ID = 'test-org';

    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);
    mockFs.readFile.mockResolvedValueOnce(Buffer.from('test file content'));

    const uploadResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        fileId: 'file-123',
        uploadUrl: 'https://upload.example.com'
      })
    } as unknown as Response;

    const putResponse = {
      ok: true,
      status: 200
    } as unknown as Response;

    const extractionResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        extractionId: 'extraction-123'
      })
    } as unknown as Response;

    const statusResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValue({
        status: 'processing'
      })
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse)
      .mockResolvedValueOnce(putResponse)
      .mockResolvedValueOnce(extractionResponse)
      .mockResolvedValue(statusResponse);

    await expect(
      extractText('test.pdf', { pollInterval: 100, timeout: 500 })
    ).rejects.toThrow(VectorizeIrisError);
    await expect(
      extractText('test.pdf', { pollInterval: 100, timeout: 500 })
    ).rejects.toThrow('timed out');
  }, 10000);

  it('should use custom credentials when provided', async () => {
    mockFs.access.mockResolvedValueOnce(undefined);
    mockFs.stat.mockResolvedValueOnce({ size: 100 } as any);
    mockFs.readFile.mockResolvedValueOnce(Buffer.from('test file content'));

    const uploadResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        fileId: 'file-123',
        uploadUrl: 'https://upload.example.com'
      })
    } as unknown as Response;

    const putResponse = {
      ok: true,
      status: 200
    } as unknown as Response;

    const extractionResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        extractionId: 'extraction-123'
      })
    } as unknown as Response;

    const statusResponse = {
      ok: true,
      status: 200,
      json: jest.fn().mockResolvedValueOnce({
        status: 'completed',
        result: { text: 'Success' }
      })
    } as unknown as Response;

    mockFetch.mockResolvedValueOnce(uploadResponse)
      .mockResolvedValueOnce(putResponse)
      .mockResolvedValueOnce(extractionResponse)
      .mockResolvedValueOnce(statusResponse);

    const result = await extractText('test.pdf', {
      apiToken: 'custom-token',
      orgId: 'custom-org',
      pollInterval: 100
    });

    expect(result).toBe('Success');

    // Verify custom credentials were used
    const firstCall = mockFetch.mock.calls[0];
    const headers = firstCall[1]?.headers as Record<string, string>;
    expect(headers['Authorization']).toBe('Bearer custom-token');
  });
});
