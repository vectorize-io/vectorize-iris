"""
Document Classification Example

This example demonstrates how to use multiple metadata schemas to automatically
classify documents and extract relevant fields.

When you provide multiple metadata schemas, Iris will:
1. Analyze the document
2. Determine which schema best matches the document type
3. Extract fields according to the matching schema
4. Return the schema ID in the response
"""

from vectorize_iris import extract_text_from_file, ExtractionOptions

# Example 1: Single document classification
print("=" * 70)
print("Example 1: Classifying a single document")
print("=" * 70)
print()

# Define multiple schemas for different document types (JSON objects)
result = extract_text_from_file(
    'document.pdf',
    options=ExtractionOptions(
        metadata_schemas=[
            {
                'id': 'invoice',
                'schema': {
                    'invoice_number': 'string',
                    'date': 'string',
                    'total_amount': 'number',
                    'vendor_name': 'string'
                }
            },
            {
                'id': 'receipt',
                'schema': {
                    'store_name': 'string',
                    'date': 'string',
                    'items': 'array',
                    'total': 'number'
                }
            },
            {
                'id': 'contract',
                'schema': {
                    'parties': 'array',
                    'effective_date': 'string',
                    'terms': 'string'
                }
            }
        ]
    )
)

# Check which schema matched
print(f"Document classified as: {result.metadata_schema}")
print(f"Extracted metadata: {result.metadata}")
print()

# Example 2: Processing multiple documents with classification
print("=" * 70)
print("Example 2: Batch classification of multiple documents")
print("=" * 70)
print()

import os
from pathlib import Path

documents_dir = Path('./documents')
if documents_dir.exists():
    for doc_path in documents_dir.glob('*.*'):
        result = extract_text_from_file(
            str(doc_path),
            options=ExtractionOptions(
                metadata_schemas=[
                    {
                        'id': 'invoice',
                        'schema': {
                            'invoice_number': 'string',
                            'date': 'string',
                            'total_amount': 'number',
                            'vendor_name': 'string'
                        }
                    },
                    {
                        'id': 'receipt',
                        'schema': {
                            'store_name': 'string',
                            'date': 'string',
                            'items': 'array',
                            'total': 'number'
                        }
                    },
                    {
                        'id': 'contract',
                        'schema': {
                            'parties': 'array',
                            'effective_date': 'string',
                            'terms': 'string'
                        }
                    }
                ]
            )
        )

        print(f"File: {doc_path.name}")
        print(f"  Type: {result.metadata_schema}")
        print(f"  Metadata: {result.metadata}")
        print()

# Example 3: Conditional processing based on classification
print("=" * 70)
print("Example 3: Conditional processing based on document type")
print("=" * 70)
print()

result = extract_text_from_file(
    'document.pdf',
    options=ExtractionOptions(
        metadata_schemas=[
            {
                'id': 'invoice',
                'schema': {
                    'invoice_number': 'string',
                    'date': 'string',
                    'total_amount': 'number',
                    'vendor_name': 'string'
                }
            },
            {
                'id': 'receipt',
                'schema': {
                    'store_name': 'string',
                    'date': 'string',
                    'items': 'array',
                    'total': 'number'
                }
            }
        ]
    )
)

# Process differently based on document type
if result.metadata_schema == 'invoice':
    print("Processing as invoice...")
    # Invoice-specific logic here
    print(f"Invoice data: {result.metadata}")
elif result.metadata_schema == 'receipt':
    print("Processing as receipt...")
    # Receipt-specific logic here
    print(f"Receipt data: {result.metadata}")
else:
    print("Unknown document type")
    print(f"Extracted text: {result.text[:200]}...")
