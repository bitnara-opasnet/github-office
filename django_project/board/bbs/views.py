from django.shortcuts import render, redirect
# from django.http import HttpResponse
from .models import Post
from pytz import timezone

def index(request):
    # return HttpResponse("Hello world") 
    return render(request,'index.html')

def list(request):
    postlist = Post.objects.all()
    return render(request, 'list.html', {'postlist': postlist})

def detail(request, pk): # 게시글(Post) 중 pk(primary_key)를 이용해 하나의 게시글(post)를 검색
    post = Post.objects.get(pk=pk)
    post.create_date = post.create_date.astimezone(timezone('Asia/Seoul'))
    print(post.create_date)
    return render(request, 'detail.html', {'post': post})

def input(request):
    if request.method == 'POST':
        new_list=Post.objects.create(
            name=request.POST['name'],
            title=request.POST['title'],
            contents=request.POST['contents'],
        )
        return redirect('/list')
    return render(request, 'input.html')

def delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('/list')