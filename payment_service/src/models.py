from dataclasses import dataclass


class PaymentStatus:
    PENDING = 1
    REJECTED = 2
    FINISHED = 3


@dataclass
class Payment:
    id: int
    amount: float
    status: PaymentStatus


payments = {}


def serialize_payments(payments):
    return [{
        "amount": p.amount,
        "status": p.status,
    } for p in payments.values()]
