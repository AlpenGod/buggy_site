from django.shortcuts import render, get_object_or_404
from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CartForm, QueryForm, SupportForm
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
import os
from django.conf import settings
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus import Spacer, Paragraph
from django.db import connection
import pickle
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from xml.etree.ElementTree import parse

# '/' buggy_site view
def home_view(request):
    return render(request, "index.html",{})

# '/support' template view
class support_view(View):

    def get(self, request, *args, **kwargs):
        return render(request, "support_page.html",{})

    def post(self, request, *args, **kwargs):
        form = SupportForm(request.POST)
        if(form.data['message']==""):
            messages.warning(self.request, "Your message is empty")
            return render(request, "support_page.html",{})
        else:
            BASE_DIR = Path(__file__).resolve().parent.parent
            try:
                file = request.FILES['document']
                path = os.path.join(BASE_DIR, "media", "uploads")
                fs = FileSystemStorage(location = path)
                if fs.exists(file.name):
                    fs.delete(file.name)
                fs.save(file.name, file)
                output = 'output'
                if file.name[-3:]=="txt":
                    try:
                        #harmful!
                        output = str(pickle.load(open(path + "/" + file.name,'rb')))
                    except pickle.UnpicklingError:
                        output = 'Unserializing error'
                elif file.name[-3:]=="xml":
                    with open(path + "/" + file.name) as fh:
                        #harmful!
                        tree = parse(fh) 
                        #lxml <4.6.2 is vulnerable to xss (use &lt; and &gt; instead of < and >)
                    output = ['xml']
                    for node in tree.iter():
                        output.append(node.tag + " " + node.text)
                elif file.name[-3:]=="jpg" or file.name[-3:]=="png":
                    output = '<div><img src="/media/uploads/'+file.name+'"/></div>'
                else:
                    output = "Unsupported file type"
                    fs.delete(file.name)
            except:
                output = "Empty"
            #harmful! .cleaned_data missing
            message = form.data['message']
            context = {
                'file' : output,
                'message' : message,
            }
            return render(request, "support_page.html", context)

# '/search' template view
def search_view(request):
    cursor = connection.cursor()
    if 'query' in request.session:
        name=request.session.pop('query',{})
        name = name[0].upper() + name[1:].lower()
        #harmful!
        cursor.execute("SELECT * from pages_item WHERE title = '" + name +"'")
    row=cursor.fetchone()
    context = {
                'object': row,
                #0 ID
                #1 TITLE
                #2 PRICE
                #3 SLUG
                #4 DESCRIPTION
                #5 IMAGE
            }
    return render(request, "search.html", context)

#main buggy_shop view
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
                    order_item.quantity += form.cleaned_data.get('cart_quantity') - 1
                    order_item.save()
                    messages.info(request, "This item was added to your cart")
            else:
                #if not, create an order
                ordered_date = timezone.now()
                order = Order.objects.create(user=request.user, ordered_date=ordered_date)
                order.items.add(order_item)
                order_item.quantity += form.cleaned_data.get('cart_quantity') - 1
                order_item.save()
                messages.info(request, "This item was added to your cart")
        return redirect("product", slug=slug)

#finalize transaction view
class CheckoutView(LoginRequiredMixin,View):

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
        #get user info to finalize transaction
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

            #for printing items in pdf
            print_items = ''
            for i in range(len(qs)):
                if i==len(qs)-1:
                    print_items = print_items + qs[i].item.title + '.'
                else:
                    print_items =print_items + qs[i].item.title + ', '

            #pdf generator logic for payment confirmation
            textLines=[
            'Payment confirmation',
            ''
            'Thanks, '+ billing_address.first_name+' '+billing_address.last_name+' for trusting us!(xd)',
            'Package will be waiting for you at ' + billing_address.shipping_address + ', ' + 
            shipping_country + '!',
            ''
            'Your credit card info: ',
            'Credit Card Number: ' + number,
            'Expiration: ' + expiration,
            'CVV: ' + cvv,
            "",
            'Items you have bought: ' + print_items,
            'For: ' + str(order.get_total_price())+'$',
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

            #delete completed order
            for order_item in qs:
                order_item.delete()
            order.delete()

            #cuz we don't store unnecessary data!
            billing_address.delete()

            messages.info(self.request, "Success! Your payment confirmation is available on: "+
                request.get_host()+'/media/' + 'f' + str(counter) + '.pdf')
            return redirect("/shop/")

#remove one piece of an item in cart in summary_view
def summary_remove(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order_item.quantity -= 1
            if order_item.quantity == 0:
                order_item.delete()
            else:
                order_item.save()
            messages.info(request, "This item quantity was updated")
        return redirect("order-summary")
    else:
        return redirect('/accounts/login/')

#remove an item in cart in summary_view
def summary_remove_all(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order_item.delete()
            messages.info(request, "This item quantity was updated")
        return redirect("order-summary")
    else:
        return redirect('/accounts/login/')

#ad one piece of an item in cart in summary_view
def summary_add(request, slug):
    if request.user.is_authenticated:
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
        return redirect("order-summary")
    else:
        return redirect('/accounts/login/')

