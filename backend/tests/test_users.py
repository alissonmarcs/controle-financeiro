from http import HTTPStatus

from backend import models, schemas


def test_create_user_should_return_created_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'Jhon',
            'email': 'jhon@gmail.com',
            'password': '654321',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'Jhon',
        'email': 'jhon@gmail.com',
    }


def test_create_user_email_not_unique_should_return_conflict(client, db_user):
    response = client.post(
        '/users/',
        json={
            'username': 'jhon',
            'email': db_user.email,
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_get_user_should_return_user(client, db_user):
    response = client.get('/users/1')

    db_user_pydantic_model = schemas.CreatedUser.model_validate(
        db_user
    ).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == db_user_pydantic_model


def test_get_user_invalid_id_should_return_not_found(client):
    response = client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_get_users_empty_db_should_return_empty_list(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_users_populated_db_should_return_populated_list(client, db_user):
    response = client.get('/users/')

    db_user_pydantic_model = schemas.CreatedUser.model_validate(
        db_user
    ).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [db_user_pydantic_model]}


def test_get_users_negative_limit(client):
    response = client.get('/users?offset=-1')

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_update_user_should_return_updated_user(client, db_user, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'batman',
            'email': 'batman@gmail.com',
            'password': '70707070',
        },
    )

    updated_user = schemas.CreatedUser.model_validate(db_user).model_dump()
    assert response.status_code == HTTPStatus.OK
    assert response.json() == updated_user


def test_update_user_should_return_forbidden(client, token):
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'batman',
            'email': 'batman@gmail.com',
            'password': '70707070',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_should_return_conflict(client, db_user, token):
    user2 = {
        'username': 'Jhon',
        'email': 'jhon@gmail.com',
        'password': '654321',
    }
    client.post('/users/', json=user2)

    response = client.put(
        f'/users/1',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user2['username'],
            'email': 'batman@gmail.com',
            'password': '70707070',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_delete_user_should_return_ok(client, db_user, token):
    response = client.delete(
        f'/users/{db_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_should_return_not_found(client, token):
    response = client.delete(
        '/users/9999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_access_token(client, db_user):
    response = client.post(
        '/token',
        data={'username': db_user.email, 'password': db_user.plain_password},
    )

    response_json = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response_json
    assert 'token_type' in response_json
    assert response_json['token_type'] == 'bearer'


def test_try_get_token_with_invalid_email_should_return_unauthorized(client):
    response = client.post(
        '/token',
        data={
            'username': 'jj@gmail.com',
            'password': 'jj',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_invalid_password(client, db_user):
    response = client.post(
        '/token', data={'username': db_user.email, 'password': 'demo'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh_token_should_return_new_token(client, token):
    response = client.get(
        '/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'
