from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserModel,Room,Room_Image
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory


class RegisterForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset= Group.objects.all(),
        required=True
    )
    class Meta:
        model = UserModel
        fields = ['username','email','phone','image','group','password1','password2']

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter username'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter email address'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter phone number'
            }),

            'image': forms.FileInput(attrs={
                'class': 'form-control rounded-3'
            }),

            'group': forms.Select(attrs={
                'class': 'form-select',
            }),
        }





class RoomForm(forms.ModelForm):


    class Meta:
        model = Room
        fields = ['title','city','near_by','pin_code','description','price','room_type','available','location','address']

        widgets = {

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder":"e.g., Spacious Single Room near Bus Stand"
            }),
            
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder":"e.g., jaipur"
            }),
            
            'near_by': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder":"e.g., Dadi Ka Phatak"
            }),
            
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder":"e.g., 000000"
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'description'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter Price'
            }),

            'room_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'single, double, flat'

            }),
            'available': forms.CheckboxInput(attrs={
                    'class': 'form-check-input'
                }),
            'location': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'location'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter address'
            }),

        }




class RoomDetail_CheckForm(forms.ModelForm):


    class Meta:
        model = Room
        fields = ['title','description','price','room_type','available','location','address','room_checked']

        widgets = {

            'title': forms.TextInput(attrs={
                'class': 'form-control',
                "placeholder":"e.g., Spacious Single Room near Bus Stand"
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'description'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter Price'
            }),

            'room_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'single, double, flat'

            }),
            'available': forms.CheckboxInput(attrs={
                    'class': 'form-check-input'
                }),
            'location': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'location'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control form-control-lg rounded-3',
                'placeholder': 'Enter address'
            }),
            'room_checked':forms.CheckboxInput(attrs={
                    'class': 'form-check-input'
                }),
        }

