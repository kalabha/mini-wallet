from django.contrib import admin

# Register your models here.
from wallet.models import Wallet, WalletUser

admin.site.register(Wallet)
admin.site.register(WalletUser)
