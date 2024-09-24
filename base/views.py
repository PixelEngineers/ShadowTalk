from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate , login, logout
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm,UserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from database.FileDatabase import FileDatabase

useDatabase = FileDatabase(
    "file_db/users.dat",
    "file_db/groups.dat",
    "file_db/messages.dat",
)

# Create your views here.

# rooms=[
#     {'id':1,'name':'Lets learn python'},
#     {'id':2,'name':'Design with me'},
#     {'id':3,'name':'Frontend developers'},
       
# ]
def loginPage(request):
    page='login' 
    if request.user.is_authenticated:
        return redirect('home')
    if request.method== 'POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user= authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Userame or password does not exist')

    context={'page':page}
    return render(request, 'base/login_register.html',context)


@login_required(login_url='/login')
def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page='register'
    form=UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    return render(request,'base/login_register.html',{'form':form})

@login_required(login_url='/login')
def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
     
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)| 
        Q(name__icontains=q) | 
        Q(description__icontains=q)|
        Q(host__message__body__icontains=q)
    ).distinct()

    room_count=rooms.count() 
    #refering parent class topic, icontains will if the letter is in the string, return insensituve to case
    topics=Topic.objects.all()

    room_messages= Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

@login_required(login_url='/login')
def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('created') #all the set of messages in that room
    participants=room.participants.all()
    if request.method=='POST':
        print(room)
        print(len(Message.objects.all()))

        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)

    context={'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)

def userProfile(request,pk):
    user=User.objects.get(id=pk) 
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='/login')
def createRoom(request):
    form= RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created= Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form=RoomForm(request.POST)
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     room.host= request.user
        #     room.save()
        return redirect('home')
    context={'form':form,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login')
def updateRoom(request,pk):
    topics=Topic.objects.all()
    room=Room.objects.get(id=pk)
    form= RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not the admin')
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created= Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form=RoomForm(request.POST,instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context={'form':form,'topics':topics,'room':room}
    return render(request, 'base/room_form.html',context)

@login_required(login_url='/login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not the admin')
    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='/login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not the admin')
    if request.method=='POST':
        message.delete()
        return redirect('room',pk=message.room.id)
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='/login')
def editMessage(request,pk):
    message=Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not the admin')
    if request.method=='POST':
        edited_message=request.POST.get('editedmessage')
        message.body=edited_message
        message.save()

        return redirect('room',pk=message.room.id)
    return render(request,'base/edit_message.html',{'obj':message})


@login_required(login_url='/login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method == 'POST':
        form=UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)

    return render(request,'base/update-user.html',{'form':form})



def land(request):
    return render(request,'base/landing_page.html')