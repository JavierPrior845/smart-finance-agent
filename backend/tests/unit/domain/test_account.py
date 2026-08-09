import pytest
from uuid import UUID
from src.domain.models.account import Account

def test_account_creation_defaults():
    account = Account(name="Test Account", account_type="BANK_ACCOUNT")
    
    assert isinstance(account.id, UUID)
    assert account.name == "Test Account"
    assert account.account_type == "BANK_ACCOUNT"
    assert account.currency == "EUR"
    assert account.initial_balance == 0.0
    assert account.current_balance == 0.0
    assert account.is_main is False
    assert account.is_active is True

def test_account_creation_with_values():
    account = Account(
        name="Main Checking",
        account_type="BANK_ACCOUNT",
        currency="USD",
        initial_balance=100.50,
        current_balance=100.50,
        is_main=True
    )
    
    assert account.currency == "USD"
    assert account.initial_balance == 100.50
    assert account.current_balance == 100.50
    assert account.is_main is True
