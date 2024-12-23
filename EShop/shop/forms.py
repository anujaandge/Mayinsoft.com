from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    
    name = forms.CharField(
         max_length=100,
         widget=forms.TextInput(attrs={
             'class': 'form-control',
             'id': 'name',
             'placeholder': 'Enter Your Name'  # Adding the placeholder attribute
         })
    )
    email = forms.EmailField(
         max_length=100,
         widget=forms.EmailInput(attrs={
             'class': 'form-control',
             'id': 'email',
             'placeholder': 'Enter Your Email'  # Adding the placeholder attribute
         })
    )
    phone = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
             'class': 'form-control',
             'id': 'phone',
             'placeholder': 'Enter Your Phone'  # Adding the placeholder attribute
         })
     )
    desc = forms.CharField(
        max_length=100,
        widget=forms.Textarea(attrs={
             'class': 'form-control',
             'id': 'desc',
             'rows': 4,
             'placeholder': 'Enter Your Message'  # Adding the placeholder attribute
         }),
        label='How May We Help You?'
    )
    
    class Meta:
        model = Contact
        fields = ("name", "email", "phone", "desc")
        
