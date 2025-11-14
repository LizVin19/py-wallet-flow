import enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from sqlalchemy import Numeric, ForeignKey, DateTime, Enum as SAEnum
from datetime import datetime, UTC
from sqlalchemy.orm import relationship, mapped_column
from app.db import Base


class Wallet(Base):
    __tablename__ = 'wallets'

    id = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = mapped_column(Numeric(10, 2), nullable=False, default=0)

    operations = relationship("Operation", back_populates="wallet")

class OperationType(str, enum.Enum):
    withdraw = 'Withdraw'
    deposit = 'Deposit'

class Operation(Base):
    __tablename__ = 'operations'

    id = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False)
    type = mapped_column(SAEnum(OperationType), nullable=False)
    amount = mapped_column(Numeric(10, 2), nullable=False)
    created_date = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    wallet = relationship('Wallet', back_populates='operations')

