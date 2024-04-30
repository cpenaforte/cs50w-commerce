from .models import Watchlist, User

def watched_listings_processor(request):
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        try:
            watchlist = Watchlist.objects.get(user=user)
            return {'watched_listings_global': watchlist.auction_listings.all()}
        except Watchlist.DoesNotExist:
            return {'watched_listings_global': []}
    else:
        return {'watched_listings_global': []}