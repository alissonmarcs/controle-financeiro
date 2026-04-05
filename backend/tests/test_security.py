from jwt import decode

from backend.security import SECRET_KEY, create_access_token
from http import HTTPStatus

def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])
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