from fastapi.testclient import TestClient

from backend.app import app, expenses_fake_db

client = TestClient(app)


def setup_function() -> None:
	expenses_fake_db.clear()


def test_create_expense_returns_201_and_created_expense() -> None:
	payload = {
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}

	response = client.post('/expenses/', json=payload)

	assert response.status_code == 201
	assert response.json() == {
		'id': 1,
		'title': 'Mercado',
		'description': 'Compra semanal',
		'value': 250,
	}
	assert len(expenses_fake_db) == 1


def test_create_expense_with_invalid_description_returns_422() -> None:
	payload = {
		'title': 'Transporte',
		'description': '',
		'value': 35,
	}

	response = client.post('/expenses/', json=payload)

	assert response.status_code == 422
	assert len(expenses_fake_db) == 0


def test_create_expense_increments_id() -> None:
	first_payload = {
		'title': 'Almoco',
		'description': 'Restaurante',
		'value': 42,
	}
	second_payload = {
		'title': 'Internet',
		'description': 'Mensalidade',
		'value': 120,
	}

	first_response = client.post('/expenses/', json=first_payload)
	second_response = client.post('/expenses/', json=second_payload)

	assert first_response.status_code == 201
	assert second_response.status_code == 201
	assert first_response.json()['id'] == 1
	assert second_response.json()['id'] == 2
	assert len(expenses_fake_db) == 2
