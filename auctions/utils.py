from .models import User, Watchlist
from django.utils import timezone

def find_max_bid(auction_listing):
    target_bid = None
    max_bid = auction_listing.starting_bid
    for bid in auction_listing.bids.all():
        if bid.bid >= max_bid:
            max_bid = bid.bid
            target_bid = bid
    return target_bid

def get_watched_listings(user_id):
    user = User.objects.get(id=user_id)
    try:
        listings = list(Watchlist.objects.get(user=user).auction_listings.all())
        return [listing.id for listing in listings]
    except:
        watchlist = Watchlist(user=user)
        watchlist.save()
        return []

def get_default_bid_value(auction_listing):
    if auction_listing.bids.all().count() == 0:
        return auction_listing.starting_bid
    else:
        return find_max_bid(auction_listing).bid + 1

def get_won_listings(user):
    # create won listings set
    won_listings = set()

    bids = user.bids.all()
    for bid in bids:
        listing = bid.auction_listing
        if listing.final_date < timezone.now():
            listing.active = False
            listing.save()
            
            if listing.current_bid and listing.current_bid.bidder.id == user.id:
                won_listings.add(listing)
    return list(won_listings)