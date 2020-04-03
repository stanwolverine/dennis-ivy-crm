from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
# from django.dispatch import
from .models import Customer


def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customers')
        instance.groups.add(group)

        print('group added to user.')

        Customer.objects.create(
            user=instance, name="{} {}".format(instance.first_name, instance.last_name), email=instance.email)

        print('customer created.')


post_save.connect(customer_profile, sender=User)
