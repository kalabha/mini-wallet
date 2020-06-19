from rest_framework import serializers

from wallet.models import Wallet, Deposit, Withdrawal


class WalletInitSerializer(serializers.Serializer):
    customer_xid = serializers.UUIDField(required=True)


class WalletDisableSerializer(serializers.Serializer):
    is_disabled = serializers.BooleanField(required=True)


class WalletEnabledSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        exclude = ("disabled_at",)

    def get_status(self, obj):
        if obj.status:
            return "enabled"
        return "disabled"


class WalletDisabledSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        exclude = ("enabled_at",)

    def get_status(self, obj):
        if obj.status:
            return "enabled"
        return "disabled"


class WalletTransaction(serializers.Serializer):
    amount = serializers.FloatField()
    reference_id = serializers.UUIDField()


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = "__all__"


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = "__all__"
