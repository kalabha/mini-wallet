from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from wallet.models import WalletUser, Wallet, Deposit, Withdrawal
from wallet.response import response, SUCCESS, FAILED
from wallet.serializers import (
    WalletInitSerializer,
    WalletEnabledSerializer,
    WalletDisableSerializer,
    WalletDisabledSerializer,
    WalletTransaction,
    DepositSerializer,
    WithdrawalSerializer,
)


class WalletApiView(APIView):
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        wallet = Wallet.objects.get(owned_by__user=request.user)
        if wallet.status:
            wallet_serializer = WalletEnabledSerializer(instance=wallet)
            return response(SUCCESS, wallet_serializer.data, status.HTTP_200_OK)
        return response(SUCCESS, {"error": "Disabled"}, status.HTTP_404_NOT_FOUND)

    def post(self, request):
        wallet = Wallet.objects.get(owned_by__user=request.user)
        if not wallet.status:
            wallet.status = True
            wallet.enabled_at = timezone.now()
            wallet.save()
            wallet_serializer = WalletEnabledSerializer(instance=wallet)
            return response(SUCCESS, wallet_serializer.data, status.HTTP_201_CREATED)
        return response(
            SUCCESS, {"error": "Already enabled"}, status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        serializer = WalletDisableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data["is_disabled"]:
            return response(
                FAILED,
                {"error": "is_disabled should be true"},
                status.HTTP_400_BAD_REQUEST,
            )
        wallet = Wallet.objects.get(owned_by__user=request.user)
        wallet.status = False
        wallet.disabled_at = timezone.now()
        wallet.save()
        wallet_serializer = WalletDisabledSerializer(instance=wallet)
        return response(SUCCESS, wallet_serializer.data, status.HTTP_200_OK)


class InitializeWalletApiView(APIView):
    @transaction.atomic
    def post(self, request):
        serializer = WalletInitSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data["customer_xid"]
            )
            token, created = Token.objects.get_or_create(user=user)
            wallet_user = WalletUser.objects.create(
                user=user, customer_xid=serializer.validated_data["customer_xid"]
            )
            Wallet.objects.create(
                owned_by=wallet_user, status=True, enabled_at=timezone.now(), balance=0.0
            )
            return response(SUCCESS, {"token": token.key}, status.HTTP_201_CREATED)
        return response(FAILED, serializer.errors, status.HTTP_400_BAD_REQUEST)


class DepositApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = WalletTransaction(data=request.data)
        if serializer.is_valid():
            wallet = Wallet.objects.select_for_update().get(owned_by__user=request.user)
            if wallet.status:
                deposit_trx = Deposit.objects.create(
                    deposited_by=wallet.owned_by, status=True, **serializer.validated_data
                )
                wallet.balance += deposit_trx.amount
                wallet.save()
                return response(
                    SUCCESS,
                    DepositSerializer(instance=deposit_trx).data,
                    status.HTTP_201_CREATED,
                )
            return response(FAILED, {"error": "disabled"}, status.HTTP_404_NOT_FOUND)
        return response(FAILED, {"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class WithdrawApiView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        serializer = WalletTransaction(data=request.data)
        if serializer.is_valid():
            wallet = Wallet.objects.select_for_update().get(owned_by__user=request.user)
            if wallet.status:
                if wallet.balance < serializer.validated_data["amount"]:
                    return response(
                        FAILED, {"error": "not enough balance"}, status.HTTP_204_NO_CONTENT
                    )
                withdraw_trx = Withdrawal.objects.create(
                    withdrawn_by=wallet.owned_by, status=True, **serializer.validated_data
                )
                wallet.balance -= withdraw_trx.amount
                wallet.save()
                return response(
                    SUCCESS,
                    WithdrawalSerializer(instance=withdraw_trx).data,
                    status.HTTP_201_CREATED,
                )
            return response(FAILED, {"error": "disabled"}, status.HTTP_404_NOT_FOUND)
        return response(FAILED, {"errors": serializer.errors}, status.HTTP_400_BAD_REQUEST)
