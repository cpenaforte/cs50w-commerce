from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("self", views.self_listings, name="self_listings"),
    path("listing/create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/edit", views.edit_listing, name="edit_listing"),
    path("listing/<int:listing_id>/delete", views.delete_listing, name="delete_listing"),
    path("listing/<int:listing_id>/bid/create", views.create_bid, name="create_bid"),
    path("listing/<int:listing_id>/comment/create", views.create_comment, name="create_comment"),
    path("listing/<int:listing_id>/watchlist/create", views.put_in_watchlist, name="put_in_watchlist"),
    path("listing/<int:listing_id>/watchlist/delete", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("listing/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/reopen", views.reopen_listing, name="reopen_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("won_listings", views.won_listings, name="won_listings"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_title>", views.category, name="category"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
