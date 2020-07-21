import json
import os

from kombu import Connection, Queue, Exchange
from kombu.mixins import ConsumerProducerMixin

from models import Payment, payments, PaymentStatus, serialize_payments


class Worker(ConsumerProducerMixin):
    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        exchange = Exchange("payment", "topic")
        return [
            Consumer(
                queues=[Queue("payment.pay", exchange=exchange, routing_key="pay")],
                on_message=self.pay,
                accept=["json"],
            ),
            Consumer(
                queues=[Queue("payment.pay_checked", exchange=exchange, routing_key="pay_checked")],
                on_message=self.pay_checked,
                accept=["json"],
            ),
            Consumer(
                queues=[Queue("payment.get_payments", exchange=exchange, routing_key="get_payments")],
                on_message=self.get_payments,
                accept=["json"],
            ),
        ]

    def pay(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        print(f"receive body: {request}")
        payments[request["id"]] = Payment(request["id"], request["amount"], PaymentStatus.PENDING)
        self.producer.publish(
            body={
                "user_id": request["user_id"],
                "payment_id": request["id"],
                "money": request["amount"],
            },
            exchange="user",
            routing_key="has_money",
            serializer='json',
        )
        message.ack()

    def pay_checked(self, message):
        print(f"receive task: {message}")
        request = json.loads(message.body)
        print(f"receive body: {request}")
        payment_id = request["payment_id"]
        status = request["status"]
        if status == "accept":
            payments[payment_id].status = PaymentStatus.FINISHED
            self.producer.publish(
                body={
                    "user_id": request["user_id"],
                    "money": payments[payment_id].amount,
                },
                exchange="user",
                routing_key="reduce_money",
                serializer='json',
            )
        elif status == "reject":
            payments[payment_id].status = PaymentStatus.REJECTED
        message.ack()

    def get_payments(self, message):
        request = json.loads(message.body)
        exchange = request["reply_to_exchange"]
        routing_key = request["reply_to_routing_key"]
        self.producer.publish(
            body=serialize_payments(payments),
            exchange=exchange,
            routing_key=routing_key,
            serializer='json',
        )
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
