from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django import forms

from .models import User, Category, AuctionListing, Bid, Watchlist, Comment
from . import utils

# FORMS

class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class Listing_Form(forms.Form):
    item_name = forms.CharField(label="Item Name", widget=forms.TextInput(attrs={'placeholder': 'Type a name', 'style': 'width: 100%;'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'placeholder': 'Type a description', 'rows': '5', 'style': 'width: 100%; resize:none;'}))
    starting_bid = forms.DecimalField(label="Starting Bid", widget=forms.NumberInput(attrs={'placeholder': 'Type a starting bid', 'style': 'width: 100%;'}))
    final_date = forms.DateTimeField(label="Final Date", initial=timezone.now(), widget=DateTimePickerInput())
    image_url = forms.URLField(label="Image URL", required=False, widget=forms.URLInput(attrs={'placeholder': 'Type an image URL', 'style': 'width: 100%;'}))

    CHOICES = ([(category.title, category.title) for category in Category.objects.all()] + [("","No category")])
    category_title = forms.ChoiceField(label="Category", choices=CHOICES, required=False)

class Bid_Form(forms.Form):
    bid = forms.DecimalField(label="", widget=forms.NumberInput(attrs={'placeholder': 'Type a bid'}))

class Comment_Form(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Type a comment', 'rows': '3', 'style': 'resize:none;'}))

# VIEWS

def index(request):
    listings= AuctionListing.objects.filter(active=True).all()
    # Inactivate listings if it's past the final date
    for listing in listings:
        if listing.final_date < timezone.now():
            listing.active = False
            listing.save()
    if request.user.is_authenticated:
        return render(request, "auctions/index.html", {
            "auction_listings": AuctionListing.objects.filter(active=True).all(),
        })
    return render(request, "auctions/index.html", {
        "auction_listings": [],
    })

@login_required
def self_listings(request):
    user = None
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))
    return render(request, "auctions/self_listings.html", {
        "auction_listings": AuctionListing.objects.filter(creator=user).all(),
    })

@login_required
def create(request):
    if request.method == "POST":
        form = Listing_Form(request.POST)
        if form.is_valid():
            item_name = form.cleaned_data["item_name"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]

            final_date = form.cleaned_data["final_date"]
            print(final_date, timezone.now())
            if final_date < timezone.now():
                return render(request, "auctions/create.html", {
                    "is_edit": False,
                    "form": form,
                    "error": "Final date must be in the future."
                })

            image_url = form.cleaned_data["image_url"]
            category_title = form.cleaned_data["category_title"]
            category = None
            if category_title != "":
                category = Category.objects.get(title=category_title)

            creator = None
            try:
                creator = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                return HttpResponseRedirect(reverse("auctions:logout"))

            auction_listing = AuctionListing(creator=creator,item_name=item_name, description=description, starting_bid=starting_bid, final_date=final_date, image_url=image_url, category=category)
            auction_listing.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        return render(request, "auctions/create.html", {
                "is_edit": False,
                "form": form,
                "error": form.errors
            })
    return render(request, "auctions/create.html", {
        "is_edit": False,
        "form": Listing_Form(),
        "categories": Category.objects.all(),
        "error": ""
    })

@login_required
def listing(request, listing_id):
    error = request.GET.get("error", "")
    try :
        auction_listing = AuctionListing.objects.get(pk=listing_id)

        # Inactivate listing if it's past the final date
        if auction_listing.final_date < timezone.now():
            auction_listing.active = False
            auction_listing.save()

        return render(request, "auctions/listing.html", {
            "listing": auction_listing,
            "watched_listings": utils.get_watched_listings(request.user.id),
            "max_bid": utils.find_max_bid(auction_listing),
            "bid_form": Bid_Form(initial={"bid": utils.get_default_bid_value(auction_listing)}),
            "comment_form": Comment_Form(),
            "error": error
        })
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })

@login_required
def edit_listing(request, listing_id):
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })
    if request.method == "POST":
        form = Listing_Form(request.POST)
        if form.is_valid():
            auction_listing.item_name = form.cleaned_data["item_name"]
            auction_listing.description = form.cleaned_data["description"]
            auction_listing.starting_bid = form.cleaned_data["starting_bid"]
            auction_listing.final_date = form.cleaned_data["final_date"]
            auction_listing.image_url = form.cleaned_data["image_url"]
            category_title = form.cleaned_data["category_title"]
            if category_title != "":
                auction_listing.category = Category.objects.get(title=category_title)
            auction_listing.save()
            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
        return render(request, "auctions/create.html", {
                "is_edit": True,
                "listing": auction_listing,
                "form": form,
                "error": form.errors
            })
    return render(request, "auctions/create.html", {
        "is_edit": True,
        "listing": auction_listing,
        "form": Listing_Form(initial={
            "item_name": auction_listing.item_name,
            "description": auction_listing.description,
            "starting_bid": auction_listing.starting_bid,
            "final_date": auction_listing.final_date,
            "image_url": auction_listing.image_url,
            "category_title": auction_listing.category.title if auction_listing.category else ""
        }),
        "categories": Category.objects.all(),
        "error": ""
    })

@login_required
def delete_listing(request, listing_id):
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })
    auction_listing.delete()
    return HttpResponseRedirect(reverse("auctions:self_listings"))

