from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .permissions import ContractPermission, ClientPermission, EventPermission, IsAdminAuthenticated, IsGestion
from . import serializers
from . import models
from datetime import datetime
from django.utils import timezone


class Users(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsGestion | IsAdminAuthenticated]
    serializer_class = serializers.UserListSerializer

    def get_queryset(self):
        queryset = models.User.objects.all()
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)
        return queryset


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
            clients = models.Client.objects.filter(sales_contact=self.request.user)
            events = [client for client in clients]
            return models.Event.objects.filter(client__in=events)
        if self.request.user.role == "S":
            events = models.Event.objects.filter(support_contact=self.request.user)
            return events

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # Vérifie si l'évènement est dépassé
        if instance.event_date > timezone.now():
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response(data={"erreur": "Vous ne pouvez pas modifier un évènement est dépassé"}, status=400)

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


class Signup(viewsets.ModelViewSet):
    permission_classes = [IsGestion]
    serializer_class = serializers.SignUpSerializer
    queryset = models.User.objects.all()

