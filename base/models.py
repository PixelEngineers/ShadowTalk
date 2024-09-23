from django.db import models
from django.contrib.auth.models import User
# Create your models here.
# database tables
class Topic(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name= models.CharField(max_length=200)
    description= models.TextField(null=True, blank=True)# can be blank
    participants= models.ManyToManyField(User,related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) #time on every time save is clicked
    created = models.DateTimeField(auto_now_add=True) # only takes time stamps only when the room is created 
    #id= models.UUIDField()

    class Meta:
        ordering = ['-updated','-created']


    def __str__(self):
        return str(self.name) 
    





class Message(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    room= models.ForeignKey(Room,on_delete=models.CASCADE)
    body=models.TextField()
    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated','-created']


    def __str__(self):
        return self.body[:50] 


