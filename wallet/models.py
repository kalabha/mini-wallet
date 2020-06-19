import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


# Create your models here.

class WalletUser(models.Model):
    customer_xid = models.UUIDField(primary_key=True, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owned_by = models.OneToOneField(
        WalletUser,
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(default=False)
    enabled_at = models.DateTimeField()
    disabled_at = models.DateTimeField()
    balance = models.FloatField()


class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deposited_by = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(default=False)
    deposited_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    reference_id = models.UUIDField(unique=True)

class Withdrawal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    withdrawn_by = models.ForeignKey(
        WalletUser,
        on_delete=models.CASCADE,
    )
    status = models.BooleanField(default=False)
    withdrawn_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    reference_id = models.UUIDField(unique=True)