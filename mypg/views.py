from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.shortcuts import redirect

def home(request):
    return render(request,'mypg/home.html')

def login_user(request):
    if(request.method=="POST"):
        name = request.POST['login_name']
        password = request.POST['login_password']
        user = authenticate(username=name,password = password)
        if user is None:
            messages.error(request,"Invalid Credentials! Try Again.")
            return redirect('home')
        else:
            login(request,user)
            messages.success(request,"Login Successfully")
            return redirect('home')
    return render(request,'mypg/login_signup.html')

def signup_user(request):
    if(request.method=='POST'):
        name = request.POST["signup_name"]
        user_name = request.POST["signup_user_name"]
        email = request.POST["signup_email"]
        password = request.POST["signup_password"]
        password2 = request.POST["signup_password_confirm"]
        # checking for valid data
        try:
            user = User.objects.get(username=user_name)
            messages.error(request,"User name already exists")
            return redirect('home')
        except Exception as e:
            if(password!=password2):
                messages.error(request,"Password doesn't matches")
                return redirect('home')
            elif (len(name)>20):
                messages.error(request,"Please enter valid name")
                return redirect('home')
            user = User.objects.create_user(username=user_name,password=password,email=email,first_name = name)
            user.save()
            messages.success(request,"Account created successfully")
            return redirect('home')
    return HttpResponse("404 Error")

def logout_user(request):
    logout(request)
    messages.success(request,"Logout Successfully")
    return redirect('home')

def about(request):
    return render(request,'mypg/about_us.html')

def faq(request):
    return render(request,'mypg/faq.html')

def policy(request):
    return render(request,'mypg/privacy_policy.html')

def conditions(request):
    return render(request,'mypg/terms_conditions.html')