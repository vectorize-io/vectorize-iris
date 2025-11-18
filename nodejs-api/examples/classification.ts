/**
 * Document Classification Example
 *
 * This example demonstrates how to use multiple metadata schemas to automatically
 * classify documents and extract relevant fields.
 *
 * When you provide multiple metadata schemas, Iris will:
 * 1. Analyze the document
 * 2. Determine which schema best matches the document type
 * 3. Extract fields according to the matching schema
 * 4. Return the schema ID in the response
 */

import { extractTextFromFile, ExtractionOptions } from '@vectorize-io/iris';
import * as fs from 'fs/promises';
import * as path from 'path';

// Example 1: Single document classification
console.log('='.repeat(70));
console.log('Example 1: Classifying a single document');
console.log('='.repeat(70));
console.log();

(async () => {
    // Define multiple schemas for different document types (JSON objects)
    const result = await extractTextFromFile('document.pdf', {
        metadataSchemas: [
            {
                id: 'invoice',
                schema: {
                    invoice_number: 'string',
                    date: 'string',
                    total_amount: 'number',
                    vendor_name: 'string'
                }
            },
            {
                id: 'receipt',
                schema: {
                    store_name: 'string',
                    date: 'string',
                    items: 'array',
                    total: 'number'
                }
            },
            {
                id: 'contract',
                schema: {
                    parties: 'array',
                    effective_date: 'string',
                    terms: 'string'
                }
            }
        ]
    });

    // Check which schema matched
    console.log(`Document classified as: ${result.metadataSchema}`);
    console.log(`Extracted metadata: ${result.metadata}`);
    console.log();

    // Example 2: Processing multiple documents with classification
    console.log('='.repeat(70));
    console.log('Example 2: Batch classification of multiple documents');
    console.log('='.repeat(70));
    console.log();

    const documentsDir = './documents';
    try {
        const files = await fs.readdir(documentsDir);

        for (const file of files) {
            const filePath = path.join(documentsDir, file);
            const stat = await fs.stat(filePath);

            if (stat.isFile()) {
                const result = await extractTextFromFile(filePath, {
                    metadataSchemas: [
                        {
                            id: 'invoice',
                            schema: {
                                invoice_number: 'string',
                                date: 'string',
                                total_amount: 'number',
                                vendor_name: 'string'
                            }
                        },
                        {
                            id: 'receipt',
                            schema: {
                                store_name: 'string',
                                date: 'string',
                                items: 'array',
                                total: 'number'
                            }
                        },
                        {
                            id: 'contract',
                            schema: {
                                parties: 'array',
                                effective_date: 'string',
                                terms: 'string'
                            }
                        }
                    ]
                });

                console.log(`File: ${file}`);
                console.log(`  Type: ${result.metadataSchema}`);
                console.log(`  Metadata: ${result.metadata}`);
                console.log();
            }
        }
    } catch (error) {
        console.log('Documents directory not found, skipping batch example');
    }

    // Example 3: Conditional processing based on classification
    console.log('='.repeat(70));
    console.log('Example 3: Conditional processing based on document type');
    console.log('='.repeat(70));
    console.log();

    const classifiedResult = await extractTextFromFile('document.pdf', {
        metadataSchemas: [
            {
                id: 'invoice',
                schema: {
                    invoice_number: 'string',
                    date: 'string',
                    total_amount: 'number',
                    vendor_name: 'string'
                }
            },
            {
                id: 'receipt',
                schema: {
                    store_name: 'string',
                    date: 'string',
                    items: 'array',
                    total: 'number'
                }
            }
        ]
    });

    // Process differently based on document type
    switch (classifiedResult.metadataSchema) {
        case 'invoice':
            console.log('Processing as invoice...');
            // Invoice-specific logic here
            console.log(`Invoice data: ${classifiedResult.metadata}`);
            break;
        case 'receipt':
            console.log('Processing as receipt...');
            // Receipt-specific logic here
            console.log(`Receipt data: ${classifiedResult.metadata}`);
            break;
        default:
            console.log('Unknown document type');
            console.log(`Extracted text: ${classifiedResult.text.substring(0, 200)}...`);
    }
})();
