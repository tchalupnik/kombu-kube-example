import json
import os

from kombu import Connection, Queue, Exchange
from kombu.mixins import ConsumerProducerMixin

from models import users, User, serialize_users


class Worker(ConsumerProducerMixin):
    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        exchange = Exchange("user", "topic")
        return [
            Consumer(
                queues=[Queue("user.create", exchange=exchange, routing_key="create_user")],
                on_message=self.create,
                accept=["json"],
            ),
            Consumer(
                queues=[Queue("user.all", exchange=exchange, routing_key="get_users")],
                on_message=self.get_users,
                accept=["json"],
            ),
            Consumer(
                queues=[Queue("user.has_money", exchange=exchange, routing_key="has_money")],
                on_message=self.has_money,
                accept=["json"],
            ),
            Consumer(
                queues=[Queue("user.reduce_money", exchange=exchange, routing_key="reduce_money")],
                on_message=self.reduce_money,
                accept=["json"],
            ),
        ]

    def create(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        users[request["id"]] = User(request["id"], request["first_name"], request["last_name"], request["money"])
        message.ack()

    def get_users(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        exchange = request["reply_to_exchange"]
        routing_key = request["reply_to_routing_key"]
        self.producer.publish(
            body=serialize_users(users),
            exchange=exchange,
            routing_key=routing_key,
            serializer='json',
        )
        message.ack()

    def has_money(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        payment_id = request["payment_id"]
        has_money = users[request["user_id"]].has_money(request["money"])
        self.producer.publish(
            body={
                "user_id": request["user_id"],
                "payment_id": payment_id,
                "status": "accept" if has_money else "reject",
            },
            exchange="payment",
            routing_key="pay_checked",
            serializer='json',
        )
        message.ack()

    def reduce_money(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        user_id = request["user_id"]
        users[user_id].reduce_money(request["money"])
        message.ack()

    def on_connection_error(self, exc, interval):
        super(Worker, self).on_connection_error(exc, interval)
        print(exc)

    def on_connection_revived(self):
        print('Connection revived')

    def on_decode_error(self, message, exc):
        super(Worker, self).on_decode_error(message, exc)
        print(f"{exc} {message}")


connection = Connection(os.environ.get("AMQP_URL"))
w = Worker(connection)
w.run()
