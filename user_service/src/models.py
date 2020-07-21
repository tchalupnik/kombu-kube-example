from dataclasses import dataclass


@dataclass
class User:
    id: int
    first_name: str
    last_name: str
    money: float
    locked_money: float = 0.

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def has_money(self, money):
        enough = self.money - self.locked_money >= money
        if enough:
            self._lock_money(money)
        return enough

    def reduce_money(self, money):
        self._unlock_money(money)
        self.money -= money

    def _lock_money(self, money):
        self.money -= money
        self.locked_money += money

    def _unlock_money(self, money):
        self.locked_money -= money
        self.money += money


users = {}


def serialize_users(users):
    return [{
        "first_name": u.first_name,
        "last_name": u.last_name,
        "money": u.money,
    } for u in users.values()]
