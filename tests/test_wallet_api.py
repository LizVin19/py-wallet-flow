import pytest
import asyncio


@pytest.mark.asyncio
async def test_create_wallet(client):
    resp = await client.post('/api/v1/wallets')
    assert resp.status_code == 201

    data = resp.json()
    assert 'id' in data
    assert 'balance' in data
    assert float(data['balance']) == 0.0


@pytest.mark.asyncio
async def test_deposit_operation_increases_balance(client):
    # 1. Create a wallet
    create_resp = await client.post('/api/v1/wallets')
    assert create_resp.status_code == 201
    wallet = create_resp.json()
    wallet_id = wallet['id']

    # 2. Deposit
    op_resp = await client.post(
        f'/api/v1/wallets/{wallet_id}/operation',
        json={
            'operation_type': 'Deposit',
            'amount': 100
        }
    )
    assert op_resp.status_code == 200
    op_data = op_resp.json()
    assert op_data['wallet_id'] == wallet_id
    assert float(op_data['balance']) == 100.0

    # 3. Check balance
    get_resp = await client.get(f'/api/v1/wallets/{wallet_id}')
    assert get_resp.status_code == 200
    balance_data = get_resp.json()
    assert float(balance_data['balance']) == 100.0


@pytest.mark.asyncio
async def test_withdraw_operation_decreases_balance(client):
    # 1. Create a wallet
    create_resp = await client.post('/api/v1/wallets')
    wallet_id = create_resp.json()['id']

    # 2. Top up wallet
    await client.post(
        f'/api/v1/wallets/{wallet_id}/operation',
        json={
            'operation_type': 'Deposit',
            'amount': 200
        }
    )

    # 3. Withdraw
    withdraw_resp = await client.post(
        f'/api/v1/wallets/{wallet_id}/operation',
        json={'operation_type': 'Withdraw', 'amount': 50}
    )
    assert withdraw_resp.status_code == 200
    data = withdraw_resp.json()
    assert float(data['balance']) == 150.00


@pytest.mark.asyncio
async def test_wallet_not_found_returns_404(client):
    fake_id = '00000000-0000-0000-0000-000000000000'

    # get /api/v1/wallets/{WALLET_UUID}
    get_resp = await client.get(f'/api/v1/wallets/{fake_id}')
    assert get_resp.status_code == 404

    # post /api/v1/wallets/{WALLET_UUID}/operation
    op_resp = await  client.post(
        f'/api/v1/wallets/{fake_id}/operation',
        json={'operation_type': 'Deposit', 'amount': 10}
    )
    assert op_resp.status_code == 404


@pytest.mark.asyncio
async def test_parallel_deposits_keep_balance_consistent(client):
    # 1. Create a wallet
    create_resp = await client.post("/api/v1/wallets")
    assert create_resp.status_code == 201
    wallet_id = create_resp.json()["id"]

    # 2. 10 parallel deposits of 100 each
    async def do_deposit():
        resp = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "Deposit", "amount": 100},
        )
        assert resp.status_code == 200

    await asyncio.gather(*[do_deposit() for _ in range(10)])

    # 3. Check the final balance
    get_resp = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert float(data["balance"]) == 1000.0




