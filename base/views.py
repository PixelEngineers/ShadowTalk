from datetime import timedelta

from django.conf.global_settings import SESSION_COOKIE_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.signals import request_finished
from django.dispatch import receiver

from database.FileDatabase import FileDatabase
# from database.FirebaseDatabase import FirebaseDatabase
from database.Interop import DatabaseInterop
from database.cookie import Cookie
from .forms import RoomForm, UserEditForm, EmailUserCreationForm, RequestForm
from django.contrib import messages
from os import mkdir
from os.path import exists

if not exists("file_db"):
    mkdir("file_db")

useDatabase: DatabaseInterop = FileDatabase(
    "file_db/users.dat",
    "file_db/groups.dat",
    "file_db/messages.dat",
    "file_db/auth.dat",
)

@receiver(request_finished)
def on_close(sender, **kwargs):
    useDatabase.deinit()

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
        return redirect(page)

    token = useDatabase.user_login(email, password)
    if token is None:
        messages.error(request, 'Login failed')
        return redirect(page)

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
    page = 'register'
    if request.method != 'POST':
        form = EmailUserCreationForm()
        return render(request, 'base/login_register.html', {'form': form})

    form = request.POST

    email = form.get('email').lower()
    email_validation = useDatabase.is_valid_email(email)
    if email_validation is not None:
        messages.error(request, email_validation)
        return redirect(page)

    if useDatabase.user_exists_email(email):
        messages.error(request, 'User already exists')
        return redirect(page)

    password = form.get('password')
    password_validation = useDatabase.is_valid_password(password)
    if password_validation is not None:
        messages.error(request, password_validation)
        return redirect(page)

    name = form.get('username')
    name_validation = useDatabase.is_valid_display_name(name)
    if name_validation is not None:
        messages.error(request, name_validation)
        return redirect(page)

    token = useDatabase.user_create(email, name, password, None)
    if token is None:
        messages.error(request, 'Failed to create account')
        return redirect(page)
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

@login_required(login_url='/login')
def profile_page(request, pk):
    if pk is None:
        if request.user is None:
            return redirect('404')
        pk = request.user.id
    user = useDatabase.user_public_get(pk)
    return render(request,'base/profile.html',{
        'user':user,
        'pk': pk
    })

@login_required(login_url='/login')
def room_create_page(request):
    form = RoomForm()
    if request.method != 'POST':
        return render(request, 'base/room_form.html', {
            'form': form,
        })
    useDatabase.group_private_create(request.POST.get('name'), request.user.id)
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
    if request.user.id not in room.admin_ids:
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
    if useDatabase.user_has_group_access(request.user.id, pk) != "admin":
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

    message = useDatabase.message_get_with_id(request.user.id, pk, gk)
    if message.author_id != request.user.id or useDatabase.user_has_group_access(request.user.id, gk) != "admin":
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
    if request.user.id != message.author_id:
        return HttpResponse('You are not allowed to edit this message')

    edited_message=request.POST.get('editedmessage')
    useDatabase.message_edit(request.user, gk, pk, edited_message)

    return redirect('room',pk=gk)


@login_required(login_url='/login')
def user_update_page(request):
    user = request.user
    if request.method != 'POST':
        return render(request, 'base/update_user.html', {
            'user': user
        })

    new_cookie = Cookie(request.user.id, request.user.email, request.user.name)
    email = request.POST.get('email')
    if email is not None and email != request.user.email:
        new_cookie.email = email
        useDatabase.user_change_email(request.user, email)

    username = request.POST.get('username')
    if username is not None and username != request.user.name:
        new_cookie.name = username
        useDatabase.user_change_username(request.user, username)


    response = redirect('user-profile',pk=user.id)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        useDatabase.encode_cookie(new_cookie),
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite='Strict',
    )
    return response

# TODO: change password??????

def landing_page(request):
    return render(request,'base/landing_page.html')

@login_required(login_url='/login')
def requests_page(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        print(request_id)
        if not useDatabase.request_send(request.user, request_id):
            messages.error(request, "Failed to send request")
        return redirect('requests-page')
    requests = list(map(
        lambda user_id: useDatabase.user_public_get(user_id),
        useDatabase.request_get(request.user)
    ))
    requests_count = len(requests)
    form = RequestForm()
    return render(request, 'base/requests_page.html', {
        'send_request': form,
        'requests': requests,
        'no_requests': requests_count == 0
    })


def download_page(request):
    return render(request, 'base/download.html')