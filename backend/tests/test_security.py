from jwt import decode

from backend.security import create_access_token

from backend.security import settings

from http import HTTPStatus

from freezegun import freeze_time

def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    assert decoded['test'] == data['test']
    assert 'exp' in decoded

def test_jwt_invlalid_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer demo'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }

def test_token_expired_after_time(client, db_user):

    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/token',
            data={'username': db_user.email, 'password': db_user.plain_password}
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']
    
    with freeze_time('2023-07-14 12:31:00'):
        response = client.put(
            f'/users/{db_user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'demo',
                'email': 'demo@gmail.com',
                'password': 'demo',
            }
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}