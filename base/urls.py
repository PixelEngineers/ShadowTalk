from django.urls import path
from . import views

urlpatterns=[
    path('',views.landing_page, name='landing-page'),
    path('login/',views.login_page,name='login'),
    path('logout/',views.logout_page,name='logout'),
    path('register/',views.register_page,name='register'),

    path('home/',views.home_page, name='home'),
    path('download/', views.download_page, name='download'),

    path('profile/<str:pk>/',views.profile_page,name='user-profile'),
    path('update-user/', views.user_update_page, name='update-user'),
    path('requests/', views.requests_page, name='requests-page'),

    path('room/<str:pk>/', views.room_page, name='room'),
    path('create-room/',views.room_create_page,name='create-room'),
    path('update-room/<str:pk>/',views.room_update_page,name='update-room'),
    path('delete-room/<str:pk>/',views.room_delete_page,name='delete-room'),

    path('delete-message/<str:gk>/<str:pk>/',views.message_delete_page,name='delete-message'),
    path('edit-message/<str:gk>/<str:pk>/',views.message_edit_page,name='edit-message'),
]