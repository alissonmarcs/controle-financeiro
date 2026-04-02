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

def test_get_user_should_return_user(client, db_user):
    response = client.get(
        '/users/1'
    )

    db_user_pydantic_model = schemas.CreatedUser.model_validate(db_user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert  response.json() == db_user_pydantic_model

def test_get_user_invalid_id_should_return_not_found(client):
    response = client.get(
        '/users/999'
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert  response.json() == {
            'detail': 'User not found'
    }

def test_get_users_empty_db_should_return_empty_list(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}

def test_get_users_populated_db_should_return_populated_list(client, db_user):
    response = client.get('/users/')

    db_user_pydantic_model = schemas.CreatedUser.model_validate(db_user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [db_user_pydantic_model]}