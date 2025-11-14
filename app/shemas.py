from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
from app.wallet_models import OperationType


class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ed749016-d409-462f-bcee-b2c654b008fb",
                "balance": "0.00",
            }
        }
    }


class OperationResponse(BaseModel):
    wallet_id: UUID
    operation: OperationType
    amount: Decimal
    balance: Decimal

    model_config = {
        "json_schema_extra": {
            "example": {
                "wallet_id": "ed749016-d409-462f-bcee-b2c654b008fb",
                "operation": "Deposit",
                "amount": "38382",
                "balance": "38382.00"
            }
        }
    }


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0)
