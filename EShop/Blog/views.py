from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .models import Blogpost
# Create your views here.

def index(request):
    myposts=Blogpost.objects.all()
    print(myposts)
    return render(request, 'blog/index.html',{'myposts':myposts})

def blogpost(request, myid):
    post=Blogpost.objects.filter(post_id=myid)[0]
    return render(request,"blog/blogpost.html",{'post':post})
