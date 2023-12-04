from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login,logout
from ecomm_app.models import product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.
def about(request):
    return HttpResponse("Hello from about page")

def contact(request):
    return HttpResponse("<h1>Hello from contact page</h1>")

def edit(request,rid):
    return HttpResponse("Id to be edited:"+rid)

def addition(request,x1,x2):
    t=int(x1)+int(x2)
    t=str(t)
    return HttpResponse("addition is:"+t)

def hello(request):
    context={}
    context['greet']="Hello,we are learning DTL"
    context['x']=10
    context['y']=20
    context['l']=[10,20,30,40]
    context['products']=[
	    {'id':1,'name':'samsung','cat':'mobile','price':2000},
	    {'id':2,'name':'jeans','cat':'clothes','price':500},
	    {'id':3,'name':'vivo','cat':'mobile','price':1500},
        ]
    return render(request,'hello.html',context)

def home(request):
    #userid=request.user.id
    #print("id of logged in user:",userid)
    #print("result:",request.user.is_authenticated)
    p=product.objects.filter(is_active=True)
    #print(p)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        usname=request.POST['usname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        if usname=="" or upass=="" or ucpass=="":
            context['errmsg']="Field can not be empty"
            return render(request,'register.html',context)

        if upass != ucpass :
            context['errmsg']="Password and confirm password didn't match"
            return render(request,'register.html',context)

        else:
            try:
                u=User.objects.create(password=upass,username=usname,email=usname)
                u.set_password(upass)
                u.save()
                context['success']="User created successfully,Please Login"
                return render(request,'register.html',context)
                #return HttpResponse("Registration Successful")
            except Exception:
                context['errmsg']="user with same username already exist"
                return render(request,'register.html',context)

    else:
         return render(request,'register.html')

def user_login(request):
    if request.method=='POST':
        usname=request.POST['usname']
        upass=request.POST['upass']
        #print(usname,"-",upass)
        #return HttpResponse("Data is fetched")
        context={}
        if usname=="" or upass=="":
            context['errmsg']="field can not be empty"
            return render(request,'login.html',context)

        else:
            u=authenticate(username=usname,password=upass)
            print(u)     #object
            #print(u.username)
            #print(u.is_superuser)
            if u is not None:
                login(request,u)
                #return render(request,'index.html')
                return redirect('/home')
            else:
                context['errmsg']="Invalid Username or password"
                return render(request,'login.html',context)

    else:
        return render(request,'login.html')


def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=product.objects.filter(is_active=True).order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render (request,'index.html',context)

def addtocart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        #print(pid)
        #print(userid)
        u=User.objects.filter(id=userid)
        #print(u[0])
        p=product.objects.filter(id=pid)
        #print(p[0])

        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=Cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        context['products']=p
        if n==1:
            context['msg']="Product Already Exist in Cart!!"
        else:
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()        
            context['success']="Product Added Successfully to cart!!"
        return render(request,'product_details.html',context)
    else:
        return redirect('/login')

def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    '''
    print(c)
    print(c[0].uid)   
    print(c[0].pid)
    print(c[0].pid.price)
    print(c[0].uid.is_superuser)'''
    s=0
    np=len(c)
    for x in c:
        # print(x)  # cart object
        #print(x.pid.price)
        s=s + x.pid.price*x.qty
    print(s)
    context={}
    context['data']=c
    context['total']=s
    context['n']=np

    return render(request,'cart.html',context)

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    if qv=='1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty>1:
            t=c[0].qty-1
            c.update(qty=t)
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    print(c)
    oid=random.randrange(1000,9999)
    #print(oid)
    for x in c:
        #print(x)
        #print(x.pid)
        #print(x.uid)
        #print(x.qty)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()  #delete records from cart table 
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    context['data']=orders
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price*x.qty
    context['total']=s
    context['n']=np
    return render(request,'placeorder.html',context)

def makepayment(request):
    uemail=request.user.username
    #print(uemail)
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s + x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_i9z3hOzNj7teK8", "zZxa9L71xgIIPZHE62Hj5IHy"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    #print(payment)
    context={}
    context['data']=payment
    context['uemail']=uemail
    return render(request,'pay.html',context)

def sendusermail(request,uemail):
    print(uemail )
    msg="order details"
    send_mail(
        "Ekart-order placed successfully",
        msg,
        "shivgundekomal@gmail.com",
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("mail sent successfully")


