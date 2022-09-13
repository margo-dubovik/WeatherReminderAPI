import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():

    return APIClient()


@pytest.fixture
def authenticated_api_client(db, api_client, ):
    pass
