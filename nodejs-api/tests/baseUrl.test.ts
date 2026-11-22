/**
 * Where requests go: api.vectorize.io/v1/org/{orgId} by default, or a base URL as given (Hindsight
 * Inference, where the organization comes from the key and isn't in the path).
 */

import fetch from 'node-fetch';
import { extractText, resolveEndpoint, VectorizeIrisError } from '../src/index';

jest.mock('node-fetch');
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

const HINDSIGHT = 'https://inference.hindsight.vectorize.io/v1';
const UPLOAD_URL = 'https://storage.example.com/signed';
const DONE = {
  ready: true,
  data: { success: true, text: 'hello', chunks: ['hello'], metadata: null, usage: { irisPages: 1 }, error: null },
};

function reply(body: unknown, status = 200) {
  return { ok: status < 400, status, json: async () => body, text: async () => JSON.stringify(body) } as never;
}

function fakeApi(): Array<{ method: string; url: string; auth?: string }> {
  const calls: Array<{ method: string; url: string; auth?: string }> = [];
  mockFetch.mockImplementation((async (url: string, init?: { method?: string; headers?: Record<string, string> }) => {
    const method = init?.method ?? 'GET';
    calls.push({ method, url, auth: init?.headers?.Authorization });
    if (method === 'PUT') return reply({});
    if (url.endsWith('/files')) return reply({ fileId: 'f1', uploadUrl: UPLOAD_URL });
    if (url.endsWith('/extraction')) return reply({ message: 'Extraction started.', extractionId: 'e1' });
    return reply(DONE);
  }) as never);
  return calls;
}

beforeEach(() => {
  jest.clearAllMocks();
  delete process.env.VECTORIZE_TOKEN;
  delete process.env.VECTORIZE_ORG_ID;
  delete process.env.VECTORIZE_IRIS_BASE_URL;
});

describe('resolveEndpoint', () => {
  it('defaults to api.vectorize.io with the org', () => {
    expect(resolveEndpoint('t', 'org-1', undefined)).toEqual({
      apiToken: 't',
      baseUrl: 'https://api.vectorize.io/v1/org/org-1',
    });
  });

  it('uses a base URL as given, with no org', () => {
    expect(resolveEndpoint('hsk_x', undefined, `${HINDSIGHT}/`)).toEqual({ apiToken: 'hsk_x', baseUrl: HINDSIGHT });
  });

  it('still needs the org without a base URL', () => {
    expect(() => resolveEndpoint('t', undefined, undefined)).toThrow(/VECTORIZE_ORG_ID/);
  });

  it('always needs a token', () => {
    expect(() => resolveEndpoint(undefined, undefined, HINDSIGHT)).toThrow(VectorizeIrisError);
  });
});

describe('extractText', () => {
  it('sends every call to the Hindsight base URL, without an org', async () => {
    const calls = fakeApi();
    const result = await extractText(Buffer.from('%PDF'), 'a.pdf', {
      apiToken: 'hsk_x',
      baseUrl: HINDSIGHT,
      pollInterval: 0,
    });
    expect(result.text).toBe('hello');
    expect(calls.filter((c) => c.method !== 'PUT').map((c) => [c.method, c.url])).toEqual([
      ['POST', `${HINDSIGHT}/files`],
      ['POST', `${HINDSIGHT}/extraction`],
      ['GET', `${HINDSIGHT}/extraction/e1`],
    ]);
    expect(calls.filter((c) => c.method !== 'PUT').every((c) => c.auth === 'Bearer hsk_x')).toBe(true);
  });

  it('reads the base URL and key from the environment', async () => {
    process.env.VECTORIZE_TOKEN = 'hsk_x';
    process.env.VECTORIZE_IRIS_BASE_URL = HINDSIGHT;
    const calls = fakeApi();
    await extractText(Buffer.from('%PDF'), 'a.pdf', { pollInterval: 0 });
    expect(calls[0].url).toBe(`${HINDSIGHT}/files`);
  });

  it('is unchanged by default', async () => {
    const calls = fakeApi();
    await extractText(Buffer.from('%PDF'), 'a.pdf', { apiToken: 't', orgId: 'org-1', pollInterval: 0 });
    expect(calls[0].url).toBe('https://api.vectorize.io/v1/org/org-1/files');
  });
});
