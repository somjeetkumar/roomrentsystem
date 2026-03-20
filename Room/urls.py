from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    #------------- auth-------------------
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', loginView.as_view(), name='login'),
    path('reSentOtp/',ReOTPSEND.as_view(), name='reSendOtp'),
    path('mailVerify/',UserEmailVerifiy.as_view(), name='mailVerify'),

    #------------- room------------------
    path('', HomeView.as_view(), name='home'),
    path('room_upload/',RoomUploadView.as_view(),name="room_upload"),
    path('check_room/<int:pk>/',CheckRoom_by_Admin.as_view(),name="check_room"),
    path('logout/',logoutUserView.as_view(),name='logout'),
    path('profile/', ProfileView.as_view(), name='Profile'),
    path('room_delete/<int:pk>/',roomdeleteByOwner.as_view(), name='roomdeleteByOwner'),
    path('update_room_owner/<int:pk>/',update_room_owner.as_view(), name='update_room_owner'),
    path('roomDetailAdmin/<int:pk>/',AdminRoomDeatil.as_view(),name='AdminRoomDeatil'),
    
    path('room_details/<int:pk>/',RoomDeatils.as_view(),name='room_details'),
    path('room_details/<int:pk>/payment/',PaymentView.as_view(),name='payment'),
    path("success/<str:order_id>/", PaymentSuccessView.as_view(), name="success"),
    path("renterList/", Renter_list.as_view(), name='renterList'),
    path("ownerList/", Owner_list.as_view(), name='ownerList'),
    path("RoomList/", Room_list.as_view(), name='RoomList'),
    path('DeleteRoom_admin/<int:pk>/',DeleteRoom_admin.as_view(), name='DeleteRoom_admin')
]

