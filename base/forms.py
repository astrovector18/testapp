## let's create a form for the Create room 
## Field.
## Our form should have input fields based on those from the Room models.

## import necessary for Field.

from django.forms import ModelForm 
## import the Room class from models.py 

from .models import Room 

class CreateRoom(ModelForm):
  class Meta: 
    model = Room 
    fields = '__all__'