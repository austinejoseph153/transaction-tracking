from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=50, verbose_name="first name")
    last_name = models.CharField(max_length=50, verbose_name="last name")
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50,unique=True)
    country = models.CharField(max_length=50, verbose_name="country")
    city = models.CharField(max_length=50, verbose_name="city")
    state = models.CharField(max_length=50, verbose_name="state")
    address = models.CharField(max_length=255, verbose_name="address")
    password = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True, verbose_name="is active")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="date joined")

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        verbose_name = "Registered user"
        verbose_name_plural = "Registered users"
        ordering = ['username']
