from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .permissions import isSales, isSupport, isGestion
from . import serializers
from . import models


class Users(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()


class Client(viewsets.ModelViewSet):
    serializer_class = serializers.ClientSerializer
    queryset = models.Client.objects.all()


class Contract(viewsets.ModelViewSet):
    serializer_class = serializers.ContractSerializer
    queryset = models.Contract.objects.all()


class Event(viewsets.ModelViewSet):
    permission_classes = [isSales]
    serializer_class = serializers.EventSerializer
    queryset = models.Event.objects.all()


class Signup(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.SignUpSerializer
    queryset = models.User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({f"L'utilisateur a bien été créé"}, status=status.HTTP_201_CREATED, headers=headers)
