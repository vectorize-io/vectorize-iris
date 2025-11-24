"""
Pydantic models for Vectorize Iris API
"""

from typing import Optional, List, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import json


# Request Models

class StartFileUploadRequest(BaseModel):
    """Request to start file upload"""
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., description="File name")
    content_type: str = Field(..., alias="contentType", description="Content type of the file")


class MetadataExtractionStrategySchema(BaseModel):
    """Schema for metadata extraction"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Schema identifier")
    schema_: str = Field(..., alias="schema", description="Schema definition for metadata extraction (JSON string or dict)")

    @field_validator('schema_', mode='before')
    @classmethod
    def convert_schema_to_string(cls, v: Union[str, Dict[str, Any]]) -> str:
        """Convert dict schema to JSON string if needed"""
        if isinstance(v, dict):
            return json.dumps(v)
        return v


class MetadataExtractionStrategy(BaseModel):
    """Strategy for extracting metadata"""
    model_config = ConfigDict(populate_by_name=True)

    schemas: Optional[List[MetadataExtractionStrategySchema]] = Field(default=None, description="List of metadata schemas")
    infer_schema: Optional[bool] = Field(default=None, alias="inferSchema", description="Whether to infer metadata schema automatically")


class StartExtractionRequest(BaseModel):
    """Request to start content extraction"""
    model_config = ConfigDict(populate_by_name=True)

    file_id: str = Field(..., alias="fileId", description="ID of the uploaded file")
    type: Optional[Literal["iris"]] = Field(default="iris", description="Extraction type")
    chunk_size: Optional[int] = Field(default=256, alias="chunkSize", description="Size of each chunk (default: 256)")
    metadata: Optional[MetadataExtractionStrategy] = Field(default=None, description="Metadata extraction configuration")
    parsing_instructions: Optional[str] = Field(
        default=None,
        alias="parsingInstructions",
        description="Optional instructions for the AI model on how to parse the document"
    )


# Response Models

class StartFileUploadResponse(BaseModel):
    """Response from starting file upload"""
    model_config = ConfigDict(populate_by_name=True, extra='allow')

    file_id: str = Field(..., alias="fileId", description="Unique identifier for the uploaded file")
    upload_url: str = Field(..., alias="uploadUrl", description="Presigned URL for uploading the file")


class StartExtractionResponse(BaseModel):
    """Response from starting extraction"""
    model_config = ConfigDict(populate_by_name=True, extra='allow')

    message: str = Field(..., description="Status message")
    extraction_id: str = Field(..., alias="extractionId", description="Unique identifier for the extraction job")


class UsageInfo(BaseModel):
    """Usage information for the extraction"""
    model_config = ConfigDict(populate_by_name=True)

    iris_pages: int = Field(..., alias="irisPages", description="Number of pages processed by Iris")


class ExtractionResultData(BaseModel):
    """Data contained in extraction result"""
    model_config = ConfigDict(populate_by_name=True, extra='allow')

    success: bool = Field(..., description="Whether the extraction was successful")
    chunks: Optional[List[str]] = Field(default=None, description="Extracted chunks of text")
    text: Optional[str] = Field(default=None, description="Full extracted text")
    metadata: Optional[str] = Field(default=None, description="Document metadata as JSON string")
    metadata_schema: Optional[str] = Field(default=None, alias="metadataSchema", description="Schema ID used for metadata")
    chunks_metadata: Optional[List[Optional[str]]] = Field(
        default=None,
        alias="chunksMetadata",
        description="Metadata for each chunk as JSON strings"
    )
    chunks_schema: Optional[List[Optional[str]]] = Field(
        default=None,
        alias="chunksSchema",
        description="Schema IDs used for each chunk's metadata"
    )
    usage: Optional[UsageInfo] = Field(default=None, description="Usage information")
    error: Optional[str] = Field(default=None, description="Error message if extraction failed")


class ExtractionResult(BaseModel):
    """Result of an extraction job"""
    model_config = ConfigDict(populate_by_name=True, extra='allow')

    ready: bool = Field(..., description="Whether the extraction is complete")
    data: Optional[ExtractionResultData] = Field(default=None, description="Extraction data (when ready=True)")


# Options for extract functions

class ExtractionOptions(BaseModel):
    """Options for text extraction"""
    type: Optional[Literal["iris"]] = Field(default="iris", description="Extraction type")
    chunk_size: Optional[int] = Field(default=None, description="Size of each chunk (default: 256)")
    metadata_schemas: Optional[List[Union[MetadataExtractionStrategySchema, Dict[str, Any]]]] = Field(
        default=None,
        description="Metadata extraction schemas (can be MetadataExtractionStrategySchema objects or dicts with 'id' and 'schema' keys)"
    )

    @field_validator('metadata_schemas', mode='before')
    @classmethod
    def convert_metadata_schemas(cls, v: Optional[List[Any]]) -> Optional[List[MetadataExtractionStrategySchema]]:
        """Convert dict schemas to MetadataExtractionStrategySchema objects"""
        if v is None:
            return None
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(MetadataExtractionStrategySchema(**item))
            else:
                result.append(item)
        return result
    infer_metadata_schema: Optional[bool] = Field(
        default=True,
        description="Whether to automatically infer metadata schema (default: True)"
    )
    parsing_instructions: Optional[str] = Field(
        default=None,
        description="Optional instructions for parsing the document"
    )

    def to_extraction_request(self, file_id: str) -> StartExtractionRequest:
        """Convert options to StartExtractionRequest"""
        metadata = None
        if self.metadata_schemas is not None or self.infer_metadata_schema is not None:
            metadata = MetadataExtractionStrategy(
                schemas=self.metadata_schemas,
                infer_schema=self.infer_metadata_schema
            )

        return StartExtractionRequest(
            file_id=file_id,
            type=self.type,
            chunk_size=self.chunk_size,
            metadata=metadata,
            parsing_instructions=self.parsing_instructions
        )
