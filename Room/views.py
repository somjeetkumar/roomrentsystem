import secrets
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import CreateView,DeleteView,DetailView,UpdateView,ListView,TemplateView
from .models import UserModel,Room,Room_Image,Payment,Otp
import random
import time

from .uitility import room_number,send_email_for_user
from django.http import HttpResponse
from django.contrib.auth import login,logout,authenticate
from django.views import View
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from .forms import *
from django.urls import reverse_lazy
import razorpay
import random
from django.http import JsonResponse
import json

# Create your views here.




def dashboard_stats(request):
    if request.user.is_authenticated:
        return {
            'total_rooms': Room.objects.all().count(),
            'total_room_owners':UserModel.objects.filter(groups__name='Owner').count(),
            'total_room_renter':UserModel.objects.filter(groups__name='Renter').count(),
        }
    return {}


class RegisterView(CreateView):
    form_class = RegisterForm
    model = UserModel
    template_name = 'auth/register.html'
    success_url = reverse_lazy('mailVerify')

    def form_valid(self, form):
        user = form.save(commit=True)
        user.groups.add(form.cleaned_data['group'])
        user.save()
        otp = str(random.randint(100000,999999))
        Otp.objects.create(
            otp=otp,
            user = user
        )
        send_mail(
            "Email Verification",
            f"Your OTP is {otp}",
            "your_email@gmail.com",
            [user.email],
        )
        self.request.session["user_id"] = user.id
        return super().form_valid(form)




class ReOTPSEND(View):
    def post(self, request):
        email = request.POST.get("email")
        if email:
            user = get_object_or_404(UserModel, email=email)
        else:
            u_id = request.session.get("user_id")
            if not u_id:
                return redirect("register")
            user = get_object_or_404(UserModel, id=u_id)
        otp = str(secrets.randbelow(900000) + 100000)
        Otp.objects.filter(user=user).delete()
        Otp.objects.create(
            otp=otp,
            user=user
        )

        send_mail(
            "Email Verification",
            f"Your OTP is {otp}",
            "your_email@gmail.com",
            [user.email],
        )

        return redirect("mailVerifiy")


class UserEmailVerifiy(View):
    def get(self,request):
        msg = ""
        return render(request,'auth/otpverify.html',{"msg":msg})
    def post(self,request):
        user_otp = request.POST.get('otp')
        u_id = self.request.session.get('user_id')
        user = get_object_or_404(UserModel, id=u_id)
        otp_obj = Otp.objects.filter(user=user).last()
        if otp_obj.is_expired():
            msg = "otp invalid send again"
            return  render(request,'auth/otpverify.html',{"msg":msg})
        if user_otp == otp_obj.otp:
            user.is_active = True
            user.verify= True
            user.save()
            otp_obj.delete()
            return redirect('login')
        else:
            msg = "otp invalid send again"
            return  render(request,'auth/otpverify.html',{"msg":msg})


            

        

class loginView(View):
    def get(self,request):
        return render(request, 'auth/login.html',{"error":""})
    
    def post(self,request):
        start = time.time()
        user = authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
        print('auth time',time.time()-start,' -- - -- ', user)
        if user is not None:
            login(request,user)
            # print('auth time',time.time()-start)
            return redirect('home')
        # print('auth time',time.time()-start)
        return render(request, 'auth/login.html', {"error":"Incorrect username or password"})
    

class logoutUserView(LogoutView):
    next_page = 'home'

class HomeView(View):
    def get(self,request):
        rooms = Room.objects.filter(room_checked=True,available=True).order_by('-create_at')
        city = request.GET.get('city','').strip()
        pin = request.GET.get('pinCode','').strip()
        if city:
            rooms = rooms.filter(city__icontains=city)
        if pin:
            rooms = rooms.filter(pin_code__icontains=pin)
        room_data = []
        for room in rooms:
            image =Room_Image.objects.filter(room=room, check_image=True).first()
            room_data.append({
                'room':room,
                "image":image
            })
        
        return render(request, 'room/index.html', {'rooms':room_data})



    

