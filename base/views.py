from datetime import timedelta

from django.conf.global_settings import SESSION_COOKIE_NAME
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,redirect
from django.http import HttpResponse

from database.FirebaseDatabase import FirebaseDatabase
from database.Interop import DatabaseInterop
from .forms import RoomForm, UserForm
from django.contrib import messages

useDatabase: DatabaseInterop = FirebaseDatabase()

def login_page(request):
    page = 'login'
    if request.COOKIES.get(SESSION_COOKIE_NAME) is not None:
        return redirect('home')
    if request.method != 'POST':
        return render(request, 'base/login_register.html', {
            'page': page
        })

    form = request.POST
    email = form.get('email').lower()
    password = form.get('password')
    if not useDatabase.user_exists_email(email):
        messages.error(request, 'User does not exist')

    token = useDatabase.user_login(email, password)
    if token is None:
        messages.error(request, 'Login failed')

    response = redirect('home')
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite='Strict',
    )
    return response


@login_required(login_url='/login')
def logout_page(request):
    request.session.flush()
    return redirect('home')


def register_page(request):
    if request.method != 'POST':
        form = UserCreationForm()
        return render(request, 'base/login_register.html', {'form': form})

    form = request.POST
    if not form.is_valid():
        messages.error(request,'An error occurred during registration')

    email = form.get('email').lower()
    password = form.get('password')
    name = form.get('username')
    token = useDatabase.user_create(email, name, password, None)
    response = redirect('home')
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite='Strict',
    )
    return response

@login_required(login_url='/login')
def home_page(request):
    """
    Currently I have turned off message searching, because the UI will also have to be configured different for those
    """
    raw_query = request.GET.get('q')
    query = raw_query if raw_query is not None else ''
     
    rooms = useDatabase.group_search(request.user, query)
    room_count = len(rooms)

    return render(request,'base/home.html', {
        'rooms':rooms,
        'room_count':room_count,
    })

@login_required(login_url='/login')
def room_page(request, pk):
    if pk is None:
        return redirect('home')
    room = useDatabase.group_get(request.user, pk)
    room_messages = useDatabase.message_get(request.user, room.id, None, 64)

    if request.method != 'POST':
        return render(request, 'base/room.html', {
            'room': room,
            'room_messages': room_messages,
            'participants': room.member_ids
        })

    _ = useDatabase.message_send(
        request.user,
        room.id,
        request.POST.get('body'),
        # TODO: replies
        False,
        None,
        None
    )
    return redirect('room',pk=room.id)


def profile_page(request, pk):
    if pk is None:
        if request.user is None:
            return redirect('404')
        pk = request.user.uid
    user = useDatabase.user_public_get(pk)
    return render(request,'base/profile.html',{
        'user':user
    })

@login_required(login_url='/login')
def room_create_page(request):
    form = RoomForm()
    if request.method != 'POST':
        return render(request, 'base/room_form.html', {
            'form': form,
        })
    useDatabase.group_private_create(request.POST.get('name'), request.user.uid)
    return redirect('home')

@login_required(login_url='/login')
def room_update_page(request, pk):
    if pk is None:
        return redirect('404')
    room = useDatabase.group_get(request.user, pk)
    form = RoomForm(instance=room)

    if request.method != 'POST':
        return render(request, 'base/room_form.html',{
            'form': form,
            'room': room
        })
    if request.user.uid not in room.admin_ids:
        return HttpResponse('You are not the admin')

    useDatabase.group_rename(request.user, room.id, request.POST.get('name'))
    return redirect('home')

@login_required(login_url='/login')
def room_delete_page(request, pk):
    if pk is None:
        return redirect('404')
    if request.method != 'POST':
        room = useDatabase.group_get(request.user, pk)
        return render(request, 'base/delete.html', {'obj': room})
    if useDatabase.user_has_group_access(request.user.uid, pk) != "admin":
        return HttpResponse('You are not the admin')

    useDatabase.group_delete(request.user, pk)
    return redirect('home')

@login_required(login_url='/login')
def message_delete_page(request, gk, pk):
    if pk is None:
        return redirect('404')

    if request.method != 'POST':
        message = useDatabase.message_get_with_id(request.user, gk, pk)
        return render(request, 'base/delete.html', {
            'obj': message
        })

    message = useDatabase.message_get_with_id(request.user.uid, pk, gk)
    if message.author_id != request.user.uid or useDatabase.user_has_group_access(request.user.uid, gk) != "admin":
        return HttpResponse('You can not delete this message')

    useDatabase.message_delete(request.user, gk, pk)
    return redirect('room', pk=gk)


@login_required(login_url='/login')
def message_edit_page(request, gk, pk):
    if pk is None:
        return redirect('404')

    message = useDatabase.message_get_with_id(request.user, gk, pk)
    if request.method != 'POST':
        return render(request, 'base/edit_message.html', {'obj': message})
    if request.user.uid != message.author_id:
        return HttpResponse('You are not allowed to edit this message')

    edited_message=request.POST.get('editedmessage')
    useDatabase.message_edit(request.user, gk, pk, edited_message)

    return redirect('room',pk=gk)


@login_required(login_url='/login')
def user_update_page(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method != 'POST':
        return render(request, 'base/update-user.html', {'form': form})

    form = UserForm(request.POST, instance=user)
    if not form.is_valid():
        messages.error(request, 'Invalid form inputs')

    email = request.POST.get('email')
    if email is not None:
        useDatabase.user_change_email(request.user, email)

    username = request.POST.get('username')
    if username is not None:
        useDatabase.user_change_username(request.user, username)

    return redirect('user-profile',pk=user.id)

# TODO: change password??????

def landing_page(request):
    return render(request,'base/landing_page.html')