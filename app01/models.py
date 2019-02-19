from django.db import models

# Create your models here.


class Province(models.Model):
    province_name = models.CharField(max_length=150)
    capital_city = models.CharField(max_length=150)

    def __str__(self):
        return self.province_name


class City(models.Model):
    city_name = models.CharField(max_length=150)
    population = models.IntegerField()
    rank = models.IntegerField()
    province = models.ForeignKey(to=Province,default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name


