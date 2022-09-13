# from rest_framework.test import APIRequestFactory
# from rest_framework.test import RequestsClient
import pytest
import json

from django.urls import reverse


@pytest.mark.skip
@pytest.mark.django_db
def test_registration(api_client):
    url = reverse('register')
    data = {
        "email": "test_user@example.com",
        "password": "example_pwd_1!",
        "password2": "example_pwd_1!"
    }
    response = api_client.post(url, data, format='json')
    response_json = json.loads(response.content)
    assert response.status_code == 201
    assert response_json['res'] == 'Registered successfully'
    assert response_json['user info'] == {'email': data['email']}


