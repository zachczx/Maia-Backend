from core.models import Customer
from core.serializers import CustomerSerializer
from rest_framework.exceptions import ValidationError
from django.db.models import Q

def get_all_customers():
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return serializer.data

def create_customer(data):
    if check_customer_exists(data.get('first_name'), 
                             data.get('last_name'), 
                             data.get('phone_number'), 
                             data.get('country_code'), 
                             data.get('email'))['exists']:
        raise ValidationError({'error': 'Customer already exists'})
    
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        raise ValidationError(serializer.errors)

def get_customer_by_id(customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer)
        return serializer.data
    except Customer.DoesNotExist:
        raise ValidationError({'error': 'Customer not found'})
    
def get_customer_by_email(email):
    try:
        customer = Customer.objects.get(email=email)
        serializer = CustomerSerializer(customer)
        return serializer.data
    except Customer.DoesNotExist:
        raise ValidationError({'error': 'Customer not found'})

def get_customer_by_phone_number(phone_number):
    try:
        customer = Customer.objects.get(phone_number=phone_number)
        serializer = CustomerSerializer(customer)
        return serializer.data
    except Customer.DoesNotExist:
        raise ValidationError({'error': 'Customer not found'})

def update_customer(customer_id, data):
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer, data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise ValidationError(serializer.errors)
    except Customer.DoesNotExist:
        raise ValidationError({'error': 'Customer not found'})

def delete_customer(customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()
        return {'status': 'deleted'}
    except Customer.DoesNotExist:
        raise ValidationError({'error': 'Customer not found'})

def check_customer_exists(first_name, last_name, country_code, phone_number, email):
    try:
        customer = Customer.objects.get(
            Q(first_name__iexact=first_name) &
            Q(last_name__iexact=last_name) &
            Q(phone_number=phone_number) &
            Q(country_code=country_code) &
            Q(email__iexact=email)
        )
        return {
            'exists': True,
            'customer': CustomerSerializer(customer).data,
            'message': 'Customer exists'
        }
    except Customer.DoesNotExist:
        return {
            'exists': False,
            'message': 'Customer not found with the given details'
        }
