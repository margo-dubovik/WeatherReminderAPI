import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        kwargs['password'] = 'strong-test-pass!'
        return django_user_model.objects.create_user(**kwargs)

    return make_user


@pytest.fixture
def api_client_with_authenticated_user(db, api_client, create_user):
    user = create_user(email='test_user@example.com')
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)
