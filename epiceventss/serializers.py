from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from . import models


class UserSerializer(ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username", "id", "role"]


class ClientSerializer(ModelSerializer):
    class Meta:
        model = models.Client
        fields = "__all__"


class ContractSerializer(ModelSerializer):
    class Meta:
        model = models.Contract
        fields = "__all__"


class EventSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = "__all__"


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

    def create(self, validated_data):
        user = models.User.objects.create(
            username=validated_data['username'],
            role=validated_data["role"]
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
