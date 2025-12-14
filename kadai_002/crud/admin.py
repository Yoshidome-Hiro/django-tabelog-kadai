from django.contrib import admin
from .models import Category, Restaurant, User, Review, Reservation

admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(User)
admin.site.register(Review)
admin.site.register(Reservation)