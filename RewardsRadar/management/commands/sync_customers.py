# sync_customers.py

from square.client import Client

from django.core.management.base import BaseCommand
from RewardsRadar.models import Customer  # Import your Django model
from django.conf import settings

# Initialize Square client
square_client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment='sandbox'  # or 'production' for live environment
)

def sync_customers():
    # Fetch customers from Square
    response = square_client.customers.list_customers()

    if response.is_success():
        # Get the list of customers from the response
        square_customers = response.body.get('customers', [])

        # Update Django model based on Square data
        for square_customer in square_customers:
            customer, created = Customer.objects.get_or_create(
                square_customer_id=square_customer.get('id')
            )
            customer.name = square_customer.get('given_name', '') + ' ' + square_customer.get('family_name', '')
            customer.email = square_customer.get('email_address', '')
            # customer.points = square_customer.get('metadata', {}).get('points', 0)
            customer.save()

        print('Customers synchronized successfully.')
    else:
        print('Error occurred while fetching customers:', response.errors)



class Command(BaseCommand):
    help = 'Synchronize customers between Django model and Square\'s Customers API'

    def handle(self, *args, **options):
        sync_customers()
        self.stdout.write(self.style.SUCCESS('Customers synchronized successfully.'))
