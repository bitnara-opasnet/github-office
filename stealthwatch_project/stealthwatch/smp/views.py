from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView, TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.views import View

from .forms import RegisterForm, UserChangeForm, ProfileForm, UserPasswordChangeForm, ApiConfigForm, FlowSearchForm
from .models import ApiConfig, TagList
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

import json
import datetime
import pytz
import pandas as pd

from lib.api_call import ApiCall, ConfingApi

def getKey(list) :
    return list['total']

# Create your views here.
def index(request):
    # return render(request, 'index.html')
    return redirect('login')

# 회원가입
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'

    def get_success_url(self):
        return reverse('login')

#회원 정보 보기
class UserDetailView(LoginRequiredMixin, DetailView): 
    model = User
    template_name = 'profile.html' 
    context_object_name = 'profile_user'

# 회원 정보 수정
class UserUpdateView(UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'user_modify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['profile_form'] = ProfileForm(self.request.POST, self.request.FILES, instance=self.request.user.profile)
        else:
            context['profile_form'] = ProfileForm(instance=self.request.user.profile)
        return context

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk':self.kwargs['pk']})

    def form_valid(self, form):
        context = self.get_context_data()
        profile_form = context['profile_form']
        profile_form = profile_form.save()
        return super().form_valid(form)

# 비밀번호 변경
class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'user_password_modify.html'

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk':self.kwargs['pk']})

# API configuration
class ApiConfigView(LoginRequiredMixin, View):
    form_class = ApiConfigForm

    def get_object(self):
        if ApiConfig.objects.exists():
            obj = ApiConfig.objects.first()
            if obj.password:
                obj.password = '********'
        else:
            obj = None
        return obj

    def get(self, request):
        context = {}
        context['form'] = self.form_class(instance=self.get_object())
        return render(request, 'apiconfig.html', context=context)
    
    def post(self, request, *args, **kewargs):
        form_password = request.POST.get('password')
        if request.POST.get('password').startswith('********'):
            form_password = ApiConfig.objects.first().password

        form = self.form_class(request.POST, instance=self.get_object())
    
        if form.is_valid():
            form.save(commit=False)
            form.instance.password = form_password
            form.save()
   
        # return render(request, 'apiconfig.html', {'form': form})
        return self.get(request)


# class ApiConfigView(LoginRequiredMixin, UpdateView): 
#     model = ApiConfig
#     form_class = ApiConfigForm
#     template_name = 'apiconfig.html' 
#     context_object_name = 'apiconfig'

#     def get_success_url(self):
#         return reverse('apiconfig')

# Host Groups List
class HostGroupList(TemplateView):
    template_name = 'hostgroups_list.html'
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('hostgroup') == None:
            hostgroup = 1
        else:
            hostgroup = self.request.GET.get('hostgroup')
        print(hostgroup)
        hostgroups_list = self.api_call.get_hostgroup_list()
        if hostgroups_list is not None:
            for i in hostgroups_list[0]['root']: 
                # print(i['name'])
                # if i['name'] == 'Inside Hosts':
                if i['id'] == int(hostgroup):
                    host_list = i['children']
            context['host_list'] = host_list
        else:
            context['hostgroup_detail'] = None
        context['hostgroup'] = hostgroup
        return context

class HostGroupListData(View):
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get(self, request, hostgroup):
        results = {}
        print(hostgroup)
        hostgroups_traffic = self.api_call.get_hostgroups_traffic()
        for i in hostgroups_traffic[0]['resultDto']:
            if i['rootTagId'] == int(hostgroup):
                insidegroup_traffic = i['tagTraffic']
        for i in self.tag_list:
            for j in insidegroup_traffic:
                if j['tagId'] == i.tagid:
                    j['name'] = i.name
        results['results'] = insidegroup_traffic
        return JsonResponse(results)

# Host Group Detail
class HostGroupDetail(TemplateView):
    template_name = 'hostgroups_detail.html'
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hostgroup_detail = self.api_call.get_hostgroup_detail(self.kwargs['id'])
        if self.request.GET.get('hostgroup') == None:
            hostgroup = 1
        else:
            hostgroup = self.request.GET.get('hostgroup')
        print(hostgroup)

        hostgroups_list = self.api_call.get_hostgroup_list()
        if hostgroups_list is not None:
            for i in hostgroups_list[0]['root']: 
                if i['id'] == int(hostgroup):
                    parent_host_list = i['children']
            for i in parent_host_list:
                if i['id'] == self.kwargs['id']:
                    host_list = i['children']
                    context['host_list'] = host_list

            context['hostgroup_detail'] = hostgroup_detail
        else:
            context['hostgroup_detail'] = None
        context['hostgroup'] = hostgroup
        return context

class HostGroupDetailData(View):
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()
    def get(self, request, id, hostgroup):
        results = {}
        print(hostgroup)
        if hostgroup ==1:
            applications_traffic_result = self.api_call.get_application_traffic(tag_id = id)
        else:
            applications_traffic_result = self.api_call.get_application_traffic_outside(tag_id = id)
        applications_traffic = []
        for i in applications_traffic_result:
            inbound_sum = 0; outbound_sum = 0; 
            for j in i['data']:
                inbound_sum += j['value']['inboundByteCount']
                outbound_sum += j['value']['outboundByteCount']
                total_sum = inbound_sum + outbound_sum
            applications_traffic.append({'id': i['header']['applicationId'], 'total': total_sum, 'inbound': inbound_sum, 'outbound': outbound_sum})
        applications_traffic.sort(key=getKey, reverse=True)
        applications_traffic = applications_traffic[0:10]

        if hostgroup == 1:
            traffic_result = self.api_call.get_traffic(tag_id = id)
        else:
            traffic_result = self.api_call.get_traffic_outside(tag_id = id)
        total_traffic = []
        for i in traffic_result['data']:
            total_traffic.append({'timestamp': datetime.datetime.strptime(i['timestamp'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d %H:%M:%S'), 
                                'total': i['value']['inboundByteCount']+i['value']['outboundByteCount'], 
                                'inbound': i['value']['inboundByteCount'], 'outbound': i['value']['outboundByteCount']})

        flow_results = self.api_call.get_host_list(tag_id = id)
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
        ip = []; first_time = [];
        for i in flow_results:
            ip.append(i['subject']['ipAddress'])
            first_time.append(i['statistics']['firstActiveTime'])
        df = pd.DataFrame({'ip': ip, 'first_time': first_time})
        df['count'] = df.groupby('ip')['ip'].transform('count')
        df = df.drop_duplicates(['ip'], keep='first')
        host_list = df.to_dict('records')

        results = {'applications_traffic': applications_traffic, 'total_traffic': total_traffic, 'host_list': host_list}        
        return JsonResponse(results)

# Host Detail
class HostDetail(TemplateView):
    template_name = 'host_detail.html'
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        hostgroup_detail = self.api_call.get_hostgroup_detail(self.kwargs['id'])
        context['hostgroup_detail'] = hostgroup_detail
        context['host_ip'] = self.kwargs['ip']

        return context

class HostDetailData(View):
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get(self, request, id, ip):
        flow_results = self.api_call.get_host_list(source_ip = ip)
        
        application = []; 
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            # i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], '%Y-%m-%dT%H:%M:%S.%f+0000')+datetime.timedelta(hours=9)
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
            application.append(i['applicationId'])

        for i in self.tag_list:
            for j in flow_results:
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name


        df = pd.DataFrame({'id': application})
        df['count'] = df.groupby('id')['id'].transform('count')
        df = df.drop_duplicates(['id'], keep='first')
        application_list = df.to_dict('records')

        results = {'flow_results': flow_results, 'application_list': application_list}
        return JsonResponse(results)

# Host List
class HostList(TemplateView):
    template_name = 'host_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class HostListData(View):
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get(self, request):
        flow_results = self.api_call.get_host_list(record_limit=1000)
        for i in self.tag_list:
            for j in flow_results:
                if j['subject']['hostGroupIds'][0] == i.tagid:
                    j['subject']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name
        
        for i in flow_results:
            if i['subject'].get('hostGroupname'):
                pass
            else:
                print(i['subject'].get('hostGroupIds'))
                
        application = []; subject_name = []
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
            i['subject']['hostGroupIds'] = i['subject']['hostGroupIds'][0]
            i['peer']['hostGroupIds'] = i['peer']['hostGroupIds'][0]
            application.append(i['applicationId'])
            subject_name.append(i['subject']['hostGroupname'])
        
        df = pd.DataFrame({'id': application})
        df['count'] = df.groupby('id')['id'].transform('count')
        df = df.drop_duplicates(['id'], keep='first')
        application_list = df.to_dict('records')

        df = pd.DataFrame({'name': subject_name})
        df['count'] = df.groupby('name')['name'].transform('count')
        df = df.drop_duplicates(['name'], keep='first')
        subject_list = df.to_dict('records')

        results = {'results': flow_results, 'application_list': application_list, 
        'subject_list': subject_list
        }
        return JsonResponse(results)

# Flow Search
class FlowSearch(View):
    api_config = ConfingApi().config_api()
    api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
    tag_list = TagList.objects.all()

    def get(self, request):
        if request.GET.get('ip'):
            ip = request.GET.get('ip')
        else:
            ip = ''
        context = {'ip': ip}
        return render(request, 'flow_search.html', context)
    
    def post(self, request):
        time_range = request.POST['time']
        record_limit = request.POST['record']
        search_keyword = {'time_range': time_range, 'record_limit': record_limit}

        if request.POST['sourceip']:
            source_ip = request.POST['sourceip']
            search_keyword.update({'source_ip': source_ip})
            results = self.api_call.get_host_list(search_time = int(time_range), record_limit = int(record_limit), source_ip = source_ip)      
        else:
            results = self.api_call.get_host_list(search_time = int(time_range), record_limit = int(record_limit))

        if request.POST['sourceport']:
            source_port = request.POST['sourceport']
            search_keyword.update({'source_port': source_port})
            results = self.api_call.get_host_list(search_time = int(time_range), record_limit = int(record_limit), source_port = source_port)
        
        if request.POST['destinationport']:
            destination_port = request.POST['destinationport']
            search_keyword.update({'destination_port': destination_port})
            results = self.api_call.get_host_list(search_time = int(time_range), record_limit = int(record_limit), destination_port = destination_port)

        for i in self.tag_list:
            for j in results:
                if j['subject']['hostGroupIds'][0] == i.tagid:
                    j['subject']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name
        for i in results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], '%Y-%m-%dT%H:%M:%S.%f+0000').replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
        context = {'results': results, 'search_keyword': search_keyword}
        return render(request, 'searched_flow.html', context)