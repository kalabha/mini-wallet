from django.urls import path, include

from wallet import views

urlpatterns = [
    path('wallet/', views.WalletApiView.as_view()),
    path('wallet/deposit/', views.deposit),
    path('wallet/withdrawals/', views.withdraw),
    path('init/', views.init_wallet)
]
