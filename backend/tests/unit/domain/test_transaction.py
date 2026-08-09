import pytest
from datetime import datetime, timezone
from uuid import uuid4
from src.domain.models.transaction import Transaction
from pydantic import ValidationError

def test_transaction_creation_valid():
    account_id = uuid4()
    now = datetime.now(timezone.utc)
    
    txn = Transaction(
        account_id=account_id,
        type="EXPENSE",
        amount=50.0,
        description="Groceries",
        source="manual",
        transaction_date=now
    )
    
    assert txn.account_id == account_id
    assert txn.type == "EXPENSE"
    assert txn.amount == 50.0
    assert txn.currency == "EUR"
    assert txn.status == "confirmed"

def test_transaction_invalid_type():
    with pytest.raises(ValidationError):
        Transaction(
            account_id=uuid4(),
            type="INVALID_TYPE", # Type validation
            amount=50.0,
            description="Groceries",
            source="manual",
            transaction_date=datetime.now(timezone.utc)
        )
