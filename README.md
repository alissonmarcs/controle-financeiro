## Como rodar o projeto ?

Dependências: `docker` e `poetry`.

```bash
git clone https://github.com/alissonmarcs/controle-financeiro.git
cd controle-financeiro/backend
touch .env
```

### Exemplo de `.env`

```
DATABASE_URL="postgresql+psycopg://app_user:app_password@0.0.0.0:5432/app_db"
SECRET_KEY="8c6bbcadfc0047fb5ba951a58a193d3ac33afb53a984be1d4d5f7c3235c48be2109fb5363b7a7261fcbe11a69f45ee2cc79a40c20526083e0e8b736cdf87820b"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Rodando o app no host e o DB no container

```bash
poetry install
poetry shell
docker compose up -d controle_financeiro_db
fastapi dev backend/app.py
```

Para parar o containter do DB: `docker compose down controle_financeiro_db`

### Rodando o app e o DB em containers:

```bash
docker compose up
```

Para parar os dois containers: `docker compose down`

## Como rodar testes

### Rodar todos os testes:

O container de DB será subido e derrubado automaticamente:

```bash
pytest
```

### Termina a execução na primeira falha:

```bash
pytest -q -x
```

### Roda somente o teste que falhou na ultima execução:

```bash
pytest --lf -q -x
```