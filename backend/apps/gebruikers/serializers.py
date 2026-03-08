"""Serializers voor gebruikers en notificaties."""
from rest_framework import serializers

from .models import Notificatie, User


class UserPublicSerializer(serializers.ModelSerializer):
    """Publieke weergave (voor andere gebruikers)."""
    class Meta:
        model = User
        fields = ["id", "naam", "organisatie", "rol"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Eigen profiel weergave."""
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    organisatie_naam = serializers.CharField(source="organisatie.naam", read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            "id", "email", "naam", "telefoon",
            "organisatie", "organisatie_naam",
            "rol", "rol_display", "status", "status_display",
            "totp_enabled", "aangemaakt_op",
        ]
        read_only_fields = [
            "id", "email", "rol", "status", "totp_enabled", "aangemaakt_op",
        ]


class UserRegistratieSerializer(serializers.ModelSerializer):
    """Serializer voor gebruikersregistratie."""
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "naam", "telefoon", "organisatie", "password", "password_confirm"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Wachtwoorden komen niet overeen."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.status = User.Status.WACHT_OP_FIATTERING
        user.save()
        return user


class NotificatieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificatie
        fields = ["id", "type", "bericht", "gelezen", "aangemaakt_op"]
        read_only_fields = ["id", "type", "bericht", "aangemaakt_op"]
