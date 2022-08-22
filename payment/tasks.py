import requests
from celery import shared_task

payment = requests.Session()


@shared_task()
def send_payment_request(payload, url):
    response = payment.post(url, json=payload)
    return response.json()
