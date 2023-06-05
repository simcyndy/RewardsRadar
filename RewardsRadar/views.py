# square_api/views.py

from django.http import JsonResponse
from django.views.generic import DetailView
from RewardsRadar.forms import CustomerRegistrationForm
from .square_service import get_locations
from RewardsRadar.track_purchase import track_purchase
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from square.client import Client
import requests
from django.conf import settings
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
import json
from RewardsRadar.models import Customer , Transaction, RewardTier, User
from .forms import SubscriptionForm, RewardTierForm, AddPointsForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import uuid

def home(request):
    return render(request, 'home.html')

def products_view(request):
    # Your logic for the products view goes here
    # Retrieve products from the database or any other necessary operations
    products = Product.objects.all()
    
    context = {
        'products': products
    }
    
    return render(request, 'products.html', context)

def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {'product': product}
    return render(request, 'product.html', context)

def locations_view(request):
    locations = get_locations()
    return JsonResponse(locations)

def process_purchase(request):
    # Process the purchase and retrieve customer ID and purchase amount
    customer_id = request.POST.get('customer_id')
    purchase_amount = request.POST.get('purchase_amount')

    # Call the track_purchase function to update the customer's points
    track_purchase(customer_id, purchase_amount)

def points_redemption_view(request):
    # Fetch customer's points from the model
    customer_id = request.user.id  # Assuming the user is authenticated and customer ID is stored in the user object
    customer = Customer.objects.get(id=customer_id)
    points = customer.points

    if request.method == 'POST':
        # Handle points redemption
        redemption_option = request.POST.get('redemption_option')
        # Apply the redemption logic based on the selected option
        if redemption_option == 'discount':
            # Apply discount using Square's API
            # Make an API request to Square to apply the discount
            # Update customer's model with decreased points
            customer.points -= 100  # Decrease points by 100 (example)
            customer.save()
            # Render a success message or redirect to a success page

    # Render the template with customer's points and redemption options
    return render(request, 'points_redemption.html', {'points': points})

@csrf_exempt
def square_webhook_view(request):
    if request.method == 'POST':
        # Verify webhook signature (Square provides a guide on how to do this)

        # Parse the webhook payload
        payload = json.loads(request.body)
        
        # Extract necessary information from the webhook payload
        event_type = payload['event_type']
        customer_id = payload['customer_id']
        transaction_amount = payload['transaction_amount']

        # Update customer's points based on the event type
        if event_type == 'TRANSACTION_CREATED':
            customer = Customer.objects.get(id=customer_id)
            customer.points += int(transaction_amount)
            customer.save()

        # Return a response to acknowledge successful processing of the webhook
        return HttpResponse(status=200)

    # For other request methods, return an empty response
    return HttpResponse(status=204)

def customer_registration(request):
    # Handle form submission
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Make API call to Square
            headers = {
                'Authorization': f'Bearer {settings.SQUARE_ACCESS_TOKEN}',
                'Content-Type': 'application/json',
            }
            data = {
                'given_name': name,
                'email_address': email,
                # 'password': password,
            }
            response = requests.post('https://connect.squareupsandbox.com/v2/customers', json=data, headers=headers)
            print (response)

            # Check the API response
            if response.status_code == 200:
                # Customer registration successful
                return redirect('customer_profile', pk=response.json()['customer']['id'])
            else:
                # Customer registration failed
                error_message = response.json()['errors'][0]['detail']
                return render(request, 'customer/customer_registration.html', {'form': form, 'error_message': error_message})

    # Render the registration form
    else:
        form = CustomerRegistrationForm()
        return render(request, 'customer_registration.html', {'form': form})

# class CustomerProfileView(DetailView):
#     model = Customer
#     template_name = 'customer_profile.html'
#     context_object_name = 'customer'
#     slug_field = 'square_id' 
#     slug_url_kwarg = 'pk'


