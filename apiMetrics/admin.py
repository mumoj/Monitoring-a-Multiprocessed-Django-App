from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(API)
admin.site.register(Transaction)
admin.site.register(TransactionStatus)

