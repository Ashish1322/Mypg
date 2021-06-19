# Importing some packages which are required
from mypg.settings import EMAIL_HOST_PASSWORD
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from .models import Contact,Pg,Images,Booking,RegisterPg,Testmotional
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from mypg.settings import EMAIL_HOST_USER
from django.core.mail import send_mail, BadHeaderError
import razorpay
from django.template.loader import render_to_string
import smtplib
from email.message import EmailMessage
import datetime

# Function to store testmotional to database
def testm(request):
    if(request.method=="POST"):
        testmotional = request.POST['testmotional']
        uservalue = request.POST['user']
        user = User.objects.get(username=uservalue)
        test = Testmotional(user=user,test=testmotional)
        test.save()
        messages.success(request,"Thanks for sharing your view with us.")
    
    return render(request,'pg/testmotional.html')

# Function to store contacts by any user
def contact(request):
    if(request.method=="POST"):
        name = request.POST['contact_name']
        email = request.POST['contact_email']
        message = request.POST['contact_message']
        # Validation checking
        if(len(name)>20):
            messages.error(request,"Please enter a valid name")
            return redirect('contact')
        elif(message==""):
            messages.error(request,"Message cannot be empty")
            return redirect('contact')

        query = Contact(name=name,email=email,message=message,responded=False)
        query.save()
        messages.success(request,"Your query has been submitted successfully. We will contact you shortly")
        return redirect('contact')

    return render(request,'pg/contact_us.html')

# Function which provides search functionaliy
def findpg(request):
    if(request.method=="POST"):
        query = str(request.POST['query'])
        query = query.strip()
        query = query.split(" ")
        # For getting empty query set
        final_pgs = {}
        for i in query:            
            i = i.capitalize()  # Because all the data in pgs is Captialize       
            if(i=='For' or i=='Of' or i=='At' or i=='A'): # ignore prepositions
                continue
            # If query in name, description, type, location of pgs then collect all those pgs.
            pg1 = Pg.objects.filter(name__contains = i)
            pg2 = Pg.objects.filter(description__contains = i)
            pg3 = Pg.objects.filter(type_pg__contains = i)
            pg4 = Pg.objects.filter(location__contains = i)
            # using sets to find union and avoid repetition
            pg = set(pg1.union(pg2,pg3,pg4))
            final_pgs =  pg.union(final_pgs)
        final_pgs = list(final_pgs)
        # Range is to print stars
        return render(request,'pg/findpg.html',{'pgs':final_pgs,'range':range(1,6),'len':len(final_pgs)})

    return HttpResponse("404 Error")

# Function to details of any Pg and slug contains pg id which is to be shown
def pgdetail(request,slug):
    pg = Pg.objects.get(slug=slug)
    distance_list = pg.distance.split(',') # for printing in html split by ,
    rules = pg.rules.split(",") # for showing rule in html spilt by ,
    images = Images.objects.filter(pg=pg) # all the image corrspond to pg
    # For more pgs like this section except currrent pg
    more_pgs1 = (Pg.objects.filter(type_pg = pg.type_pg)).exclude(sno= pg.sno)
    more_pgs2 = Pg.objects.filter(location= pg.location).exclude(sno = pg.sno)
    more_pgs3 = Pg.objects.filter(price__lte =   pg.price).exclude(sno=pg.sno)
    pgs = more_pgs1.union(more_pgs2,more_pgs3)
    # range --> for selected pg rating out of 5
    # range2 --> for selected pg remaining rating stars
    # range3 --> for more like this pgs showing the stars in card
    return render(request,'pg/pgdetail.html',{'pg':pg,'range':range(0,pg.ratings),'range2':range(0,5-pg.ratings),'distance':distance_list,'rules':rules,'images':images,'pgs':pgs,'range3':range(1,6)})
 

