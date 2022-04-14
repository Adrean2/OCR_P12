from rest_framework.serializers import ModelSerializer
import rest_framework.serializers as s
from django.contrib.auth.password_validation import validate_password
from . import models


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
        if value not in ["S,C"]:
            raise s.ValidationError("Choisissez un rôle valide (S,C)")
        return value

    def create(self, validated_data):
        user = models.User.objects.create(
            username=validated_data['username'],
            role=validated_data["role"]
        )
        user.set_password(validated_data['password'])
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
