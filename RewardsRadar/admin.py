from django.contrib import admin
from .models import Product, Customer, Transaction, RewardTier

admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Transaction)
admin.site.register(RewardTier)
# admin.site.register(UserProfile)