class CustomerProfileView(DetailView):
    model = User
    template_name = 'customer/customer_profile.html'
    context_object_name = 'customer'
    slug_field = 'square_id'
    slug_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        square_id = self.kwargs.get(self.slug_url_kwarg)
        if square_id is not None:
            queryset = queryset.filter(square_id=square_id)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

@csrf_exempt
def webhook_view(request):
    if request.method == 'POST':
        webhook_data = json.loads(request.body)
        event_type = webhook_data['type']
        if event_type == 'payment.created':
            # Assuming webhook_data contains 'reward_points' and 'customer_id'
            reward_points = webhook_data['data']['object']['reward_points']
            customer_id = webhook_data['data']['object']['customer']['id']

            customer = Customer.objects.get(square_customer_id=customer_id)

            Transaction.objects.create(
                transaction_id=webhook_data['data']['object']['id'],
                customer=customer,
                reward_points=reward_points
            )

        return HttpResponse(status=200)

    else:
        return HttpResponse(status=405)

def create_reward_tier(request):
    if request.method == 'POST':
        form = RewardTierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reward_tier_list')
    else:
        form = RewardTierForm()
    
    return render(request, 'rewards/create_reward_tier.html', {'form': form})

def reward_tier_list(request):
    reward_tiers = RewardTier.objects.all()
    return render(request, 'rewards/reward_tier_list.html', {'reward_tiers': reward_tiers})

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            reward_tier = form.cleaned_data['reward_tier']
            request.user.customer.reward_tier = reward_tier
            request.user.customer.save()
            return redirect('profile')  # Replace 'profile' with your desired success URL
    else:
        form = SubscriptionForm()
    
    return render(request, 'subscribe.html', {'form': form})

# WOrks Form here

class CustomerRegistrationView(TemplateView):
    template_name = 'customer/customer_registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomerRegistrationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            print('Form is valid')  # Debugging print statement
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']

            client = Client(
                access_token=settings.SQUARE_ACCESS_TOKEN,
                environment='sandbox', 
            )

            body = {
                'given_name': name,
                'email_address': email,
            }
            response = client.customers.create_customer(body)

            if response.is_success():
                print('Successful Square API response')  # Debugging print statement
                square_id = response.body['customer']['id']

                customer = Customer.objects.create(
                    name=name,
                    email=email,
                    square_id=square_id
                )
                customer.add_points(100) 
                customer.save()
                
                request.session['customer_id'] = customer.id
                request.session['points_earned'] = 100
                return redirect('welcome')
            else:
                error_message = response.errors[0]['detail']
                print('Square API error:', error_message)  # Debugging print statement
                return render(request, self.template_name, {'form': form, 'error_message': error_message})
        else:
            print(form.errors)  # Print form errors
            return render(request, self.template_name, {'form': form})
        # print('Form is not valid')  # Debugging print statement
        # return render(request, self.template_name, {'form': form})


def welcome_view(request):
    points_earned = request.session.get('points_earned', 0)
    customer_id = request.session.get('customer_id')
    customer = Customer.objects.get(id=customer_id)

    return render(request, 'customer/welcome.html', {
        'customer': customer,
        'points_earned': points_earned,
    })

from django.views.generic import ListView
from .models import Product
import square.client

class ProductListView(ListView):
    model = Product
    template_name = 'products/products_listing.html'
    context_object_name = 'products'

def payment_failure(request):
    return render(request, 'payments/payment_failure.html')

client = Client(
    access_token=settings.SQUARE_ACCESS_TOKEN,
    environment=settings.SQUARE_ENVIRONMENT,
)

def product_purchase_confirmation(request, product_id):
    product = Product.objects.get(id=product_id)
    print(product.id)
    return render(request, 'products/product_purchase_confirmation_page.html', {'product': product})

