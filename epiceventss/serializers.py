from rest_framework.serializers import ModelSerializer
import rest_framework.serializers as s
from django.contrib.auth.password_validation import validate_password
from . import models
from django.utils import timezone
from datetime import datetime


class UserSerializer(ModelSerializer):
    class Meta:
        model = models.User
        exclude = ("password", "groups", "user_permissions")


class UserListSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "role"]


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "password", "role"]
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def validate_password(self, value):
        validated = validate_password(password=value)
        if validated is None:
            return value

    def validate_role(self, value):
        if value in ["S", "C", "G"]:
            return value
        else:
            raise s.ValidationError("Choisissez un rôle valide (S,C)")

    def create(self, validated_data):
        user = models.User.objects.create(
            username=validated_data['username'],
            role=validated_data["role"]
        )
        user.set_password(validated_data['password'])
        if validated_data["role"] == "G":
            user.is_staff = True
        user.save()
        return user


class ClientSerializer(ModelSerializer):
    sales_contact = UserListSerializer()

    class Meta:
        model = models.Client
        fields = "__all__"


class ClientListSerializer(ModelSerializer):
    class Meta:
        model = models.Client
        fields = ["id", "company_name", "isPotential", "phone", "email", "sales_contact"]


class ContractSerializer(ModelSerializer):
    sales_contact = UserListSerializer()
    client = ClientListSerializer()

    class Meta:
        model = models.Contract
        fields = "__all__"


class ContractListSerializer(ModelSerializer):
    class Meta:
        model = models.Contract
        fields = ["id", "sales_contact", "client", "status", "amount", "payment_due"]

    def validate_client(self, client):
        if client.isPotential is False:
            return client
        else:
            raise s.ValidationError("Le client est encore potentiel!")

    def validate_payment_due(self, value):
        if value > timezone.now():
            return value
        else:
            raise s.ValidationError("Vous ne pouvez pas créer de contrat dont la date de paiement est déjà dépassée")


class EventSerializer(ModelSerializer):
    client = ClientListSerializer()
    support_contact = UserListSerializer()

    class Meta:
        model = models.Event
        fields = "__all__"


class EventListSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = ["id", "client", "support_contact",
                  "event_status", "attendees", "event_date", "notes"]

    def validate_event_status(self, contract):
        if contract.status is True:
            return contract
        else:
            raise s.ValidationError("Le contract n'a pas été signé")

    def validate_event_date(self, value):
        if value > timezone.now():
            return value
        else:
            raise s.ValidationError("Vous ne pouvez pas créer d'évènement dont la date est dépassée")

    def validate_support_contact(self, contact):
        if contact.role == "S":
            return contact
        else:
            raise s.ValidationError("Vous devez ajouter un référent support")
