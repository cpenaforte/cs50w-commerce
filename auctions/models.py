from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class AuctionListing(models.Model):
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="auction_listings")
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    item_name = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    final_date = models.DateTimeField(default=(timezone.now() + timedelta(days=15)))
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name="auction_listings")
    current_bid = models.ForeignKey("Bid", blank=True, null=True, on_delete=models.SET_NULL, related_name="winning_listing")

    def __str__(self):
        return self.item_name

class Bid(models.Model):
    bid_date = models.DateTimeField(auto_now_add=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")
    auction_listings = models.ManyToManyField(AuctionListing, blank=True, related_name="watchlists")

class Comment(models.Model):
    text = models.TextField()
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")