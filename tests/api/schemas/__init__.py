from pydantic import ValidationError
import pytest


def validate_schema(response_data: dict, schema_class):
    """
    Validate response data against a Pydantic schema.
    
    Args:
        response_data: The JSON response data
        schema_class: The Pydantic model class to validate against
        
    Returns:
        The validated Pydantic model instance
        
    Raises:
        pytest.fail if validation fails
    """
    try:
        return schema_class(**response_data)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed for {schema_class.__name__}: {e}")
