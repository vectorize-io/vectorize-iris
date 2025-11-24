/**
 * Unit tests for type handling and schema conversion
 */

import type { MetadataExtractionStrategySchema, ExtractionOptions } from '../src/types';

describe('MetadataExtractionStrategySchema', () => {
  it('should accept schema as a string', () => {
    const schema: MetadataExtractionStrategySchema = {
      id: 'test',
      schema: '{"invoice_number": "string", "total": "number"}'
    };
    expect(schema.id).toBe('test');
    expect(schema.schema).toBe('{"invoice_number": "string", "total": "number"}');
  });

  it('should accept schema as an object', () => {
    const schema: MetadataExtractionStrategySchema = {
      id: 'test',
      schema: { invoice_number: 'string', total: 'number' }
    };
    expect(schema.id).toBe('test');
    expect(schema.schema).toEqual({ invoice_number: 'string', total: 'number' });
  });

  it('should accept nested object schemas', () => {
    const schema: MetadataExtractionStrategySchema = {
      id: 'invoice-data',
      schema: {
        invoice_number: 'string',
        date: 'string',
        total_amount: 'number',
        vendor_name: 'string',
        items: [{
          description: 'string',
          quantity: 'number',
          price: 'number'
        }]
      }
    };
    expect(schema.id).toBe('invoice-data');
    expect(typeof schema.schema).toBe('object');
  });
});

describe('ExtractionOptions with metadataSchemas', () => {
  it('should accept metadataSchemas with string schema', () => {
    const options: ExtractionOptions = {
      metadataSchemas: [{
        id: 'doc-info',
        schema: 'Extract title, author, and main topics'
      }]
    };
    expect(options.metadataSchemas).toHaveLength(1);
    expect(options.metadataSchemas![0].schema).toBe('Extract title, author, and main topics');
  });

  it('should accept metadataSchemas with object schema', () => {
    const options: ExtractionOptions = {
      metadataSchemas: [{
        id: 'invoice-data',
        schema: {
          invoice_number: 'string',
          date: 'string',
          total_amount: 'number',
          vendor_name: 'string',
          items: [{
            description: 'string',
            quantity: 'number',
            price: 'number'
          }]
        }
      }]
    };
    expect(options.metadataSchemas).toHaveLength(1);
    expect(options.metadataSchemas![0].id).toBe('invoice-data');
    expect(typeof options.metadataSchemas![0].schema).toBe('object');
  });

  it('should accept mixed string and object schemas', () => {
    const options: ExtractionOptions = {
      metadataSchemas: [
        {
          id: 'string-schema',
          schema: 'Extract basic info'
        },
        {
          id: 'object-schema',
          schema: { field: 'string' }
        }
      ]
    };
    expect(options.metadataSchemas).toHaveLength(2);
    expect(typeof options.metadataSchemas![0].schema).toBe('string');
    expect(typeof options.metadataSchemas![1].schema).toBe('object');
  });
});

describe('Schema conversion to JSON string', () => {
  it('should convert object schema to JSON string for API request', () => {
    const schemas: MetadataExtractionStrategySchema[] = [
      {
        id: 'test',
        schema: { invoice_number: 'string', total: 'number' }
      }
    ];

    // Simulate the conversion that happens in index.ts
    const normalizedSchemas = schemas.map(s => ({
      id: s.id,
      schema: typeof s.schema === 'string' ? s.schema : JSON.stringify(s.schema)
    }));

    expect(normalizedSchemas[0].schema).toBe('{"invoice_number":"string","total":"number"}');
  });

  it('should keep string schema as is', () => {
    const schemas: MetadataExtractionStrategySchema[] = [
      {
        id: 'test',
        schema: '{"invoice_number": "string"}'
      }
    ];

    // Simulate the conversion that happens in index.ts
    const normalizedSchemas = schemas.map(s => ({
      id: s.id,
      schema: typeof s.schema === 'string' ? s.schema : JSON.stringify(s.schema)
    }));

    expect(normalizedSchemas[0].schema).toBe('{"invoice_number": "string"}');
  });

  it('should handle nested object schemas', () => {
    const schemas: MetadataExtractionStrategySchema[] = [
      {
        id: 'invoice-data',
        schema: {
          invoice_number: 'string',
          items: [{
            description: 'string',
            quantity: 'number'
          }]
        }
      }
    ];

    // Simulate the conversion that happens in index.ts
    const normalizedSchemas = schemas.map(s => ({
      id: s.id,
      schema: typeof s.schema === 'string' ? s.schema : JSON.stringify(s.schema)
    }));

    const parsed = JSON.parse(normalizedSchemas[0].schema);
    expect(parsed.invoice_number).toBe('string');
    expect(parsed.items).toHaveLength(1);
    expect(parsed.items[0].description).toBe('string');
  });
});
