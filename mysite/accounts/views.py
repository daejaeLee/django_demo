from django.shortcuts import render, redirect
from .models import CustomUser
from django.db import connection
#from django.contrib.auth import authenticate

def home(request):
    users = CustomUser.objects.all()
    context = {'users': users}
    
    return render(request, 'accounts/home.html', context)

def register(request):
    url = 'home:home'
    if request.method == "POST":
        email = request.POST['email']
        name = request.POST['name']
        password1 = request.POST['password1']
        user = CustomUser.objects.filter(email = email)
        print(len(user))
        if len(user) == 0:
            CustomUser.objects.create_user(
                username=email,
                email=email,  
                name=name,  
                password=password1
            )            
        else:
            alert = {'msg':'중복된 아이디 입니다.', 'url':'register'}
            return render(request, 'alert.html', alert)    

        print(url)
        return redirect(url)
    else:        
        return render(request, 'accounts/register.html')

#ORM기법을 통한 로그인
def login(request):
    url = "home:home"
    alert = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = CustomUser.objects.filter(email = email)
        if email is not None and password is not None and len(user) != 0:
            #user = authenticate(request, username=email, password=password)
            #print(user, type(user))
            #auth_login(request, user)
            pwd = user.first().password
            print(pwd)
            if pwd == password:
                request.session['user'] = email 
                print('seesion : ', request.session.get('user'))
            else:
                alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login'}
        else:
            alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login'}
        print(alert)
        if alert != "": return render(request, 'alert.html', alert)
        return redirect(url)
    else:
        return render(request, 'accounts/login.html')

#Raw Query 로그인 1
def login2(request):
    url = "home:home"
    alert = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        if email is not None and password is not None:
            cursor = connection.cursor()
            sql= f'select password from users where email = \'{email}\''
            print(sql)
            cursor.execute(sql)
            pwd = cursor.fetchall() # 레코드를 배열 형식으로 저장함
            pwd = pwd[0][0]
            print(pwd)
            if password == pwd:
                request.session['user'] = email 
                print('seesion : ', request.session.get('user'))
            else:
                alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login2'}
        else:
            alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login2'}
        if alert != "": return render(request, 'alert.html', alert)
        return redirect(url)
    else:
        return render(request, 'accounts/login2.html')

#Raw Query 로그인 2
def login3(request):
    url = "home:home"
    alert = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        if email is not None and password is not None:
            cursor = connection.cursor()
            sql = f'select email,pw from users where email = \'{email}\' and password = \'{password}\''
            print(sql)
            cursor.execute(sql)
            user = cursor.fetchall() # 레코드를 배열 형식으로 저장함

            if len(user) == 0:
                print('user is None')
                alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login3'}
            else:
                user = user[0][0]
                print(user)
                request.session['user'] = user 
                print('seesion : ', request.session.get('user'))
        else:
            alert = {'msg':'이메일 또는 비밀번호가 잘못되었습니다.', 'url':'login3'}
        if alert != "": return render(request, 'alert.html', alert)
        return redirect(url)
    else:
        return render(request, 'accounts/login3.html')

def logout(request):
    if request.session.get('user'):
        del(request.session['user'])
    print(request.session.keys())
        
    return redirect('home:home')