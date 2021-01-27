from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
import os.path
from reportlab.pdfgen import canvas


# Create your models here.

class Item(models.Model):
	title = models.CharField(max_length=100)
	price = models.FloatField()
	slug = models.SlugField()
	description = models.TextField()
	image = models.ImageField()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("product", kwargs={
			'slug':self.slug
			})

	def get_add_to_cart_url(self):
		return reverse("add_to_cart", kwargs={
			'slug':self.slug
			})
	def get_remove_from_cart_url(self):
		return reverse("remove_from_cart", kwargs={
			'slug':self.slug
			})

class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)


	def __str__(self):
		return f"{self.quantity} of {self.item.title}"

	def get_total_item_price(self):
		return round(self.quantity * self.item.price,2)

	def get_final_price(self):
		return self.get_total_item_price()


class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	billing_address=models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

	def __str__(self):
		return self.user.username

	def get_total_price(self):
		total=0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return round(total,2)

	def get_total_quantity(self):
		total=0
		for order_item in self.items.all():
			total += order_item.quantity
		return total

class BillingAddress(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.CharField(max_length=100)
	expiration = models.CharField(max_length=100)
	cvv = models.CharField(max_length=100)
	number = models.CharField(max_length=100)
	shipping_country = CountryField(multiple=False)
	shipping_zip = models.CharField(max_length=100)
	shipping_address = models.CharField(max_length=100)

	def __str__(self):
		return self.user.username

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)
    message = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


