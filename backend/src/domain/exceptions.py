class DomainException(Exception):
    """Base exception for all domain business rule violations."""
    pass


class InvalidTransactionAmountError(DomainException):
    def __init__(self, amount: float):
        super().__init__(f"Transaction amount must be non-zero. Got: {amount}")


class CategoryNotFoundError(DomainException):
    def __init__(self, category_id: str):
        super().__init__(f"Category with ID '{category_id}' not found.")
