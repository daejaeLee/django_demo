from django.shortcuts import render
from accounts.models import CustomUser
# Create your views here.

def mypage(request):
    if request.session.get('user'):
        user = CustomUser.objects.filter(email = request.session.get('user'))
        name = user.first().name
        user_dict = {'name':name}
        return render(request, 'mypage.html', user_dict)
    else:
        alert = {'msg':'로그인 후 이용할 수 있는 서비스입니다.', 'url':'/accounts/login'}
        return render(request, 'alert.html', alert)    

def pwchange(request):
    user = CustomUser.objects.filter(email = request.session.get('user'))
    user = user.first()
    print(user)
    if request.method == "POST":
        pw = request.POST.get('password1')
        pw2 = request.POST.get('pwchange')
        CustomUser.objects.filter(email = request.session.get('user')).update(
            password=pw2
        )
        alert = {'msg':'비밀번호 변경 완완료', 'url':'/accounts/logout'}
        return render(request, 'alert.html', alert)    
    return render(request, 'pwchange.html', {'user':user}) 