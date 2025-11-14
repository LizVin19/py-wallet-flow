from fastapi import FastAPI, HTTPException, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shemas import WalletResponse, OperationResponse
from app.db import get_db
from app.wallet_models import Wallet, OperationType, Operation
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal

app = FastAPI(title='FastAPI Wallet')


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal


async def get_wallet_or_error(wallet_id: UUID, db: AsyncSession) -> Wallet:
    res = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = res.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(status_code=404, detail='Wallet not found')
    return wallet


@app.post('/api/v1/wallets', status_code=status.HTTP_201_CREATED, response_model=WalletResponse)
async def create_wallet(db: AsyncSession = Depends(get_db)):
    wallet = Wallet()
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)

    return WalletResponse(id=wallet.id, balance=wallet.balance)


@app.get('/api/v1/wallets/{WALLET_UUID}', response_model=WalletResponse)
async def get_wallet_balance(
        wallet_id: UUID = Path(..., alias='WALLET_UUID'),
        db: AsyncSession = Depends(get_db)):
    wallet = await get_wallet_or_error(wallet_id, db)
    return WalletResponse(id=wallet.id, balance=wallet.balance)


@app.post('/api/v1/wallets/{WALLET_UUID}/operation', response_model=OperationResponse)
async def operation(
    wallet_id: UUID = Path(..., alias="WALLET_UUID"),
    op: OperationRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    if op.amount <= 0:
            raise HTTPException(status_code=400, detail='Amount must be positive')

    async with db.begin():
        res = await db.execute(select(Wallet).where(Wallet.id == wallet_id).with_for_update())
        wallet = res.scalar_one_or_none()

        if wallet is None:
             raise HTTPException(status_code=404, detail='Wallet not found')

        if op.operation_type == OperationType.deposit:
            wallet.balance += op.amount

        elif op.operation_type == OperationType.withdraw:
            if wallet.balance <  op.amount:
                raise HTTPException(status_code=400, detail='Insufficient funds')
            wallet.balance -= op.amount

        else:
            raise HTTPException(400, 'Invalid operation type')

        op_info = Operation(wallet_id=wallet.id, type=op.operation_type, amount=op.amount)
        db.add(op_info)

    await db.refresh(wallet)

    return OperationResponse(
        wallet_id=wallet.id,
        operation=op.operation_type,
        amount=op.amount,
        balance=wallet.balance,
    )
