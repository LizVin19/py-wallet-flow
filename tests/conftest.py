import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from app.main import app
from app.db import AsyncSessionLocal
from app.wallet_models import Wallet, Operation


@pytest.fixture(autouse=True, scope='function')
async def clean_db():
    """ Clean db before test """
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Operation))
        await session.execute(delete(Wallet))
        await session.commit()
    yield


@pytest.fixture
async def client():
    """ HTTP-client on the top of the application (without uvicorn run) """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as c:
        yield c

