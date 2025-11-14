## Запуск локально (без Docker-контейнера приложения)

### 1. Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Поднять PostgreSQL через docker-compose

```bash
docker compose up -d postgres
```
PostgreSQL будет доступен на localhost:5430.


### 3. Настроить переменные окружения

Создать .env из примера:
```bash
cp .env.example .env
```
>*Важно*: в файле `.env.exapmle` я разместила уже готовые данные для проверки работы всего приложения.

По умолчанию в примере:
```env
DATABASE_URL=postgresql+psycopg://WalletUser:walletuserpassword@localhost:5430/fastapi_wallet
```

### 4. Накатить миграции
```bash
alembic upgrade head
```

### 5. Запустить приложение
```bash
uvicorn app.main:app --reload
```
Документация Swagger UI: http://127.0.0.1:8000/docs


## Полный запуск в Docker

Собрать и запустить приложение и базу:
```bash
docker compose up --build
```
API: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs

В docker-compose.yml приложение использует переменную:
```yaml
DATABASE_URL=postgresql+psycopg://WalletUser:walletuserpassword@postgres:5432/fastapi_wallet
```

Запуск миграций внутри контейнера приложения:
```bash
docker compose run --rm app alembic upgrade head
```

## Тесты

Эндпоинты покрыты тестами, включая тест параллельных операций по одному кошельку.

### Запуск тестов локально 
Требуется запущенный PostgreSQL и накатанные миграции:
```bash
pytest
```

### Запуск тестов в Docker
```bash
docker compose run --rm app pytest
```

## API

Базовый URL: http://127.0.0.1:8000/api/v1

### 1. Создать кошелёк
`POST /api/v1/wallets`

Пример ответа 201:
```json
{
  "id": "ed749016-d409-462f-bcee-b2c654b008fb",
  "balance": 0.0
}
```

### 2. Получить баланс кошелька
`GET /api/v1/wallets/{WALLET_UUID}`

Пример ответа 200:
```json
{
  "id": "ed749016-d409-462f-bcee-b2c654b008fb",
  "balance": 100.0
}
```
Возможные ошибки:
`404 Wallet not found` - кошелёк не найден.

### 3. Операция по кошельку (пополнение / списание)
`POST /api/v1/wallets/{WALLET_UUID}/operation`

Тело запроса:
```json
{
  "operation_type": "Deposit", // или "Withdraw"
  "amount": 100.0
}
```

Пример ответа 200:
```json
{
  "wallet_id": "ed749016-d409-462f-bcee-b2c654b008fb",
  "operation": "Deposit",
  "amount": 100.0,
  "balance": 200.0
}
```

Проверки и ошибки:

- `amount` должен быть строго больше 0;
- при списании и недостаточном балансе - `400 Insufficient funds`;
- при неизвестном `WALLET_UUID` - `404 Wallet not found`.


## Конкурентный доступ

Обновление баланса выполняется в транзакции с блокировкой строки кошелька.
```python
...select(Wallet).where(Wallet.id == wallet_id).with_for_update()
```
