# kombu-kube-example
Build:

`docker build user_service --tag user-service:1.0`

`docker build payment_service --tag payment-service:1.0`

Run:

`kubectl apply -f rabbitmq/rabbitmq-deployment.yaml`

`kubectl apply -f user_service/deployment.yaml`

`kubectl appply -f payment_service/deployment.yaml`


Rabbitmq:
1. Check all payments/users
`{"reply_to_exchange": "worker", "reply_to_routing_key": "worker"}`
2. Add user
`{"id": 1, "first_name": "John", "last_name": "Doe", "money": 300}`
3. Add payment
`{"id": 1, "amount": 100, "user_id": 1}`

Process:
1. `payment_service.pay` initializes payment
2. `payment_service.pay` asks `user_service.has_money`
3. `user_service.has_money` responses to `payment_service.pay_checked`
4. if user has money then `payment_service.pay_checked` asks `user_service.reduce_money` and sets status ACCEPTED 
5. if user has not money then `payment_service.pay_checked` sets status REJECTED 
 