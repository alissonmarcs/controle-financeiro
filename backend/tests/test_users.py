from http import HTTPStatus

from backend import models, schemas

def test_create_user_should_return_created_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Jhon',
            'email': 'jhon@gmail.com',
            'password': '654321',
        }
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
            'id': 1,
            'username': 'Jhon',
            'email': 'jhon@gmail.com',
    }

def test_create_user_email_not_unique_should_return_conflit(client, db_user):
    response = client.post(
        '/users/',
        json={
            'username': 'jhon',
            'email': db_user.email,
            'password': '123456'
        }
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
            'detail': 'Username or email already exists'
    }