from django.urls import path, include

from wallet import views

urlpatterns = [
    path('wallet/', views.WalletApiView.as_view()),
    path('wallet/deposit/', views.Deposit.as_view()),
    path('wallet/withdrawals/', views.Withdraw.as_view()),
    path('init/', views.init_wallet)
]