class RoomUploadView(LoginRequiredMixin,PermissionRequiredMixin,CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'room/room_form.html'
    permission_required = 'Room.add_room'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # room = form.save(commit=False)
        room = form.save(commit=False)
        form.instance.onwer = self.request.user
        images = self.request.FILES.getlist('images')
        
        room.room_number = room_number()
        room.save()
        for image in images:
            Room_Image.objects.create(room=room,image=image)
        
        return super().form_valid(form)


    def form_invalid(self, form):
        print("FORM ERRORS:", form.errors) 
        return super().form_invalid(form)
    











class CheckRoom_by_Admin(LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = (
        'Room.change_room_image',
        'Room.change_room'
    )

    def get(self,request,pk):
        room =get_object_or_404(Room,pk=pk)
        form = RoomDetail_CheckForm(instance=room)
        image_room = Room_Image.objects.filter(room=room)

        return render(
            request,
            'room/check_room.html',
            {'form':form,
             'image':image_room,
             'room':room 
             }
        )
    
    def post(self,request,pk):
        room =get_object_or_404(Room,pk=pk)
        form = RoomDetail_CheckForm(request.POST,request.FILES,instance=room)
        image_room = Room_Image.objects.filter(room=room)
        if form.is_valid():
            form.save()
            for img in  image_room:
                if f"img{img.id}" in request.POST:
                    img.check_image = True
                    img.save()
                else:
                    img.check_image = False
                    img.save()
            return redirect('RoomList')
        return render(
            request,
            'room/check_room.html',
            {'form':form,
             'image':image_room,
             'room':room 
             }
        )
            


class ProfileView(LoginRequiredMixin,ListView):
    model = Room
    template_name = 'room/owner_profile.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        rooms = Room.objects.filter(onwer=self.request.user)
        room_data = []

        for room in rooms:
            if room.room_checked == True:
                image =Room_Image.objects.filter(room=room, check_image=True).first()
                room_data.append({
                        'room':room,
                        'room_image':image
                    })
            else:
                image =Room_Image.objects.filter(room=room).first()
                room_data.append({
                        'room':room,
                        'room_image':image
                    })

    def dispatch(self, request, *args, **kwargs):

            if not request.user.groups.filter(name='Owner').exists():
                return redirect('home')

            return super().dispatch(request, *args, **kwargs)



class roomdeleteByOwner(View):
    def get(self,request,pk):
        return render(request,'room/ownerRoomDelete.html')
    def post(self,request,pk):
        room = get_object_or_404(Room,pk=pk)
        room.delete()
        return redirect('Profile')


class update_room_owner(View):
    def get(self,request,pk):
        room = get_object_or_404(Room,pk=pk)
        images = Room_Image.objects.filter(room=room)

        context = {
            "room":room,
            "images":images
        }
        return render(request,"room/updateRoomOwner.html",context)
    
    def post(self,request,pk):
        room = get_object_or_404(Room,pk=pk)
        room.title = request.POST.get("title")
        room.room_type = request.POST.get("room_type")
        room.city = request.POST.get("city")
        room.near_by = request.POST.get("near_by")
        room.pin_code = request.POST.get("pin_code")
        # room.available = request.POST.get("available")
        room.location = request.POST.get("location")
        room.address = request.POST.get("address")
        room.price = request.POST.get("price")
        room.description = request.POST.get("description")

        room.room_checked = False
        room.save()
        delete_images = request.POST.getlist('delete_images')
        if delete_images:
            for img_id in delete_images:
                img = get_object_or_404(Room_Image,id=img_id)
                img.image.delete()
                img.delete()
            
        new_image = request.FILES.getlist('new_images')
        if new_image:
            for img in new_image:
                Room_Image.objects.create(
                room=room,
                image=img,
                check_image=False
                )
        
        return redirect('Profile')



    


    


    # {'Room.change_room_image', 'Room.add_room', 'Room.view_room_image', 'Room.delete_room', 'Room.view_room', 'Room.delete_room_image', 'Room.add_room_image', 'Room.change_room'}      


class RoomDeatils(LoginRequiredMixin,DetailView):
    model = Room
    template_name = 'room/room-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        roomImages = Room_Image.objects.filter(room=room,check_image=True)
        context['room'] = room
        context['images'] = roomImages

        return context
    






class PaymentView(LoginRequiredMixin, TemplateView):

    template_name = "room/payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        room = get_object_or_404(Room, pk=self.kwargs["pk"])
        if room.available == False:
            return redirect('home')
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        amount = 4000

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })
        

        payment = Payment.objects.create(
            user=self.request.user,
            room=room,
            amount=amount,
            razorpay_order_id=order["id"]
        )
        room.available = False
        room.save()

        context["order"] = order
        # print(order,'===================')
        context["payment"] = payment
        context["razorpay_key"] = settings.RAZORPAY_KEY_ID

        return context











