from django.db import models

# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=150, verbose_name="标题")
    author = models.CharField(max_length=150)
    price = models.FloatField()

    def __str__(self):
        return self.title



