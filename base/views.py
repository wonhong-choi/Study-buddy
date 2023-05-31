from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse
from .models import Room, Topic
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
    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room':room}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home") # urls.py > urlpatterns > name
            
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # pre-filled with a Model obj
    
    if request.user != room.host:
        return HttpResponse("Your are not allowed here")
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) # instance for what object updated
        if form.is_valid():
            form.save()
            return redirect("home")
        
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)
    

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Your are not allowed here")
    
    if request.method == 'POST':
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})