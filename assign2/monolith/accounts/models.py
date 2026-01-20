from django.db import models

class Customer(models.Model):
    # Theo yêu cầu: id, name, email, password [cite: 84]
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255) # Lưu ý: Bài tập này đang lưu password thường, thực tế cần mã hóa.

    def __str__(self):
        return self.name