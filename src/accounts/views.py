from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Customer
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only
# Create your views here.


@unauthenticated_user
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_to_login = authenticate(
            request, username=username, password=password)
        print(user_to_login)
        if user_to_login is not None:
            login(request, user_to_login)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')
    return render(request, 'accounts/login.html', context={})


def logout_view(request):
    logout(request)
    return redirect('login')


@unauthenticated_user
def register_view(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

            # --- ALL BELOW CODE HAS BEEN MOVED TO SIGNALS ---
            # # ---start--- To add user to a group
            # group = Group.objects.get(name='customers')
            # user.groups.add(group)
            # # ---end--- To add user to a group

            # # ---start--- To create customer at the same time
            # Customer.objects.create(
            #     user=user, name="{} {}".format(user.first_name, user.last_name), email=user.email)
            # # ---end--- To create customer at the same time

            username = form.cleaned_data.get('username')
            messages.success(
                request, 'Account has been created for {}'.format(username))
            return redirect('login')
    return render(request, 'accounts/register.html', context={'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['customers'])
def user_page_view(request):
    orders = request.user.customer.order_set.all()
    context = {
        'orders': orders
    }
    return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customers', 'admins'])
def account_settings_view(request):
    form = CustomerForm(instance=request.user.customer)
    if (request.method == 'POST'):
        form = CustomerForm(request.POST or None,
                            files=request.FILES, instance=request.user.customer)
        if form.is_valid():
            form.save()
    context = {
        'form': form
    }
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@admin_only
def home_view(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    fiveOrders = orders[:5]
    delivered_orders_count = Order.objects.filter(status='Delivered').count()
    pending_orders_count = orders.count() - delivered_orders_count
    context = {
        'order_list': fiveOrders,
        'customer_list': customers,
        'total_delivered_orders': delivered_orders_count,
        'total_pending_orders': pending_orders_count
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins'])
def products_view(request):
    context = {
        'product_list': Product.objects.all()
    }
    return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins'])
def customer_view(request, pk):
    customer = Customer.objects.get(id=pk)
    # orders = customer.order_set.all()  # django_filters filter code

    # *** my filter code start***
    orders = None
    my_filter = OrderFilter(request.GET)
    if my_filter.is_valid():
        cleaned_data = my_filter.cleaned_data

        product_field = cleaned_data.get('product')
        status_field = cleaned_data.get('status')
        note_field = cleaned_data.get('note')
        start_date_field = cleaned_data.get('start_date')
        end_date_field = cleaned_data.get('end_date')

        if product_field == None and (status_field == '' or status_field == None) and (note_field == '' or note_field == None) and (start_date_field == None or start_date_field == '') and (end_date_field == None or end_date_field == ''):
            orders = customer.order_set.all()
        else:
            kwargs = {}

            if product_field != None and product_field != '':
                kwargs['product'] = product_field
            if status_field != None and status_field != '':
                kwargs['status'] = status_field
            if note_field != None and note_field != "":
                kwargs['note__icontains'] = note_field
            if start_date_field != None and start_date_field != "":
                kwargs['date_created__gte'] = start_date_field
            if end_date_field != None and end_date_field != "":
                kwargs['date_created__lte'] = end_date_field

            orders = customer.order_set.filter(**kwargs)
    else:
        orders = customer.order_set.all()
    # *** my filter code end***

    # # django_filters filter code
    # my_filter = OrderFilter(request.GET, queryset=orders)
    # orders = my_filter.qs  # django_filters filter code
    context = {
        'customer': customer,
        'order_list': orders,
        'total_orders': orders.count(),
        'my_filter': my_filter
    }
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins'])
def create_order_view(request, pk):
    customer = Customer.objects.get(id=pk)

    OrderFormSet = inlineformset_factory(
        Customer, Order, fields=('product', 'status'), extra=10)  # attributes: extra = for telling how many empty fields to render
    # attributes: queryset = for telling which data to use for filling fields
    formset = OrderFormSet(instance=customer, queryset=Order.objects.none())
    # form = OrderForm(initial={'customer': customer})

    if request.method == 'POST':
        # form = OrderForm(request.POST or None)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {
        'formset': formset
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins'])
def update_order_view(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST or None, instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    context = {
        'formset': form
    }
    return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins'])
def delete_order_view(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context = {
        'order': order
    }
    return render(request, 'accounts/delete.html', context)
