from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q # or 조건 사용하기

from .models import Post
from .forms import PostForm

from werkzeug.urls import url_encode
import datetime
import pytz

def reverse_querystring(view, urlconf=None, args=None, kwargs=None, current_app=None, query_kwargs=None):
    base_url = reverse(view, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    if query_kwargs:
        return '{}?{}'.format(base_url, urlencode(query_kwargs))
    return base_url 

def index(request):
    return render(request,'index.html')

# Read
class IndexView(ListView):
    model = Post
    context_object_name = 'postlist'   
    template_name='list.html'
    paginate_by = 10

    # def get_queryset(self):
    #     postlist = Post.objects.order_by('-create_date')
    #     return postlist

    def get_queryset(self):
        search_keyword = self.request.GET.get('keyword', '') 
        search_type = self.request.GET.get('type', '')
        search_date = self.request.GET.get('date', '')
        # print(search_date) # 2021-10-8
        if search_date:
            # search_date = datetime.datetime.strptime(search_date, "%Y-%m-%d").date()
            # postlist = Post.objects.filter(create_date__icontains=search_date)
            search_date = pytz.timezone('UTC').localize(datetime.datetime.strptime(search_date, "%Y-%m-%d"))
            postlist = Post.objects.filter(create_date__date=search_date)
        else:
            postlist = Post.objects.order_by('-create_date') 

        if search_type and search_keyword:
            if search_type == 'all':
                search_post_list = postlist.filter(Q(title__icontains=search_keyword) | Q(contents__icontains=search_keyword) | Q(name__icontains=search_keyword))
            elif search_type == 'title':
                search_post_list = postlist.filter(title__icontains=search_keyword) # 대소문자 구분 없는 검색    
            elif search_type == 'contents':
                search_post_list = postlist.filter(contents__icontains=search_keyword)    
            elif search_type == 'name':
                search_post_list = postlist.filter(name__icontains=search_keyword)
            return search_post_list
        return postlist
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range) # 전체 page 수

        page = self.request.GET.get('page', '1') # request 객체의 page값을 가져옴, 없으면 1
        current_page = int(page) if page else 1 # 현재 page, 없으면 1

        start_index = int((current_page-1)/page_numbers_range) * page_numbers_range # 화면에 보여줄 index의 시작
        end_index = start_index + page_numbers_range # 화면에 보여줄 index의 끝
        if end_index >= max_index: # end_index가 max_index보다 크면 max_index 값으로 설정
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index] # 화면에 보여줄 index값 설정
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('keyword', '')
        search_type = self.request.GET.get('type', '')
        search_date = self.request.GET.get('date', '')
        if search_type and search_keyword :
            context['keyword'] = search_keyword
            context['type'] = search_type
        if search_date:
            context['date'] = search_date
        search_params = '&' + url_encode({'type': search_type, 'keyword': search_keyword, 'date': search_date})
        context['search_params'] = search_params
        return context

# Detail
class DetailView(DetailView):
    model = Post
    context_object_name = 'post'  
    template_name='detail.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        search_keyword = self.request.GET.get('keyword', '')
        search_type = self.request.GET.get('type', '')
        search_params = '&' + url_encode({'type': search_type, 'keyword': search_keyword})
        if search_type and search_keyword :
            context['keyword'] = search_keyword
            context['type'] = search_type
            context['search_params'] = search_params
        context['page'] = page
        return context

# Create
class CreateView(CreateView):
    model = Post
    form_class = PostForm
    # fields = ['name', 'title', 'contents'] # form_class와 동시에 사용 불가
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        search_keyword = self.request.GET.get('keyword', '')
        search_type = self.request.GET.get('type', '')
        search_params = '&' + url_encode({'type': search_type, 'keyword': search_keyword})
        if search_type and search_keyword :
            context['keyword'] = search_keyword
            context['type'] = search_type
            context['search_params'] = search_params
        context['page'] = page
        return context

    def get_success_url(self):
        page = self.request.GET.get('page')
        search_keyword = self.request.GET.get('keyword', '')
        search_type = self.request.GET.get('type', '')
        # return reverse('detail', kwargs={'pk': self.object.pk})
        return reverse_querystring('detail', kwargs={'pk': self.object.pk}, 
                                    query_kwargs={'page': page, 'keyword': search_keyword, 'type':search_type})