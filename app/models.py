from django.db import models

# Create your models here.


class Contact(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    image = models.ImageField(null=True)

    def __str__(self):
        return self.email


    class Meta:
        ordering = ['id']
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