@csrf_exempt
def process_payment_view(request, product_id):
    product = Product.objects.get(id=product_id)
    
    # Get the payment nonce from the request
    nonce = request.POST.get('payment_nonce')  # Replace 'payment_nonce' with the actual name of the form field containing the nonce
    
    # Create the Square payment request
    request_body = {
        'source_id': nonce,
        'idempotency_key': str(uuid.uuid4()),  # Generate a unique idempotency key for each request
        "amount_money": {
           'amount': int(product.price * 100),
            "currency": "USD"
            }  
    }

    # body = {
    # "source_id": "cnon:CBASEMBVgSve75ExbVlesbe_xYE",
    # "idempotency_key": "fdce92bc-dd28-4b8a-bd59-e913a85e92d4",
    # "amount_money": {
    #   "amount": 10,
    #   "currency": "USD"
    # }
    print (request_body)
    # Process the payment
    try:
        response = client.payments.create_payment(request_body)
        print("This is the response",response)
        if response.is_success():
            # Payment is successful
            # Update the customer's points or perform any other necessary actions
            # Get the customer ID from the session
            customer_id = request.session.get('customer_id')
            print (customer_id)

            # Retrieve the customer from the database
            customer = Customer.objects.get(id=customer_id)

            # Update the customer's points
            points_earned = 20  # Replace with the actual number of points earned for the purchase
            customer.add_points(points_earned)
            customer.save()

            return redirect('payment_success')  # Redirect to the sucess page
        else:
            # Payment failed
            error_message = response.errors[0]['detail']
            # Handle the error appropriately
            # ...
    except square.exceptions.ApiException as e:
        # An exception occurred during the API call
        error_message = str(e)
        # Handle the exception appropriately
        # ...
    
    return redirect('payment_failure')  # Redirect to the product listing page if payment processing fails

def success_page(request):
    # Retrieve the customer ID from the session
    customer_id = request.session.get('customer_id')

    # Retrieve the customer from the database
    customer = Customer.objects.get(id=customer_id)

    # Retrieve the earned points from the session
    points_earned = request.session.get('points_earned')
    print("Points Eraned success_page ", points_earned)

    return render(request, 'customer/success_page.html', {
        'customer': customer,
        'points_earned': points_earned,
    })


@login_required
def profile_view(request):
    customer = Customer.objects.get(email=request.user.email)
    points = customer.points
    if request.method == 'POST':
        form = AddPointsForm(request.POST)
        if form.is_valid():
            points = form.cleaned_data['points']
            customer.add_points(points)
            customer.save()
            messages.success(request, f'Successfully added {points} points!')
            return redirect('profile_view')
    else:
        form = AddPointsForm()

    return render(request, 'customer/customer_profile.html', {
        'points': points,
        'form': form,
        'customer': customer,
    })

class CustomerLoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'customer/customer_login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('customer_profile')
        else:
            return render(self.request, self.template_name, {'form': form, 'invalid_creds': True})


from square.client import Client
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            customer = request.user.customer
            tier = form.cleaned_data['tier']
            # Assume that 'location_id' and 'plan_id' are part of the form or predefined

            client = Client(
                access_token=settings.SQUARE_ACCESS_TOKEN,
                environment='sandbox', 
            )

            # Create a new subscription in Square
            body = {
                'location_id': form.cleaned_data['location_id'],
                'plan_id': form.cleaned_data['plan_id'],
                'customer_id': customer.square_id,  # Use the Square ID of the customer
            }
            response = client.subscriptions.create_subscription(body)

            if response.is_success():
                # Add points to the customer
                points = get_points_for_tier(tier)  # This function should return the points for a given tier
                customer.add_points(points)
                customer.save()

                subscription = Subscription.objects.create(
                    square_id=response.body['subscription']['id'],
                    start_date=response.body['subscription']['start_date'],
                    end_date=form.cleaned_data['end_date'],  # You might need to calculate this based on the subscription plan
                    customer=customer,
                    tier=tier,
                )

                return redirect('profile')  # Replace 'profile' with your desired success URL
            else:
                error_message = response.errors[0]['detail']
                return render(request, 'subscriptions/create_subscription.html', {'form': form, 'error_message': error_message})

    else:
        form = SubscriptionForm()

    return render(request, 'subscriptions/create_subscription.html', {'form': form})


