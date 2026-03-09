"""Gebruikersmodel met 2FA (TOTP) ondersteuning."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager voor het custom User model."""

    def create_user(self, email, naam, password=None, **extra_fields):
        if not email:
            raise ValueError("E-mailadres is verplicht.")
        email = self.normalize_email(email)
        user = self.model(email=email, naam=naam, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, naam, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser moet is_staff=True hebben.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser moet is_superuser=True hebben.")

        return self.create_user(email, naam, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom gebruikersmodel met e-mail als login en 2FA support."""

    class Rol(models.TextChoices):
        PUBLIEK = "publiek", "Publiek"
        AANBOD_RAADPLEGER = "aanbod_raadpleger", "Aanbod-raadpleger"
        GEBRUIK_RAADPLEGER = "gebruik_raadpleger", "Gebruik-raadpleger"
        AANBOD_BEHEERDER = "aanbod_beheerder", "Aanbod-beheerder"
        GEBRUIK_BEHEERDER = "gebruik_beheerder", "Gebruik-beheerder"
        IBD_BEHEERDER = "ibd_beheerder", "IBD-beheerder"
        GT_INKOOP_BEHEERDER = "gt_inkoop_beheerder", "GT Inkoop-beheerder"
        FUNCTIONEEL_BEHEERDER = "functioneel_beheerder", "Functioneel beheerder"

    class Status(models.TextChoices):
        ACTIEF = "actief", "Actief"
        INACTIEF = "inactief", "Inactief"
        WACHT_OP_FIATTERING = "wacht_op_fiattering", "Wacht op fiattering"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="E-mailadres")
    naam = models.CharField(max_length=255, verbose_name="Volledige naam")
    organisatie = models.ForeignKey(
        "organisaties.Organisatie",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gebruikers",
        verbose_name="Organisatie",
    )
    rol = models.CharField(
        max_length=30,
        choices=Rol.choices,
        default=Rol.AANBOD_RAADPLEGER,
        verbose_name="Rol",
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.WACHT_OP_FIATTERING,
        verbose_name="Status",
    )
    totp_enabled = models.BooleanField(default=False, verbose_name="2FA ingeschakeld")
    telefoon = models.CharField(max_length=20, blank=True, verbose_name="Telefoonnummer")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    aangemaakt_op = models.DateTimeField(auto_now_add=True, verbose_name="Aangemaakt op")
    gewijzigd_op = models.DateTimeField(auto_now=True, verbose_name="Gewijzigd op")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["naam"]

    class Meta:
        verbose_name = "Gebruiker"
        verbose_name_plural = "Gebruikers"
        ordering = ["-aangemaakt_op"]

    def __str__(self):
        return f"{self.naam} ({self.email})"

    @property
    def is_beheerder(self):
        """Controleer of gebruiker een beheerrol heeft."""
        return self.rol in [
            self.Rol.AANBOD_BEHEERDER,
            self.Rol.GEBRUIK_BEHEERDER,
            self.Rol.IBD_BEHEERDER,
            self.Rol.GT_INKOOP_BEHEERDER,
            self.Rol.FUNCTIONEEL_BEHEERDER,
        ]

    @property
    def is_functioneel_beheerder(self):
        return self.rol == self.Rol.FUNCTIONEEL_BEHEERDER


class Notificatie(models.Model):
    """Notificatie voor een gebruiker."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificaties", verbose_name="Gebruiker")
    type = models.CharField(max_length=50, verbose_name="Type")
    bericht = models.TextField(verbose_name="Bericht")
    gelezen = models.BooleanField(default=False, verbose_name="Gelezen")
    aangemaakt_op = models.DateTimeField(auto_now_add=True, verbose_name="Aangemaakt op")

    class Meta:
        verbose_name = "Notificatie"
        verbose_name_plural = "Notificaties"
        ordering = ["-aangemaakt_op"]

    def __str__(self):
        return f"[{self.type}] {self.bericht[:50]}"
