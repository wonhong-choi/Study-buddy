from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) # if null is True, black(null) allowed for DataBase, if blak is True, blank allowed for FORM
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) # whenever call SAVE(), this field will be changed.
    created = models.DateTimeField(auto_now_add=True) # when first call SAVE(), this field will be generated. 그 이후, SAVE()할 때 안 변함
    
    
    class Meta:
        ordering = ['-updated', '-created'] # if doesn't have '-' > ASC, else > DESC
    
    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # when user deleted.
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # when parent(Room) deleted, what you want to do with children? == on_delete
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) # whenever call SAVE(), this field will be changed.
    created = models.DateTimeField(auto_now_add=True) # when first call SAVE(), this field will be generated. 그 이후, SAVE()할 때 안 변함
    
    class Meta:
        ordering = ['-updated', '-created'] # if doesn't have '-' > ASC, else > DESC
    
    def __str__(self):
        return self.body[:50]
    