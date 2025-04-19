from django.conf import settings
import requests
from django.shortcuts import redirect
from django.urls import reverse
from pypaystack2 import Paystack
from paystackease import PayStackBase, Currency, convert_to_subunit
from pypaystack2 import Paystack
paystack_client = PayStackBase()

def initiate_paystack_payment(request, ref_id, email, amount):
    """
    @param ref_id: Transaction reference
    @param email: Customer email address
    @param amount: Amount to be charged
    @param request: Django request object
    """
    success_path = '/daily/contribution/success/{0}/'.format(ref_id)
    cancel_path = "/daily/contribution/"
    
    success_url = request.build_absolute_uri(success_path)
    cancel_url = request.build_absolute_uri(cancel_path)
        
    metadata = {
            # 'mode':'payment',
            "channels": ["card"],
            'client_reference_id': ref_id,
            'cancel_action': cancel_url,
            "customer_email": email,
    }
    # convert to kobo
    amount = convert_to_subunit(int(amount), currency=Currency.NGN)
    try:
        # call the transaction instance and the initialize() method
        # to initialize or start a transaction.
        session = paystack_client.transactions.initialize(
            email=email, amount=amount, currency="NGN", callback_url=success_url,
            metadata=metadata, reference=ref_id
        )
        request.session["client_ref"] = ref_id
        return {"link": session.data["authorization_url"]}
    except Exception as error:
        # send message of failure to the template
        return {"error": str(error)}


def initiate_flutterwave_payment(tx_ref, amount, email, full_name, request):
    """
    @param tx_ref: Transaction reference
    @param amount: Amount to be charged
    @param email: Customer email address
    @param full_name: Customer full name
    @param request: Django request object
    """
    
    url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    success_path = '/daily/contribution/success/{}/'.format(tx_ref)
    success_url = 'http://127.0.0.1:8000/daily/contribution/success/{}/'.format(tx_ref)
    data = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "redirect_url": success_url,
        "payment_options": "card",
        "customer": {
            "email": email,
            "name": full_name,
        },
        "customizations": {
                "title": "Daily Contribution",
                "description": "Payment for contribution for the day",
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(response.reason)
        return {"error": "Failed to initiate payment"}
    res_data = response.json()
    if res_data.get("status") == "success":
        return {"link":res_data['data']['link']}
    else:
        return {"error": res_data.get("message", "An error occurred")}

def initialize_flutterwave_payment(amount, email, phone_number, redirect_url):
    url = 'https://api.flutterwave.com/v3/payments'
    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'tx_ref': 'unique-transaction-reference',
        'amount': amount,
        'currency': 'NGN',
        'redirect_url': redirect_url,
        'payment_options': 'card,ussd',
        'customer': {
            'email': email,
            'phonenumber': phone_number,
            'name': 'Customer Name'
        },
        'customizations': {
            'title': 'Payment Title',
            'description': 'Payment Description',
            'logo': 'https://example.com/logo.png'
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['data']['link']
    else:
        return None
    
def verify_flutterwave_payment(transaction_id):
    url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'
    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
amount = 1000
email = 'customer@example.com'
phone_number = '08012345678'
redirect_url = 'https://example.com/payment-redirect'

# payment_link = initialize_flutterwave_payment(amount, email, phone_number, redirect_url)
# if payment_link:
#     # Redirect the user to the payment link
#     print(payment_link)
# else:
#     # Handle payment initialization failure
#     print("bad")