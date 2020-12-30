from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from .models import Item, OrderItem, Order, BillingAddress, Message
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CartForm, QueryForm, SupportForm
from pages.templatetags import cart_template_tags
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen.canvas import Canvas
import os
from django.conf import settings
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus import Spacer, Paragraph
from django.db import connection, transaction
from django.utils.safestring import mark_safe


# Create your views here.

# '/' page view
def home_view(request):
    return render(request, "index.html",{})

def xxe_view(request):
    return render(request, "xxe.html",{})
'''
#test and with xss page view
def xss_view(request):
    try:
        messages = Message.objects.all()
        context = {
                    'object': mark_safe(messages)
                }
        print(context)
        if request.method == 'POST':
            form = SupportForm(request.POST)
            name = form.data['name']
            message = form.data['message']
            message_model = Message(
                user=request.user,
                name = name,
                message = message,
                )
            message_model.save()
            print(message_model)
            print(name)
            print(message)
            return render(request, "xss.html",context)
        return render(request, "xss.html",context)
    except:
        print('a')
        return render(request, "xss.html",{})
'''
class xss_view(ListView):

    #model = Message
    template_name = "xss.html"
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        form = SupportForm(request.POST)
        message = form.data['message']
        message_model = Message(
            user=request.user,
            message = message,
            )
        message_model.save()
        return redirect('/xss/')

# '/support/' page view
class support_view(LoginRequiredMixin, ListView):
    template_name = "support.html"

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(user=user)

    def post(self, request, *args, **kwargs):
        form = SupportForm(request.POST)
        message = form.data['message']
        message_model = Message(
            user=request.user,
            message = message,
            )
        message_model.save()
        return redirect('/support/')

def search_view(request):
    cursor = connection.cursor()
    if 'query' in request.session:
        name=request.session.pop('query',{})
        cursor.execute("SELECT * from pages_item WHERE title = '" + name +"'")
    row=cursor.fetchone()
    context = {
                'object': row,
                #0 ID
                #1 TITLE
                #2 PRICE
                #3 CATEGORY
                #4 LABEL
                #5 SLUG
                #6 DESCRIPTION
                #7 IMAGE
            }
    return render(request, "search.html", context)
    #else:
    #    return render(request, "search.html")

#main shop view
class HomeView(ListView):
    model = Item
    template_name = "home-page.html"

    def post(self, request, *args, **kwargs):
        form = QueryForm(request.POST)
        if form.is_valid():
            request.session['query'] = form.cleaned_data.get('query')
        return redirect('/search/')

#open current order view, redirect if cart is empty
class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'order_summary.html', context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("/shop/")

#specific product view, add to cart logic from post
class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

    def post(self, request, slug, *args, **kwargs):
        if 'buy' in request.POST:
            form = CartForm(request.POST)
            if form.is_valid():
                item = get_object_or_404(Item, slug=slug)
                order_item, created = OrderItem.objects.get_or_create(
                item=item,
    			user=request.user,
    			ordered=False
    			)
                order_qs = Order.objects.filter(user=request.user, ordered=False)
                if order_qs.exists():
                    order = order_qs[0]
    				#check if the order item is in the order
                    if order.items.filter(item__slug=item.slug).exists():
                        order_item.quantity += form.cleaned_data.get('cart_quantity')
                        order_item.save()
                        messages.info(request, "This item quantity was updated")
                    else:
                        order.items.add(order_item)
                        messages.info(request, "This item was added to your cart")
                        return redirect("product", slug=slug)
                else:
                    ordered_date = timezone.now()
                    order = Order.objects.create(user=request.user, ordered_date=ordered_date)
                    order.items.add(order_item)
                    messages.info(request, "This item was added to your cart")
                return redirect("product", slug=slug)
            else:
                return redirect("product", slug=slug)
        if 'check' in request.POST:
            return redirect("product", slug=slug)

#finalise transaction view
class CheckoutView(View):

    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order_qs = Order.objects.filter(user=self.request.user, ordered=False)
        if order_qs.exists():
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
				'form':form,
				'object': order
            }
            return render(self.request, "checkout-page.html", context)
        else:
            messages.warning(self.request, "You do not have an active order")
            return redirect('/shop/')

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        order = Order.objects.get(user=self.request.user, ordered=False)
        if form.is_valid():
            shipping_address = form.cleaned_data.get('shipping_address')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            expiration = form.cleaned_data.get('expiration')
            cvv = form.cleaned_data.get('cvv')
            number = form.cleaned_data.get('number')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')
            billing_address = BillingAddress(
				user=self.request.user,
				first_name = first_name,
				last_name = last_name,
				email = email,
				expiration = expiration,
				cvv = cvv,
				number = number,
				shipping_country = shipping_country,
				shipping_zip = shipping_zip,
				shipping_address = shipping_address,
			)
            billing_address.save()
            order.billing_address=billing_address
            qs = OrderItem.objects.filter(user=self.request.user, ordered=False)
            
            for order_item in qs:
                order_item.delete()
            order.delete()

            #pdf logic
            textLines=[
            'Payment confirmation',
            'Thanks, '+ billing_address.first_name+' '+billing_address.last_name+' for trusting us!',
            'Package will be waiting for you at ' + billing_address.shipping_address +'!'
            ]
            counter = 0
            path = os.path.join(settings.BASE_DIR, 'media', 'f' + str(counter) + '.pdf')
            while os.path.isfile(path):
                counter += 1
                path = os.path.join(settings.BASE_DIR, 'media', 'f' + str(counter) + '.pdf')
            doc = SimpleDocTemplate(path)
            Story = [Spacer(1,2*inch)]
            for line in textLines:
	            p = Paragraph(line)
	            Story.append(p)
	            Story.append(Spacer(1,0.2*inch))
            doc.build(Story)
            return redirect('/media/' + 'f' + str(counter) + '.pdf')

            billing_address.delete()


