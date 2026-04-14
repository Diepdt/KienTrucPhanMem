from django.db import models
import hashlib, os

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        return self.password == hashlib.sha256(raw_password.encode()).hexdigest()

    def __str__(self):
        return self.name


class CustomerToken(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='token')
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key():
        return hashlib.sha256(os.urandom(32)).hexdigest()
