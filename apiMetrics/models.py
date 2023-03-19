from django.db import models
# Create your models here.

class API(models.Model):
    name = models.CharField(max_length=15, unique=True)
    description = models.CharField(max_length=100)
    params = models.JSONField()


class TransactionStatus(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100)


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    api = models.ForeignKey(API, on_delete=models.CASCADE)
    status = models.ForeignKey(TransactionStatus, on_delete=models.CASCADE)



