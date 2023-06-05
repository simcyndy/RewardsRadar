from square.client import Client

SQUARE_ACCESS_TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN')
SQUARE_ENVIRONMENT = os.environ.get('SQUARE_ENVIRONMENT', 'sandbox')

client = Client(
     access_token=SQUARE_ACCESS_TOKEN,
     environment=SQUARE_ENVIRONMENT,
   )

# Get a mapping of reward tier names to Square subscription plan IDs
SQUARE_SUBSCRIPTION_PLAN_IDS = {
    'Bronze': 'plan_id_for_bronze',
    'Silver': 'plan_id_for_silver',
    'Gold': 'plan_id_for_gold',
}

class UserProfile(models.Model):
    # ...

    square_subscription_id = models.CharField(max_length=255, null=True)

    def update_tier(self):
        # ...

        # Update the user's subscription in Square
        if self.tier is not None:
            plan_id = SQUARE_SUBSCRIPTION_PLAN_IDS[self.tier.name]
            if self.square_subscription_id is None:
                # Create a new subscription
                body = {
                    'idempotency_key': str(uuid.uuid4()),
                    'location_id': 'your_location_id',  # Replace with your location ID
                    'plan_id': plan_id,
                    'customer_id': 'your_customer_id',  # Replace with your customer ID
                }
                response = client.subscriptions.create_subscription(body)
                if response.is_success():
                    self.square_subscription_id = response.body['subscription']['id']
            else:
                # Update the existing subscription
                body = {
                    'subscription': {
                        'plan_id': plan_id,
                    }
                }
                response = client.subscriptions.update_subscription(self.square_subscription_id, body)
            self.save()
