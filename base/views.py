from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


from .models import Room, Topic, Message
from .forms import RoomForm

# Create your views here.

def login_page(request):
    page = 'login'
    # when enter url with "/login/" user can re-login. so prevent re-login
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            
        user = authenticate(request, username=username, password=password) # authenticate > id, password 등 일치여부를 인식해 user 객체를 반환
        if user is not None:
            login(request, user) # session에 login 상태 저장
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')
        
    context = {'page' : page}
    return render(request, 'base/login_register.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def register_user(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) # commit=True > save date to DB. else > return obj
            # why we do not directly save? > uppercase to lowercase, etc
            user.username = user.username.lower()
            user.save()
            login(request, user) # optional
            return redirect('home')
        else:
            messages.error(request, 'An Error occured during registeration')

    context = {'form' : form}
    return render(request, 'base/login_register.html', context)


def home(request):
    ##### +, # 등과 같은 특수문자는 공백처리됨. 이를 어떻게 처리할까??
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    
    # queryset = ModelName.objects.all()
    # response = model name. model objects attribute. method
    # Q for multiple conditions
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) # contains > 포함하는 문자열 찾기, icontains > 대소문자 구분하지 않음.
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )
    
    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count,
               'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room,
               'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,
               'rooms': rooms,
               'room_messages': room_messages,
               'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, was_created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            
        return redirect("home") # urls.py > urlpatterns > name
            
    context = {'form' : form,
               'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # pre-filled with a Model obj
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse("You're are not allowed here")
    
    if request.method == 'POST':
        # form = RoomForm(request.POST, instance=room) # instance for what object updated
        # if form.is_valid():
        #     form.save()
        #     return redirect("home")
        
        topic_name = request.POST.get('topic')
        topic, was_created = Topic.objects.get_or_create(name=topic_name)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        
    context = {'form' : form,
               'topics': topics,
               'room' : room}
    return render(request, 'base/room_form.html', context)
    

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You're are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You're are not allowed here")
    
    if request.method == 'POST':
        message.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':message})