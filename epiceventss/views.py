from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .permissions import ContractPermission, ClientPermission, EventPermission, IsAdminAuthenticated
from . import serializers
from . import models
from datetime import datetime


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

    # Permet de filter le queryset en fonction du rôle de l'utilisateur
    def role_queryset(self):
        if self.request.user.role == "C":
            return models.Client.objects.filter(sales_contact=self.request.user)
        elif self.request.user.role == "S":
            events = models.Event.objects.filter(support_contact=self.request.user)
            clients = [event.client.id for event in events]
            return models.Client.objects.filter(id__in=clients)
        else:
            return models.Client.objects.all()

    # Permet de gérer les paramètres de filtrage
    def get_queryset(self):
        queryset = self.role_queryset()
        name = self.request.query_params.get("name")
        email = self.request.query_params.get("email")
        if name:
            queryset = models.Client.objects.filter(company_name=name)
        elif email:
            queryset = models.Client.objects.filter(email=email)

        return queryset

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

    def role_queryset(self):
        if self.request.user.role == "C":
            return models.Contract.objects.filter(sales_contact=self.request.user)
        elif self.request.user.role == "S":
            events = models.Event.objects.filter(support_contact=self.request.user)
            contract = [event.event_status.id for event in events]
            return models.Contract.objects.filter(id__in=contract)
        else:
            return models.Client.objects.all()

    def get_queryset(self):
        queryset = self.role_queryset()
        q_param = [param for param in self.request.query_params]
        if q_param and len(q_param) <= 1:
            try:
                param_data = self.request.query_params.get(q_param[0])
                if not param_data:
                    raise ValueError("Inscrivez une valeur")
            except ValueError:
                return queryset

            if "name" in q_param:
                queryset = models.Contract.objects.filter(client__company_name=param_data)
            elif "email" in q_param:
                queryset = models.Contract.objects.filter(client__email=param_data)
            elif "date" in q_param:
                queryset = models.Contract.objects.filter(payment_due=datetime.strptime(param_data, "%Y-%m-%d"))
            elif "amount" in q_param:
                queryset = models.Contract.objects.filter(amount=param_data)

        return queryset

    def retrieve(self, request, pk=None, **kwargs):
        queryset = models.Contract.objects.get(id=pk)
        serializer = serializers.ContractSerializer(queryset, many=False)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if "sales_contact" not in serializer.validated_data:
            serializer.save(sales_contact=self.request.user)
        return Response(serializer.data)


class Event(viewsets.ModelViewSet):
    permission_classes = [EventPermission]
    serializer_class = serializers.EventListSerializer

    # Permet de filter le queryset en fonction du rôle de l'utilisateur

    def role_queryset(self):
        if self.request.user.role == "C":
            return models.Client.objects.all()
        if self.request.user.role == "S":
            events = models.Event.objects.filter(support_contact=self.request.user)
            return events

    def get_queryset(self):
        queryset = self.role_queryset()
        q_param = [param for param in self.request.query_params]
        if q_param and len(q_param) <= 1:
            try:
                param_data = self.request.query_params.get(q_param[0])
                if not param_data:
                    raise ValueError("Inscrivez une valeur")
            except ValueError:
                return queryset

            if "name" in q_param:
                queryset = models.Event.objects.filter(client__company_name=param_data)
            elif "email" in q_param:
                queryset = models.Event.objects.filter(client__email=param_data)
            elif "date" in q_param:
                queryset = models.Event.objects.filter(event_date=datetime.strptime(param_data, "%Y-%m-%d"))

        return queryset

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
