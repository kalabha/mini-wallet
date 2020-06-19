from django.urls import path

from wallet import views

urlpatterns = [
    path('wallet/', views.WalletApiView.as_view()),
    path('wallet/deposit/', views.DepositApiView.as_view()),
    path('wallet/withdrawals/', views.WithdrawApiView.as_view()),
    path('init/', views.InitializeWalletApiView.as_view())
]
