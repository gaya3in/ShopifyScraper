from django.db import models

# Create your models here.
WEBTYPE_CHOICES = [
    ('','-----'),
    ("Type1", "Type1"),
    ("Type2", "Type2")
]
class Website(models.Model):
    url = models.URLField(max_length=500)
    title = models.CharField(max_length = 100)
    switch = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    webType = models.CharField(max_length=20,choices=WEBTYPE_CHOICES,default='')

    def __str__(self):
       return self.title

class Endpoint(models.Model):
    url = models.ForeignKey(Website,on_delete=models.CASCADE,null=True,blank=True)
    endpoint = models.URLField(max_length=500)

    def __str__(self):
        return str(self.url)

