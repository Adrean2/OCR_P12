from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .permissions import ContractPermission, ClientPermission, EventPermission, IsAdminAuthenticated
from . import serializers
from . import models


class Users(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAdminAuthenticated]
    serializer_class = serializers.UserListSerializer

    def get_queryset(self):
        queryset = models.User.objects.all()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def retrieve(self, request, pk=None, **kwargs):
        queryset = models.User.objects.get(id=pk)
        serializer = serializers.UserSerializer(queryset, many=False)
        return Response(serializer.data)


class Client(viewsets.ModelViewSet):
    permission_classes = [ClientPermission]
    serializer_class = serializers.ClientListSerializer
    queryset = models.Client.objects.all()

    def retrieve(self, request, pk=None, **kwargs):
        queryset = models.Client.objects.get(id=pk)
        serializer = serializers.ClientSerializer(queryset, many=False)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if "sales_contact" not in serializer.validated_data:
            serializer.save(sales_contact=self.request.user)
        return Response(serializer.data)


class Contract(viewsets.ModelViewSet):
    permission_classes = [ContractPermission]
    serializer_class = serializers.ContractListSerializer
    queryset = models.Contract.objects.all()

    def retrieve(self, request, pk=None, **kwargs):
        queryset = models.Contract.objects.get(id=pk)
        serializer = serializers.ContractSerializer(queryset, many=False)
        return Response(serializer.data)


class Event(viewsets.ModelViewSet):
    permission_classes = [EventPermission]
    serializer_class = serializers.EventListSerializer
    queryset = models.Event.objects.all()

    def perform_create(self, serializer):
        if "support_contact" not in serializer.validated_data:
            serializer.save(support_contact=self.request.user)

    def retrieve(self, request, pk=None, **kwargs):
        queryset = models.Event.objects.get(id=pk)
        serializer = serializers.EventSerializer(queryset, many=False)
        return Response(serializer.data)


class Signup(viewsets.ModelViewSet):
    permission_classes = [IsAdminAuthenticated]
    serializer_class = serializers.SignUpSerializer
    queryset = models.User.objects.all()
