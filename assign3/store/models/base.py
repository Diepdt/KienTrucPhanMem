"""
Base Models - Abstract base classes for the bookstore application.
Contains: TimeStampedModel, Person
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating created_at and updated_at fields.
    All models that need timestamp tracking should inherit from this class.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Person(models.Model):
    """
    Abstract base class for person-related models (Customer, Staff, etc.).
    Provides common fields: name, email, phone.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
