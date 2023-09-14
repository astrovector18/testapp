from django.shortcuts import render , redirect
from django.http import HttpResponse 
from .models import Room , Topic , Message
from .forms import CreateRoom 
from django.contrib import messages 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
# A function for searching the database
from django.db.models import Q

# rooms= [
#   {"id":1,"name":"Computer science"},
#   {"id":2 , "name": "Data science"},
#   {"id":3 , "name":"React.Js"}
# ]



def home(request):
  q = request.GET.get('q') if request.GET.get('q') != None else ""
    # double underscore
## filtering by host , title , description
  rooms = Room.objects.filter(Q( topic__title__icontains=q) |
   Q( name__icontains=q)  |
   Q(desc__icontains=q) |
   Q(host__username__icontains = q)) 
  topics = Topic.objects.all() 
  len_rooms = rooms.count()
  context = {'rooms':rooms ,'topics':topics ,'len_rooms':len_rooms}
  return render(request ,"base/home.html" ,context) 
  
#@login_required(login_url='login')
def room(request,pk): 
  room = Room.objects.get(id=pk) 
  ## Getting all the children 
  room_messages  = room.message_set.all() 
  participants = room.participants.all()
  if request.method == "POST":
    messages = Message.objects.create(
       user = request.user ,
       room = room ,
       body = request.POST['body']
      )
    room.participants.add( 
        request.user
        )
    return redirect('room',pk=room.id)
      
  context = { 
    'room':room ,
    'room_messages': room_messages,
    'participants':participants 
  }
  return render(request , 'base/rooms.html',context)  
  
@login_required(login_url='login')
def createRoom(request):
  ## An empty formfield
  form = CreateRoom() 
  ## check if request is POST
  if request.method == "POST":
    ## fill out the form with the post details 
    form = CreateRoom(request.POST) 
    ## check if filled form is valid 
    if form.is_valid(): 
      #save to the database
      form.save() 
      #redirect to home.
      return redirect('home') 
      ## prep for rendering.
  context = {'form':form} 
  return render(request , 'base/room_form.html',context) 

@login_required(login_url='login')  
def updateRoom(request,pk):
  ## get the exact room with an id of pk 
  
  room = Room.objects.get(id=pk) 
  ## create a form and fill it with details of the room 
  if request.user != room.host:
    return HttpResponse('You are not allowed here')
  form = CreateRoom(instance=room) 
  ## if the method is post 
  if request.method == "POST":
    form = CreateRoom(request.POST,instance=room) 
    if form.is_valid():
      form.save() 
      return redirect('home') 
  context = {'form':form}
  return render(request ,'base/room_form.html',context) 

@login_required(login_url='login')
def deleteRoom(request,pk):
  room = Room.objects.get(id=pk) 
  
  if request.user != room.host:
    return HttpResponse('You are not allowed here') 
    
  if request.method == "POST":
    room.delete() 
    return redirect('home')
  context = {'obj':room} 
  return render(request,'base/delete.html' ,context) 

@login_required(login_url='login')
def deleteMessage(request,pk):
  room = Room.objects.all()
  participant = room.participants.get(id =request.user.id)
  message= Message.objects.get(id=pk) 
  if request.user != message.user:
    return HttpResponse('You are not allowed here') 
    
  if request.method == "POST":
    message.delete()
    room.participant.remove()
    return redirect('home')
  context = {'obj':message} 
  return render(request,'base/delete.html' ,context) 
  
def loginPage(request):
  page = "login"
  if request.user.is_authenticated :
    return redirect('home')
    
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    try:
      user = User.objects.get(username=username)
    except: 
      messages.error(request ,' User does not exist')
    user = authenticate(username=username,password=password) 
    if user is not None :
      login(request,user) 
      messages.success(request,' Logged in.') 
      return redirect('home')
    else:
      messages.error(request,'invalid credentials.')
  context = {'page':page} 
  return render (request ,'base/login_register.html',context) 
  
def registerPage(request):
  form = UserCreationForm() 
  if request.method == "POST":
    form = UserCreationForm(request.POST) 
    
    if form.is_valid():
      user = form.save(commit=False) 
      user.username = user.username.lower()
      user.save() 
      login(request,user) 
      return redirect('home') 
    else:
      messages.error(request,'An error occurred...')
  context = {'form':form}
  return render(request , 'base/login_register.html', context) 
  
  
def logoutUser (request):
  logout (request) 
  return redirect('home') 
  