from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.shortcuts import redirect
from pg.models import Pg,recommended,Testmotional
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from mypg.settings import EMAIL_HOST_USER

def home(request):
    r_pg = recommended.objects.all()
    testmotional = Testmotional.objects.all()
    # range is to print stars on the card of pg
    return render(request,'mypg/home.html',{'pgs':r_pg,'range':range(1,6),'len':len(r_pg),'testmotionals':testmotional,'len2':len(testmotional)})

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

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "mypg/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'apnastartuppg.herokuapp.com',
					'site_name': 'Apna Thikana',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, EMAIL_HOST_USER , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="mypg/password_reset.html", context={"password_reset_form":password_reset_form})