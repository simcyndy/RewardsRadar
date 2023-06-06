import requests
from RewardsRadar.models import Customer 

def track_purchase(customer_id, purchase_amount):
    # Make an HTTP request to Square's Transactions API to track the purchase
    api_endpoint = 'https://connect.squareup.com/v2/locations/LEDT0KBMQZ6EY/transactions'
    headers = {
        'Authorization': 'Bearer EAAAEFRpdoZZVxTj0VN4Kg04vRidG5qi7H3hQNScg-btwkSUIONwnMByJFZANUZp',
        'Content-Type': 'application/json',
    }
    data = {
        'location_id': 'LEDT0KBMQZ6EY',
        'customer_id': customer_id,
        'amount_money': {
            'amount': int(purchase_amount) * 100,
            'currency': 'USD',
        },
    }

    response = requests.post(api_endpoint, headers=headers, json=data)

    if response.status_code == 200:
        # Purchase tracked successfully, update the customer's points
        customer = Customer.objects.get(id=customer_id)
        customer.points += int(purchase_amount)
        customer.save()
        print('Purchase tracked successfully.')
    else:
        print('Error occurred while tracking the purchase:', response.json())
