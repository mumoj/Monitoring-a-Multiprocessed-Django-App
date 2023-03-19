import os
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()

from apiMetrics.models import *


STATUSES = ['TimedOut', 'Pending', 'Processing', 'Processed', 'Failed']

def get_status():
    status = TransactionStatus.objects.get_or_create(name = random.choice(STATUSES))[0]
    status.description = status.name
    status.save()
    return status

def apis():
    if not API.objects.count() == 2:
        API.objects.create(name="Mpesa Express", description="Mpesa Express", params= {})
        API.objects.create(name = "Mpesa B2C", description="Mpesa B2C", params={})
    else:
        return API.objects.all()
    
def populate(n=50):
    _apis = apis()
    print('Populating ...')
    for i in range(50):
        Transaction.objects.create(amount=random.randint(11100,99999)/100,
                api=random.choice(_apis),
                status = get_status()
            )
        
    print('DB Populated')


if __name__ == "__main__":
    populate()
    


