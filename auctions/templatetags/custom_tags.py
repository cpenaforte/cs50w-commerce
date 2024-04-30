from django import template

register = template.Library()

@register.filter
def is_in_list(value, given_list):
    return True if value in given_list else False

@register.filter
def format_money(value):
    return f"${value}"

@register.filter
def sort_by_bid(bids):
    return sorted(bids, key=lambda bid: bid.bid, reverse=True)
