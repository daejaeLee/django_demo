from django.shortcuts import render
from accounts.models import CustomUser

def home(request):
    content = {'login':'/accounts/login', 'logout':'/accounts/logout', 'register':'/accounts/register', 'accounts':'accounts/'}
    #세션이 존재하면 db에서 값 추출
    if request.session.get('user'):
        user = CustomUser.objects.filter(email = request.session.get('user'))
        print(user.first().name)
        name = user.first().name
        user_dict = {'name':name}
        content = {**content, **user_dict} #딕셔너리 병합
        print(request.session.keys())

    return render(request, 'index.html', content)