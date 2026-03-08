from django.db import models


class UserName(models.Model):
    username = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    host = models.CharField(max_length=155, blank=True, null=True)
    ip_address = models.CharField(max_length=155, blank=True, null=True)

    def __str__(self):
        return self.username


class Compare(models.Model):
    user1 = models.CharField(max_length=64)
    user2 = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    host = models.CharField(max_length=155)
    ip_address = models.CharField(max_length=155)

    def __str__(self):
        return "Compared: %s with %s" %(self.user1, self.user2)
