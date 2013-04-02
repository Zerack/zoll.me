'''
James D. Zoll

4/1/2013

Purpose: Defines database models for the Files application

License: This is a public work.

'''

# Library Imports
from django.db import models
from django.contrib.auth.models import User

# The Group model holds information about File Uploader "Groups"
class Group(models.Model):
    group = models.CharField(max_length=20)

# This keys to Django users and tells us who is in what group for this application
class Group_Member(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)

# This holds the actual file information itself.
class File(models.Model):
    uploaded_file = models.FileField(upload_to='files/%Y/%m/%d')
    display_path = models.CharField(max_length=100)
    date = models.DateTimeField()
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)