from django.shortcuts import render, get_object_or_404
from django.db import connection
from .models import Board,Comment
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404
import os

def board_list(request):
    cursor = connection.cursor()

    # 검색 키워드와 검색 필드 가져오기
    search_keyword = request.GET.get('search', '').strip()
    search_field = request.GET.get('field', 'title')  # 기본값은 'title'
    page = int(request.GET.get('page', 1))

    # 기본 SQL 쿼리
    sql = 'SELECT b_num, title, email, write_time FROM board WHERE d_check = true'

    # 검색 필드와 키워드에 따라 SQL 조건 추가
    if search_keyword and search_field in ['title', 'content', 'email']:
        sql += f" AND {search_field} LIKE '%%{search_keyword}%%'"

    sql += ' ORDER BY b_num DESC'
    cursor.execute(sql)
    boards = cursor.fetchall()

    # 페이징 처리
    paginator = Paginator(boards, 10)  # 한 페이지에 10개씩 표시
    boards_page = paginator.get_page(page)

    context = {
        'boards': boards_page,
        'search_keyword': search_keyword,
        'search_field': search_field,
        'current_page': boards_page.number,
        'page_range': paginator.get_elided_page_range(page, on_each_side=2, on_ends=1),
        'total_pages': paginator.num_pages,
    }
    return render(request, 'board/list.html', context)

def board_view(request):
    alert=''
    if request.method == 'POST':
        bNum = request.POST.get('b_num')
        Comment.objects.create(
                    post = bNum,
                    user = request.session.get('user'),
                    content = request.POST.get('comment'),
        )
        cursor = connection.cursor()
        sql = f'update board set comment = comment+1 where b_num = {bNum}'
        cursor.execute(sql)

        alert = {'msg':'댓글을 작성했습니다.', 'url':'/board/view?b_num='+bNum}
        return render(request, 'alert.html', alert)
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        
        cursor = connection.cursor()
        sql = f'select title,email,content,v_num,write_time,file_name,file_path,comment from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        board = cursor.fetchall()
        
        if len(board) != 0:
            # 조회수 로직
            v_num = board[0][3]
            if request.session.get('user') != board[0][1]:
                sql = f'update board set v_num = v_num+1 where b_num = {bNum}'
                cursor.execute(sql)
                v_num += 1
            comment = board[0][7]
            if comment != 0:
                comments = Comment.objects.filter(post=bNum)
            else:
                comments = []
            print(comment)
            # 데이터 저장
            content = {
                'title':board[0][0], 
                'email':board[0][1], 
                'content':board[0][2], 
                'v_num':v_num, 
                'write_time':board[0][4],
                'b_num':bNum,
                'file_name':board[0][5],
                'file_path':board[0][6],
                'comments':comments
                }
        else:
            #글이 존재하지 않을 때
            alert = {'msg':'존재하지 않는 글 입니다.', 'url':'/board/list?page=1'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board/list?page=1'}
    if alert !='': return render(request, 'alert.html', alert)
    return render(request, 'board/view.html', content)

def board_write(request):
    alert=''
    if request.session.get('user'):
        if request.method == "POST":
            #글 작성 로직
            r_title = request.POST.get('title')
            r_content = request.POST.get('content')
            
            if r_title.strip() !='' and r_content.strip() != '':
                uploaded_file = request.FILES.get('file')
                print(uploaded_file)
                if uploaded_file != None:
                    Board.objects.create(
                    title = r_title,
                    content = r_content,
                    email = request.session.get('user'),
                    file_name=uploaded_file,
                    file_path=uploaded_file
                ) 
                else:
                    Board.objects.create(
                        title = r_title,
                        content = r_content,
                        email = request.session.get('user') 
                    )   
                alert = {'msg':'글 작성 완료', 'url':'/board/list?page=1'}
            else:
                #제목과 내용이 공백일 경우
                alert = {'msg':'제목과 내용을 정확히 입력해 주세요', 'url':'write'}
        else:
            #post로 접근한게 아닐 경우 글 작성 페이지 렌더링
            return render(request, 'board/write.html')
    else:
        #로그인 사용자가 아닐 경우 처리
        alert = {'msg':'로그인 후 작성해 주세요', 'url':'/accounts/login'}

    #로직이 끝난 후 최종 url로 redirect
    return render(request, 'alert.html', alert)

def board_update(request):
    alert=''
    # 수정 view
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        
        cursor = connection.cursor()
        sql = f'select title,content from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        board = cursor.fetchall()
        print(len(board))
        if len(board) != 0:
            content = {
                'title':board[0][0],
                'content':board[0][1],
                'b_num':bNum
                }
        else:
            #글이 존재하지 않을 때
            alert = {'msg':'존재하지 않는 글 입니다.', 'url':'/board/list?page=1'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board/list?page=1'}
    
    # update요청 처리 로직
    if request.method == "POST":
        bNum = request.POST.get('b_num')
        content = request.POST.get('content')
        print(bNum, content)
        if content.strip() != '':
            cursor = connection.cursor()
            sql = f'update board set content = \'{content}\' where b_num = {bNum}'
            cursor.execute(sql)
            alert = {'msg':'수정 완료', 'url':'/board/view?b_num='+bNum}    
        else:
            alert = {'msg':'수정 실패', 'url':'/board/view?b_num='+bNum}
    if alert !='': return render(request, 'alert.html', alert)
    return render(request, 'board/update.html', content)

def board_delete(request):
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        cursor = connection.cursor()
        sql = f'select email from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        user = cursor.fetchall()
        if len(user) != 0:
            user = user[0][0]
            if user == request.session.get('user'):
                sql = f'update board set d_check = false where b_num = {bNum}'
                cursor.execute(sql)
                alert = {'msg':'삭제 완료', 'url':'/board/list?page=1'}
            else:
                alert = {'msg':'권한이 없습니다.', 'url':'/board/list?page=1'}
        else:
            alert = {'msg':'이미 삭제된 글이거나, 존재하지 않습니다.', 'url':'/board/list?page=1'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board/list?page=1'}
    return render(request, 'alert.html', alert)

def download_file(request, filename, bnum):
    # 파일 이름으로 레코드 검색
    file_record = get_object_or_404(Board, file_name=filename, b_num = bnum)
    print(file_record)
    # 실제 파일 경로
    file_path = file_record.file_path.path  # 파일의 절대 경로
    
    # 파일이 존재하는지 확인
    
    # 파일 확인 및 반환
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        raise Http404("File not found")