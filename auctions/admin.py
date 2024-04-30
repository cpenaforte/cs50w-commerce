from django.contrib import admin

from .models import AuctionListing, Bid, Category, Watchlist, Comment

# Register your models here.
admin.site.register(AuctionListing)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Watchlist)
admin.site.register(Comment)