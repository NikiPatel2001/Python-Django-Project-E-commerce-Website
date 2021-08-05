from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from .models import Product, Contact, Orders, OrderUpdate, Customer
from math import ceil
import json
from django.views import View


# print(make_password('1234'))
# print(check_password('1234','pbkdf2_sha256$180000$EIjQMtCWnOES$bnx3Zv9twg9RnzqAdHZas1g3b0nSVlhFnbFqxzZCH6g='))

class Login(View):
    def get(self, request):
        return render(request, 'shop/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                return redirect('ShopHome')
            else:
                error_message = "Email or Password are invalid !!"
        else:
            error_message = "Email or Password Invalid !!"
        print(email, password)
        print('You Are : ', request.session.get('email'))
        return render(request, 'shop/login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    
    return redirect('Login')


class Signup(View):

    def get(self, request):
        return render(request, 'shop/signup.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        confirmpass = postData.get('password2')

        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None
        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password, confirmpass=confirmpass)

        error_message = self.validateCustomer(customer)

        # saving-----------
        if not error_message:
            print(first_name, last_name, phone, email, password, confirmpass)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('ShopHome')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'shop/signup.html', data)

    def validateCustomer(self, customer):
        error_message = None
        if not customer.first_name:
            error_message = "First Name Required !!"
        elif len(customer.first_name) < 3:
            error_message = "First Name Must Be 3 Character Long"
        elif not customer.last_name:
            error_message = "Last Name Requires !!"
        elif len(customer.last_name) < 3:
            error_message = "Last Name Must Be 3 Character Long"
        elif not customer.phone:
            error_message = "Phone Number Required !!"
        elif len(customer.phone) < 10:
            error_message = "Phone Number Must Be 10 Digit Long"
        elif not customer.email:
            error_message = "Email Required !!"
        elif len(customer.email) < 11:
            error_message = "Email Must Be 11 Digit Long"
        elif not customer.password:
            error_message = "Password Required !!"
        elif len(customer.password) < 8:
            error_message = "Password Must Be 8 Character Long"
        elif customer.password != customer.confirmpass:
            error_message = "Password can't match"
        elif customer.isExists():
            error_message = 'Email Address Already Registered..'

        return error_message


def index(request):
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods': allprods}

    print('You Are : ', request.session.get('email'))
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    ''' Return true only if query matches the item '''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods': allprods, 'msg': ""}
    if len(allprods) == 0 or len(query) < 4:
        params = {'msg': "Please Make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', ' ')
        email = request.POST.get('email', ' ')
        phone = request.POST.get('phone', ' ')
        desc = request.POST.get('desc', ' ')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', ' ')
        email = request.POST.get('email', ' ')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json},
                                          default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error.."}')
    return render(request, 'shop/tracker.html')


def productview(request, myid):
    # Fatch the product using id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/productview.html', {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', ' ')
        name = request.POST.get('name', ' ')
        amount = request.POST.get('amount', ' ')
        email = request.POST.get('email', ' ')
        address = request.POST.get('address1', ' ') + " " + request.POST.get('address2', ' ')
        city = request.POST.get('city', ' ')
        state = request.POST.get('state', ' ')
        zip_code = request.POST.get('zip_code', ' ')
        phone = request.POST.get('phone', ' ')
        order = Orders(items_json=items_json, name=name, amount=amount, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order Has Been Placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
    return render(request, 'shop/checkout.html')

def gallary(request):
    return render(request, 'shop/gallary.html')