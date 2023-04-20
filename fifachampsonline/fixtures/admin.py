from django.contrib import admin
from .models import Fixture, Player, Item, HeadToHead, Matches, Purchase, Result, Booking

# Register your models here.

admin.site.register(Fixture)
admin.site.register(Player)
admin.site.register(Item)
admin.site.register(HeadToHead)
admin.site.register(Purchase)
admin.site.register(Matches)
admin.site.register(Result)
admin.site.register(Booking)