class PaymentSuccessView(View):

    def get(self, request, order_id):
        print(order_id,'-------------------------')

        payment = get_object_or_404(Payment, razorpay_order_id=order_id)

        payment_id = request.GET.get("payment_id")

        if not payment_id:
            return HttpResponse("Invalid payment")

        # # Prevent duplicate processing
        if not payment.paid:

            payment.razorpay_payment_id = payment_id
            payment.paid = True
            payment.save()
            payment.room.available = False
            # payment.room.save()
            payment.room.save(update_fields=["available"])

            renter_email = payment.user.email
            owner_email = payment.room.onwer.email

            messageRenter = f"""
            Room booked successfully.

            Room: {payment.room.title}
            Amount Paid: ₹{payment.amount/100}
            Room Owner Phone: {payment.room.onwer.phone}
            Room Owner Email: {owner_email}
            Address: {payment.room.address}
            Location: {payment.room.location}
            """

            messageOwner = f"""
            Your room has been booked.

            Room: {payment.room.title}
            Amount Paid: ₹{payment.amount/100}
            Renter Phone: {payment.user.phone}
            Renter Email: {renter_email}
            """

            send_mail(
                "Room Booking Successful",
                messageRenter,
                settings.EMAIL_HOST_USER,
                [renter_email],
                fail_silently=False,
            )

            send_mail(
                "New Room Booking",
                messageOwner,
                settings.EMAIL_HOST_USER,
                [owner_email],
                fail_silently=False,
            )

        return render(request, "room/success.html", {"payment": payment})





class Renter_list(ListView):
    model = UserModel
    template_name = 'deshbord/renter.html'
    context_object_name = 'renter'
    def get_queryset(self):
        return UserModel.objects.filter(groups__name = 'Renter')
    


class Owner_list(ListView):
    model = UserModel
    template_name = 'deshbord/owner.html'
    context_object_name = 'owner'
    def get_queryset(self):
        return UserModel.objects.filter(groups__name = 'Owner')
    





class Room_list(ListView):
    model = Room
    template_name = 'deshbord/room_List.html'
    context_object_name = 'rooms'
    def get_context_data(self, **kwargs):   
        # print(self.request.user.get_all_permissions())
        context = super().get_context_data(**kwargs)
        rooms = Room.objects.all()
        room_data = []
        for room in rooms:
            image =Room_Image.objects.filter(room=room, check_image=True).first()
            room_data.append({
                'room':room,
                "image":image
            })
        #     print(room,image,' - -- - ')
        context['rooms'] = room_data
        
        return context



class AdminRoomDeatil(View):
    def get(self,request,pk):
        room = get_object_or_404(Room, pk=pk)
        room_image = Room_Image.objects.filter(room=room)
        # payment =  get_object_or_404(Payment,room=room)
        payment = Payment.objects.filter(room=room, paid=True).first()

        renter = None
        if payment:
            renter = payment.user
        
        context = {
            "room":room,
            "images":room_image,
            "renter":renter
        }
    
        return render(request, 'deshbord/room-details.html', {"context":context})
    



class DeleteRoom_admin(View):
    def get(self,request,pk):
        room = get_object_or_404(Room,pk=pk)
        room.delete()
        return redirect('RoomList')
        