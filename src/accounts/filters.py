import django_filters
from django import forms
from django_filters import DateFilter, CharFilter
from .models import Product, Order, Customer


# class OrderFilter(django_filters.FilterSet):
#     start_date = DateFilter(field_name="date_created", lookup_expr='gte')
#     end_date = DateFilter(field_name="date_created", lookup_expr='lte')
#     note = CharFilter(field_name="note", lookup_expr='icontains')

#     class Meta:
#         model = Order
#         fields = '__all__'
#         exclude = ['customer', 'date_created']


class OrderFilter(forms.ModelForm):
    # customer = forms.ModelChoiceField(
    #     queryset=Customer.objects.all(), required=False)

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), required=False)

    status = forms.ChoiceField(choices=(
        ('', '--------'),
        ('Pending', 'Pending'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered')
    ), required=False)

    note = forms.CharField(required=False)

    start_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'placeholder': "MM/DD/YYYY"}))

    end_date = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'placeholder': "MM/DD/YYYY"}))

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['customer']
