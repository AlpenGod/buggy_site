from django import template
from pages.models import Order,OrderItem

register = template.Library()

#sums total item quantity at navbar
@register.filter
def cart_item_count(user):
	if user.is_authenticated:
		total=0
		qs = OrderItem.objects.filter(user=user, ordered=False)
		for order_item in qs:
			total += order_item.quantity
		return total
	return 0