# Function which provides quick serch functionaliy
def quicksearch(request,slug):
    # Slug is the type of quick search
    pgs = [] # list to store results
    if(slug=="paying-guests-cgc-jhanjeri-mohali-chandigarh"):
        pgs = Pg.objects.filter(location__contains = "Jhanjeri")
        
    elif(slug=="paying-guests-cgc-landra-mohali-chandigarh"):
        pgs = Pg.objects.filter(location__contains = "Landra")

    elif(slug == "pgs-for-boys-cgc-jhanjeri-landra-chandigarh"):
        pgs = Pg.objects.filter(type_pg = "Boys")
        
    elif(slug == "boys-girls-pg-near-cgc-chandigarh"):
        pgs = Pg.objects.all()
        
    elif(slug == "pgs-for-girls-cgc-jhanjeri-landra-chandgarh"):
        pgs = Pg.objects.filter(type_pg = "Girls")
        
    else:
        return HttpResponse("404 Error")

    # If there are more results then 6 then create pages using paginator
    p = Paginator(pgs,6)
    page_number = request.GET.get('page') # for navigating between pages
    pgs_page = p.get_page(page_number) # current page
    return render(request,'pg/findpg.html',{'pgs':pgs_page,'len':len(pgs),'range':range(1,6),'for':"Pg's for Boys",'page_range':p.page_range,}) # p.page_range is to show all the availbale pages for navigation which are fetching by get request in line 109

# To show book pg form of selected pg
def book_pg_form(request,slug):
    pg = Pg.objects.get(slug=slug)
    # Range is to print stars shown on selected pg
    return render(request,'pg/bookpg.html',{'pg':pg,'range':range(1,6)})

# Function to store data of booked pgs, slug is id of pg to be order
def book_pg(request,slug):
    if(request.method=="POST"):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        address = request.POST['address']
        phonenumber = request.POST['phone_number']
        state = request.POST['state']
        zip_code = request.POST['zip']
        college = request.POST['college_name']
        username = request.POST['user']
        # Finding Pg and user
        pg = Pg.objects.get(slug=slug)
        user = User.objects.get(username=username)


        # Checking if the user has already booked 2 pgs because more than 2 pgs are not booked at same account
        # no_of_pending = Booking.objects.filter(user=user,order_confirmed=0)
        # if(len(no_of_pending)>=2):
        #     messages.error(request,"Booking Failed because you cannot have more then 2 pending orders, So please try later !")
        #     return redirect('home')
        # elif (len(str(phonenumber))!=10):
        #     messages.error(request,'Invalid Phone number!')
        #     return redirect('home')

        
        # Creating order from server side to Razorpay
        client = razorpay.Client(auth = ('rzp_test_xxnGiAzsbNO0b9', '1TO0c2GUr4dscLuVSNaC65Ja'))
        order_amount = pg.price*100 #Price is in paisas to multiply by 100
        order_currency = 'INR'
        notes = {'first_name':first_name,'last_name':last_name,'email':email,'address':address,'phonenumber':phonenumber,'state':state,'username':username}
    
        order = client.order.create({'amount':order_amount, 'currency':order_currency,'notes':notes})
    
        # initially the status of this order in databae is pending
        order_ds = Booking(first_name=first_name,last_name=last_name,email=email,address=address,phone_number=phonenumber,state=state,zip_code=zip_code,college=college,pg=pg,user=user,order_id = order['id'])
        order_ds.save()      
        
        return render(request,'pg/payment_process.html',{'order_id':order['id'],'amount':order_amount,'amount_rupee': order_amount/100,'name':first_name+last_name,'email':email,'name_pg':pg.name})
        
    return HttpResponse("404 Error") #if someone try to manually put url then show error