@login_required
def create_bid(request, listing_id):
    if request.method == "POST":
        form = Bid_Form(request.POST)
        if form.is_valid():
            bidder = None
            try :
                bidder = User.objects.get(pk=request.user.id)
            
            except User.DoesNotExist:
                return HttpResponseRedirect(reverse("auctions:logout"))
                
            bid = form.cleaned_data["bid"]
            bid_date = timezone.now()


            auction_listing = None

            try:
                auction_listing = AuctionListing.objects.get(pk=listing_id)
            except AuctionListing.DoesNotExist:
                return render(request, "auctions/listing.html", {
                    "error": "Listing does not exist."
                })
            
            # if bid_date is greater then final_date, return error
            if bid_date > auction_listing.final_date:
                return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )) + "?error=Bid must be placed before the final date.")

            if (auction_listing.current_bid == None and bid >= auction_listing.starting_bid) or (auction_listing.current_bid and bid > auction_listing.current_bid.bid):
                # Create bid
                bid = Bid(bid=bid, bid_date=bid_date, bidder=bidder, auction_listing=auction_listing)
                bid.save()
                auction_listing.current_bid = bid
                auction_listing.save()

                # Put listing in watchlist if it's not there yet
                user = None
                try:
                    user = User.objects.get(pk=request.user.id)
                except User.DoesNotExist:
                    return HttpResponseRedirect(reverse("auctions:logout"))

                watchlist = None
                try:
                    watchlist = Watchlist.objects.get(user=user)
                except Watchlist.DoesNotExist:
                    watchlist = Watchlist(user=user)
                    watchlist.save()
                watchlist.auction_listings.add(auction_listing)
                watchlist.save()
                return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )) + "?error=Bid must be greater than current bid or at least the same of the starting bid, if there is no bid yet.")
            
        try:
            auction_listing = AuctionListing.objects.get(pk=listing_id)
        
            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )) +"?error=There are errors in the form. Please correct them and try again.")
        except AuctionListing.DoesNotExist:
            return render(request, "auctions/listing.html", {
                "error": "Listing does not exist."
            })
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required
def create_comment(request, listing_id):
    if request.method == "POST":
        form = Comment_Form(request.POST)
        if form.is_valid():
            commenter = None
            try :
                commenter = User.objects.get(pk=request.user.id)
            
            except User.DoesNotExist:
                return HttpResponseRedirect(reverse("auctions:logout"))
                
            text = form.cleaned_data["text"]

            auction_listing = None

            try:
                auction_listing = AuctionListing.objects.get(pk=listing_id)
            except AuctionListing.DoesNotExist:
                return render(request, "auctions/listing.html", {
                    "error": "Listing does not exist."
                })

            comment = Comment(text=text, commenter=commenter, auction_listing=auction_listing)
            comment.save()
            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
        try:
            auction_listing = AuctionListing.objects.get(pk=listing_id)
        
            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id, )) + "?error=There are errors in the form. Please correct them and try again.")
        except AuctionListing.DoesNotExist:
            return render(request, "auctions/listing.html", {
                "error": "Listing does not exist."
            })
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required
def put_in_watchlist(request, listing_id):
    auction_listing = None
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })
    user = None
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))
    watchlist = None
    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        watchlist = Watchlist(user=user)
        watchlist.save()
    watchlist.auction_listings.add(auction_listing)
    watchlist.save()
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
    
@login_required
def remove_from_watchlist(request, listing_id):
    # should remove only if user didn't bid
    user = None
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))

    auction_listing = None
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })

    if Bid.objects.filter(bidder=user, auction_listing=listing_id).all().count() > 0:
        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)) + "?error=You can't remove a listing from your watchlist if you already bid on it.")

    watchlist = None
    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))
    
    watchlist.auction_listings.remove(auction_listing)
    watchlist.save()
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required
def close_listing(request, listing_id):
    auction_listing = None
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })
    auction_listing.active = False
    auction_listing.save()
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required
def reopen_listing(request, listing_id):
    auction_listing = None
    try:
        auction_listing = AuctionListing.objects.get(pk=listing_id)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/listing.html", {
            "error": "Listing does not exist."
        })
    auction_listing.active = True
    auction_listing.save()
    return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required
def watchlist(request):
    user = None
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))
    watchlist = None
    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))

    listings = watchlist.auction_listings.all()

    # Check if final date has passed and Remove inactive listings from watchlist
    for listing in listings:
        # check if it is not active
        if not listing.active:
            watchlist.auction_listings.remove(listing)
            watchlist.save()
            continue
            
        if listing.final_date < timezone.now():
            listing.active = False
            listing.save()
            watchlist.auction_listings.remove(listing)
            watchlist.save()

    return render(request, "auctions/watchlist.html", {
        "watched_listings": watchlist.auction_listings.all()
    })

@login_required
def won_listings(request):
    user = None
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse("auctions:logout"))
    won_listings = utils.get_won_listings(user)
    return render(request, "auctions/won_listings.html", {
        "won_listings": won_listings
    })

@login_required
def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

@login_required
def category(request, category_title):
    listings = []

    # filter listings by category title
    for listing in AuctionListing.objects.filter(active=True).all():
        if listing.category and listing.category.title == category_title:
            listings.append(listing)

    return render(request, "auctions/category.html", {
        "category": category_title,
        "listings": listings,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
