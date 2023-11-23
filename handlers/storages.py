from datetime import datetime
from dataclasses import dataclass


@dataclass
class Transaction:
    amount: float
    description: str
    category_id: int
    payment_id: int
    account_id: int
    transaction_date: datetime = datetime.utcnow()

    def to_tuple(self):
        return (
            self.amount,
            self.description,
            self.category_id,
            self.payment_id,
            self.account_id,
            self.transaction_date,
        )


@dataclass
class Transfer:
    from_account: int
    to_account: int
    amount: float
    transfer_date: datetime = datetime.utcnow()

    def to_tuple(self):
        return (
            self.from_account,
            self.to_account,
            self.amount,
            self.transfer_date,
        )


@dataclass
class InfoCollection:
    main: float
    opt: float
    stg: float
    debt: float
    month_expenses: float
    month_income: float
    d: float
    top_expenses: float
    top_name: str
    cash: float
    card: float


__all__ = ["Transaction", "Transfer", "InfoCollection"]