# if we send email in payment success function below then it will take time and no laoding will show due to some defualt settings of razorpay form so after the saving and confirming order we are sending the request to this fuction and while showing loading animation we can send email using this function and it will look more geniune to user that loading is happening if we don't do this then the impacct will be bad
def show_load(request,sno):
    order = Booking.objects.get(sno=sno)
    # getting all the data of confirmed order and sending mail receipt to user
    c = {'pgname':order.pg.name,'pglocation':order.pg.location,'pgtype': order.pg.type_pg,'price':order.pg.price ,'paymentid':order.razorpay_payment_id,'phonenumber':order.phone_number,'email':order.email,'name':order.first_name+ order.last_name,'zip':order.zip_code,'state':order.state,'paymentmethod':'UPI','orderid':order.order_id,'pymentdate':order.booking_date,'validdate':order.expiry_date}
    filepos = "pg/paymentdone.txt"
    msg = EmailMessage()
    msg['Subject'] = 'Payment Receipt for your Booking'
    msg['From'] = EMAIL_HOST_USER 
    msg['To'] = order.email
    msg.set_content(render_to_string(filepos,c), subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD) 
        smtp.send_message(msg)
        # When mail is send show succesfull message and redirect to receipt
        messages.success(request,"Congratulations your payment is Successfull. Payment receipt has been sent on given email.")
        return render(request,'pg/receipt.html',c)   
    
# Razorpay will send a post request to this view function when a user will make payment and  return all the details of payment and status of payment using post request to us but in django it is not allowed that some other websites will make post request on our website due to csrf protection so here we are removing csrf protection for this view function so that it will accept the post requests made by other websites
@csrf_exempt
def payment_success(request):
    if(request.method=="POST"):
        # Fetching details returned by the checkout form of razorpay
        razorpay_payment_id = request.POST['razorpay_payment_id']
        razorpay_order_id = request.POST['razorpay_order_id']
        razorpay_signature = request.POST['razorpay_signature']
        order_id = request.POST['order_id']
        email = request.POST['email']
        # Store this details in a order database
        order = Booking.objects.get(order_id=order_id)
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_signature = razorpay_signature
        order.save()
        # login the client
        client = razorpay.Client(auth = ('rzp_test_xxnGiAzsbNO0b9', '1TO0c2GUr4dscLuVSNaC65Ja'))
        # store all the variables in a dictionary
        params_dict = {'razorpay_order_id':razorpay_order_id ,'razorpay_payment_id': razorpay_payment_id,'razorpay_signature': razorpay_signature}
        # Verify the signature returned by the razorpay and know payment is successfull or not
        #by using verify_payment_signature function which return None when signature matches and if there is any problem or signature not mathces then it willl raise the error which we are handling in the except block and if it is successfull then it will remain in try block and if not successfull then it will go on except block 
        try:
            # if payment is successfull then  update the status of order in database which is fetch by using order_id above to the Success

            client.utility.verify_payment_signature(params_dict)
            order.order_status = "confirmed"
            order.save()

            # Getting Dates of booking and expiry of booking
            x = datetime.datetime.now()
            validtill = x+datetime.timedelta(36)
            booking_date = x.strftime("%d %b %Y, %H:%M:%S")
            validtill = validtill.strftime("%d %b %Y, %H:%M:%S")
            order.booking_date = booking_date
            order.expiry_date = validtill
            order.save()

            # At this step payment is successfull and order is confirmed so show the loading html file for loading animation and while this animation send email to user using show_load function and show order successfull message.
            return render(request,'pg/shoload.html',{'sno':order.sno})
            

        except Exception as e:
            # if payment is failed then  update the status of order in database which is fetch by using order_id above to the Failure
            order.order_status = "failed"
            order.save()
            messages.error(request,"Payment Failed, Something went wrong please try again")
            return redirect("home") #if payment is failed redirect to home

       
        
    return HttpResponse("404 Error")


# To show user view of any user
def userview(request,slug):
    # slug is the username of the current user
    user = User.objects.get(username=slug)
    if(user.is_authenticated): # if user is login then show all the things

        # Getting orders which are not successfull
        p1 = Booking.objects.filter(user=user,order_status='pending')
        p2 = Booking.objects.filter(user=user,order_status='failed')
        pending_orders = p1.union(p2)
        # Getting orders which are confirmed and successfull
        confirmed_orders = Booking.objects.filter(user=user,order_status='confirmed')
        # For identyfying in the html file that pending order or confirmed are empty
        pending_len = len(pending_orders)
        confirm_len = len(confirmed_orders)

        # Range is to print stars on the pg card
        return render(request,'pg/userview.html',{'pending_orders':pending_orders,'confirmed_orders': confirmed_orders,'range':range(1,6),'pending_len':pending_len,'confirm_len':confirm_len})
    else:
        # if not login then show error
        messages.error(request,'Some Error Occurd.')
        return redirect("home")

