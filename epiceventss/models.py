from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Gestion = SuperUser
    ROLE_CHOICES = (
        ("G", "Gestion"),
        ("C", "Commercial"),
        ("S", "Support"),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username}"


class Client(models.Model):
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=250, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    sales_contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    isPotential = models.BooleanField()

    def __str__(self):
        if self.isPotential is True:
            return f"{self.company_name}, client potentiel"
        else:
            return f"{self.company_name}, client"


class Contract(models.Model):
    sales_contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='+')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    # je suppose que status = fini ou pas donc True = Fini, False = En cours
    status = models.BooleanField()
    amount = models.FloatField()
    payment_due = models.DateTimeField()

    def __str__(self):
        return f"{self.client.company_name}, {self.amount}, {self.payment_due}"


class Event(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='+')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    support_contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    event_status = models.ForeignKey(Contract, on_delete=models.CASCADE)
    attendees = models.IntegerField()
    event_date = models.DateTimeField()
    notes = models.TextField(blank=True)

    def __str(self):
        return f"{self.client.company_name}, {self.event_date}, {self.attendees}, {self.event_status.status}"

# phpsgresql
# image
