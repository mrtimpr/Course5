import pytest

pytestmark = pytest.mark.django_db


def test_openapi_schema_and_swagger_are_available(api_client):
    schema = api_client.get("/api/schema/")
    swagger = api_client.get("/api/docs/")

    assert schema.status_code == 200
    assert swagger.status_code == 200