# Function to change some other details of user
def change_details(request,slug):
    if(request.method=="POST"):
        user = User.objects.get(username=slug) # Fetching the user
        name = request.POST['name']
        email = request.POST['email']
        user.first_name = name # chaging the name of user
        user.email = email # changing the email of user
        user.save()
        messages.success(request,"Information Updated Succesfully")
        return redirect('userview',slug)
    # if request is not post then show error
    return HttpResponse("404 Error")

# Function to change password
def changepassword(request,slug):
    if(request.method=="POST"):
        oldpassword = request.POST['oldpassword']
        newpassword1 = request.POST['newpassword']
        newpassword2 = request.POST['confirmnewpassword']
        user = authenticate(username=slug,password = oldpassword)

        # Checing for correctness of old password
        if user is None:
            # if old password is wrong then user is failed to authenticate and return None
            messages.error(request,"Invalid Password! Please Try Again.")
            
        else:
            # if old password is correct then match two new password
            if(newpassword1==newpassword2):
                # if match then change password
                try:
                    user.set_password(newpassword2)
                    user.save()
                    messages.success(request,"Password chagned successfully.")
                except Exception as e:
                    messages.error(request,"Some error Occured!")
            else:
                # if not match then show error
                messages.error(request,"Password doesn't Matches")
        return redirect('home')
        
    return HttpResponse("404 Error")

# Function to register pg
def registerpg(request):
    if(request.method=='POST'):
        name_owner = request.POST['owner_name']
        name_pg = request.POST['pgname']
        location = request.POST['location']
        phone_number = request.POST['phone_number']
        typepg = request.POST['typepg']
        description = request.POST['description']
        if(len(str(phone_number))!=10):
            messages.error(request,"Invalid Phone Number!")
            return redirect('registerpg')
        register = RegisterPg(name=name_pg,location=location,typepg=typepg,phonenumber=phone_number,description=description,owner_name=name_owner,verified=0)
        register.save()
        messages.success(request,"Request Successfully submitted. We will contact you shortly.")
        return redirect('registerpg')

    return render(request,'pg/register.html')

# Function to cancel order
def cancel(request,sno):
    # sno is the id of order to be deleted from database
    try:
        order = Booking.objects.get(sno=sno)
        username = order.user.username
        order.delete()
        messages.success(request,"Order Deleted Successfuly")
        return redirect('userview',username) # redirecting to userview with username as slug
    except Exception as e:
        messages.error(request,"Some error Occured Please try agian.")
        return redirect('home')

def receipt(request,sno):
    try:
        order = Booking.objects.get(sno=sno)
        x = datetime.datetime.now()
        validtill = x+datetime.timedelta(36)
        booking_date = x.strftime("%d %b %Y, %H:%M:%S")
        validtill = validtill.strftime("%d %b %Y, %H:%M:%S")

            # Filling the empty feilds and detalis in the payment reciept that has to be send to user
        c = {'pgname':order.pg.name,'pglocation':order.pg.location,'pgtype': order.pg.type_pg,'price':order.pg.price ,'paymentid':order.razorpay_payment_id,'phonenumber':order.phone_number,'email':order.email,'name':order.first_name+ order.last_name,'zip':order.zip_code,'state':order.state,'paymentmethod':'UPI','orderid':order.order_id,'pymentdate':order.booking_date,'validdate':order.expiry_date}  
        content = render_to_string('pg/paymentdone.txt',c)

        return render(request,'pg/receipt.html',c)     
    except Exception as e:
        messages.error("Something Went Wrong Please Try again later")
        return redirect('home')

   