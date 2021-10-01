from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Post

def index(request):
    return render(request,'index.html')

# Read
class IndexView(ListView):
    model = Post
    context_object_name = 'postlist'   
    template_name='list.html'
    paginate_by = 10  

    def get_queryset(self):
        postlist = Post.objects.order_by('-create_date')
        # page = request.GET.get('page', '1')
        # paginator = Paginator(postlist, 10)
        # page_obj = paginator.get_page(page)
        return postlist

# Detail
class DetailView(DetailView):
    model = Post
    context_object_name = 'post'  
    template_name='detail.html'  

# Create
class CreateView(CreateView):
    model = Post
    fields = ['name', 'title', 'contents']
    template_name = 'input.html'

    def get_success_url(self):
        return reverse('list')

#Delete
class DeleteView(DeleteView) :
    model = Post
    template_name ='delete.html'
    success_url = reverse_lazy('list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

#Update
class UpdateView(UpdateView):
    model = Post
    fields = ['name', 'title', 'contents']
    template_name = 'modify.html'

    def get_success_url(self):
        return reverse('detail', kwargs={'pk':self.object.pk})