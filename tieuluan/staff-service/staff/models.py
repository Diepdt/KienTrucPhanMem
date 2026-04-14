from django.db import models
import hashlib, os

class Staff(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, default='staff',
                            choices=[('staff', 'Staff'), ('senior_staff', 'Senior Staff')])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        return self.password == hashlib.sha256(raw_password.encode()).hexdigest()

    def __str__(self):
        return f"{self.name} ({self.email})"


class StaffToken(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='token')
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key():
        return hashlib.sha256(os.urandom(32)).hexdigest()

    def __str__(self):
        return f"Token for {self.staff.email}"
