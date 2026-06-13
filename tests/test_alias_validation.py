import pytest
from pydantic import ValidationError

from app.schemas.url import CreateShortURLRequest


def test_custom_alias_validation_allows_safe_alias() -> None:
    payload = CreateShortURLRequest(long_url="https://example.com", custom_alias="my-link_123")
    assert payload.custom_alias == "my-link_123"


def test_custom_alias_validation_rejects_reserved_alias() -> None:
    with pytest.raises(ValidationError):
        CreateShortURLRequest(long_url="https://example.com", custom_alias="api")
