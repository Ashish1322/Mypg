# Importing some packages which are required
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from .models import Contact,Pg,Images,Booking,RegisterPg,Testmotional
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.paginator import Paginator

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
    pg = Pg.objects.get(sno=slug)
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
    if(slug=="Jhanjeri"):
        pgs = Pg.objects.filter(location__contains = "Jhanjeri")
        
    elif(slug=="Landra"):
        pgs = Pg.objects.filter(location__contains = "Landra")

    elif(slug == "for-boys-only"):
        pgs = Pg.objects.filter(type_pg = "Boys")
        
    elif(slug == "for-boys-girls"):
        pgs = Pg.objects.all()
        
    elif(slug == "for-girls-only"):
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
    pg = Pg.objects.get(sno=slug)
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
        # Finding Pg
        pg = Pg.objects.get(sno=slug)
        user = User.objects.get(username=username)
        # Checking if the user has already booked 2 pgs because more than 2 pgs are not booked at same account
        no_of_pending = Booking.objects.filter(user=user,order_confirmed=0)
        if(len(no_of_pending)>=2):
            messages.error(request,"Booking Failed because you cannot have more then 2 pending orders, So please try later !")
            return redirect('home')
        elif (len(str(phonenumber))!=10):
            messages.error(request,'Invalid Phone number!')
            return redirect('home')
        
        order = Booking(first_name=first_name,last_name=last_name,email=email,address=address,phone_number=phonenumber,state=state,zip_code=zip_code,college=college,pg=pg,user=user,order_confirmed=0)
        order.save()
        messages.success(request,"Thank for ordering we will contact you shortly for confirmation of order")
        return redirect('home')
        
    return HttpResponse("404 Error")

# To show user view of any user
def userview(request,slug):
    # slug is the username of the current user
    user = User.objects.get(username=slug)
    if(user.is_authenticated): # if user is login then show all the things
        pending_orders = Booking.objects.filter(user=user,order_confirmed=0)
        confirmed_orders = Booking.objects.filter(user=user,order_confirmed=1)
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
