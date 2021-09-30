from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import ListView, DetailView, DeleteView, UpdateView

from .models import Post

from pytz import timezone
import datetime

def index(request):
    # return HttpResponse("Hello world") 
    return render(request,'index.html')

# Read
# def list(request):
#     postlist = Post.objects.all()
#     return render(request, 'list.html', {'postlist': postlist})

class IndexView(ListView):
    model = Post
    context_object_name = 'postlist'   
    template_name='list.html'  

# def detail(request, pk): # 게시글(Post) 중 pk(primary_key)를 이용해 하나의 게시글(post)를 검색
#     try:
#         post = Post.objects.get(pk=pk)
#         post.create_date = post.create_date.astimezone(timezone('Asia/Seoul'))
#         print(post.create_date)
#     except Post.DoesNotExist:
#         raise Http404("Does not exist!")
#     return render(request, 'detail.html', {'post': post})

class DetailView(DetailView):
    model = Post
    context_object_name = 'post'  
    template_name='detail.html'  

# Create
def input(request):
    if request.method == 'POST':
        new_list = Post.objects.create(
            name=request.POST['name'],
            title=request.POST['title'],
            contents=request.POST['contents'],
        )
        # return redirect('/list')
        return HttpResponseRedirect(reverse('list'))
    return render(request, 'input.html')


#Delete
def delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect('/list')

# class DeleteView(DeleteView) :
#     model = Post
#     template_name ='delete.html'

#Update
# def modify(request, pk):
#     post = Post.objects.get(pk=pk)
#     if request.method == 'POST':
#         post.name = request.POST['name']
#         post.title = request.POST['title']
#         post.contents = request.POST['contents']
#         post.create_date = datetime.datetime.now()
#         post.save()
#         return redirect('/list')
#     return render(request, 'modify.html', {'post': post})

class UpdateView(UpdateView):
    model = Post
    fields = ['name', 'title', 'contents']
    template_name = 'modify.html'

    def update_date(self):
        self.create_date = datetime.datetime.now()
        super(Post, self).save()

    def get_success_url(self):
        return reverse('detail', kwargs={'pk':self.object.pk})