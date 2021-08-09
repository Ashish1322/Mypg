# Importing some required libraries
from email.message import EmailMessage
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

import smtplib
from .settings import EMAIL_HOST_PASSWORD
from django.urls import reverse

# For sending activation key
from django.utils.encoding  import DjangoUnicodeDecodeError,force_bytes,force_text
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
# Function to home page
def home(request):
    r_pg = recommended.objects.all() # Recommended pgs from database shown on home page
    testmotional = Testmotional.objects.all()
    # range is to print stars on the card of pg
    return render(request,'mypg/home.html',{'pgs':r_pg,'range':range(1,6),'len':len(r_pg),'testmotionals':testmotional,'len2':len(testmotional)})

# Login the user function
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

# Funtion to Signup User
def signup_user(request):
    if(request.method=='POST'):
        name = request.POST["signup_name"]
        user_name = request.POST["signup_user_name"]
        email = request.POST["signup_email"]
        password = request.POST["signup_password"]
        password2 = request.POST["signup_password_confirm"]

        # checking for valid data
        try:
            user = User.objects.get(email=email)
            messages.error(request,"An account with this email already exists, Please use diffrent email address.")
            return redirect("home")
        except Exception as e:
            pass
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
             # Saving the user but now account is not activate a confirmation link will be sent on given mail to activate account
            user.is_active = False
            user.save()
            # Content of activation email
            domain = get_current_site(request).domain
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
         
            link =  reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
            # Sending Account Activation email to user
            subjet = "Activate your account"
            activate_url = "http://"+domain+link
            body = "Hi "+user.username + "Please use this link to verify your account\n"+activate_url
            send_mail(
                subjet,
                body,
                'noreply@semicolon.com',
                [email],
                fail_silently=False,
            )
            messages.warning(request,"The Activation link has been sent on the provided email. Kindly check your mail and activate your account")
            return redirect('home')

    return HttpResponse("404 Error")

# Function on which user land when he click on the activation email or token are verified of his account on signup
def get(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception as e:
        user = None
    if user is not None and token_generator.check_token(user,token):
        user.is_active = True
        user.save()
       # if everthing is fine then Sending Welcome Email to user when account is activated
        msg = EmailMessage()
        msg['Subject'] = 'Welcome to the Apna Thikana'
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = user.email
        content = render_to_string('pg/welcome.txt',{'name':user.first_name})
        msg.set_content(content,subtype='html')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) 
            smtp.send_message(msg)
                 
        messages.success(request,"Your account has been verified and activated succesfully. Hoping for your better experience.")
        return render(request,"mypg/account-activation.html")

    messages.error(request,"There is some problem in link so please Try again.")
    return redirect("home")

# Function to logout the user
def logout_user(request):
    logout(request)
    messages.success(request,"Logout Successfully")
    return redirect('home')

# Funtction to about page
def about(request):
    return render(request,'mypg/about_us.html')

# Function to faq page
def faq(request):
    return render(request,'mypg/faq.html')

# Function to policy page
def policy(request):
    return render(request,'mypg/privacy_policy.html')

# Funtion to conditions page
def conditions(request):
    return render(request,'mypg/terms_conditions.html')


# Function to reset the password and send mail 
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