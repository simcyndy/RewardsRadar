from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User
from django.conf import settings
from square.client import Client
import uuid

class RewardTier(models.Model):
    name = models.CharField(max_length=100)
    points_required = models.PositiveIntegerField(default=0)
    benefits = models.TextField()

    def __str__(self):
        return self.name

# Get a mapping of reward tier names to Square subscription plan IDs
SQUARE_SUBSCRIPTION_PLAN_IDS = {
    'Basic': 'LSQ5WIOLEKYROF34OTPDEVPP',
    # 'Silver': 'plan_id_for_silver',
    # 'Gold': 'plan_id_for_gold',
}

class CustomerManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        customer = self.model(email=email, name=name)
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

    def create_superuser(self, email, name, password=None):
        customer = self.create_user(email, name, password)
        customer.is_admin = True
        customer.save(using=self._db)
        return customer


class Customer(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    points = models.IntegerField(default=0)
    square_id = models.CharField(max_length=255, unique=True)
    square_subscription_id = models.CharField(max_length=255, null=True)
    #Tie program to customer.
    reward_tier = models.ForeignKey(RewardTier, on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    def update_tier(self):
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment=settings.SQUARE_ENVIRONMENT,
            )


        if self.reward_tier is not None:
            plan_id = SQUARE_SUBSCRIPTION_PLAN_IDS[self.reward_tier.name]
            if self.square_subscription_id is None:
                # Create a new subscription
                body = {
                    'idempotency_key': str(uuid.uuid4()),
                    'location_id': settings.LOCATION_ID,  # Replace with your location ID
                    'plan_id': plan_id,
                    'customer_id': settings.CUSTOMER_ID,  # Replace with your customer ID
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

    def add_points(self, points):
        self.points += points
        self.update_tier()
        self.save()

    def subtract_points(self, points):
        self.points = max(0, self.points - points)
        self.update_tier()
        self.save()
    
class Subscription(models.Model):
    square_id = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tier = models.CharField(max_length=100)

class Transaction(models.Model):
    square_transaction_id = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    reward_points = models.PositiveIntegerField() 

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
