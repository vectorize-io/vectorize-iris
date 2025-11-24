"""
Unit tests for vectorize_iris models
"""

import json
import pytest
from vectorize_iris.models import (
    MetadataExtractionStrategySchema,
    ExtractionOptions,
)


class TestMetadataExtractionStrategySchema:
    """Test MetadataExtractionStrategySchema model"""

    def test_schema_as_string(self):
        """Test that schema can be passed as a JSON string"""
        schema_str = '{"invoice_number": "string", "total": "number"}'
        schema = MetadataExtractionStrategySchema(id="test", schema=schema_str)
        assert schema.schema_ == schema_str

    def test_schema_as_dict(self):
        """Test that schema can be passed as a dict and is converted to JSON string"""
        schema_dict = {"invoice_number": "string", "total": "number"}
        schema = MetadataExtractionStrategySchema(id="test", schema=schema_dict)
        assert schema.schema_ == json.dumps(schema_dict)

    def test_schema_as_nested_dict(self):
        """Test that nested dict schemas are properly converted"""
        schema_dict = {
            "invoice_number": "string",
            "date": "string",
            "total_amount": "number",
            "vendor_name": "string",
            "items": [{
                "description": "string",
                "quantity": "number",
                "price": "number"
            }]
        }
        schema = MetadataExtractionStrategySchema(id="invoice-data", schema=schema_dict)
        assert schema.schema_ == json.dumps(schema_dict)
        # Verify it's valid JSON
        parsed = json.loads(schema.schema_)
        assert parsed == schema_dict


class TestExtractionOptions:
    """Test ExtractionOptions model"""

    def test_metadata_schemas_as_dicts(self):
        """Test that metadata_schemas can be passed as a list of dicts"""
        options = ExtractionOptions(
            metadata_schemas=[{
                'id': 'invoice-data',
                'schema': {
                    'invoice_number': 'string',
                    'date': 'string',
                    'total_amount': 'number',
                }
            }]
        )
        assert len(options.metadata_schemas) == 1
        assert options.metadata_schemas[0].id == 'invoice-data'
        # Schema should be converted to JSON string
        parsed = json.loads(options.metadata_schemas[0].schema_)
        assert parsed == {
            'invoice_number': 'string',
            'date': 'string',
            'total_amount': 'number',
        }

    def test_metadata_schemas_as_model_objects(self):
        """Test that metadata_schemas can be passed as MetadataExtractionStrategySchema objects"""
        schema_obj = MetadataExtractionStrategySchema(
            id='test-schema',
            schema='{"field": "string"}'
        )
        options = ExtractionOptions(metadata_schemas=[schema_obj])
        assert len(options.metadata_schemas) == 1
        assert options.metadata_schemas[0].id == 'test-schema'
        assert options.metadata_schemas[0].schema_ == '{"field": "string"}'

    def test_metadata_schemas_mixed(self):
        """Test that metadata_schemas can mix dicts and model objects"""
        schema_obj = MetadataExtractionStrategySchema(
            id='obj-schema',
            schema='{"obj_field": "string"}'
        )
        options = ExtractionOptions(
            metadata_schemas=[
                schema_obj,
                {
                    'id': 'dict-schema',
                    'schema': {'dict_field': 'number'}
                }
            ]
        )
        assert len(options.metadata_schemas) == 2
        assert options.metadata_schemas[0].id == 'obj-schema'
        assert options.metadata_schemas[1].id == 'dict-schema'

    def test_to_extraction_request(self):
        """Test conversion to StartExtractionRequest"""
        options = ExtractionOptions(
            metadata_schemas=[{
                'id': 'test',
                'schema': {'field': 'string'}
            }],
            chunk_size=512,
            infer_metadata_schema=False
        )
        request = options.to_extraction_request('file-123')
        assert request.file_id == 'file-123'
        assert request.chunk_size == 512
        assert request.metadata is not None
        assert request.metadata.infer_schema is False
        assert len(request.metadata.schemas) == 1
        assert request.metadata.schemas[0].id == 'test'
