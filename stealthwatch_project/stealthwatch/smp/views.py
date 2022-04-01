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

import csv
import json
import datetime
import pytz
import pandas as pd
from collections import Counter
import pickle

from lib.api_call import ApiCall, ConfingApi
from lib.portnum_to_name import CSVFileIO
from lib.data_call import read_json

csv_file_io = CSVFileIO('service-names-port-numbers.csv', ',')
port_dict = csv_file_io.transfer_portname()
csv_file_io = CSVFileIO('country_code_flags.csv', ',')
flag_dict = csv_file_io.get_flag_url()

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

# Conversation summary
class ConversationTransactionSummary(TemplateView):
    template_name = 'conversation_transaction_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ConversationTransactionSummaryData(View):
    def get(self, request):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        conversations_flow_results = api_call.get_flow_reports(search_item='top-conversations')
        # conversations_flow_results = read_json('get_reports_top-conversations.json')
        
        final_list = []
        if conversations_flow_results:
            for i in conversations_flow_results['results']:
                results = {}
                results['port'] = i['portProtocol']['port']
                results['protocol'] = i['portProtocol']['protocol']
                # service 이름 정의 여부 확인 ex) 'https'
                if i['portProtocol'].get('service'):
                    if i['portProtocol']['service'].get('name'):
                        results['name'] = i['portProtocol']['service']['name']
                    else:
                        results['name'] = 'Unassigned' 
                else:
                    results['name'] = 'Unassigned'
                final_list.append(results)

            # port, protocol별 개수 count
            df = pd.DataFrame(final_list)
            df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')
            port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
            udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
            tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

            results = {'conversations_flow_results': conversations_flow_results, 'udp_list': udp_list, 'tcp_list': tcp_list}
        return JsonResponse(results)

# Conversation flow
class ConversationTransactionFlows(TemplateView):
    template_name = 'conversation_transaction_flows.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ConversationTransactionFlowsData(View):
    def get(self, request):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        # conversations_flow_results = read_json('get_reports_top-conversations.json')
        conversations_flow_results = api_call.get_flow_reports(search_item='top-conversations')
        if conversations_flow_results:
            # host group id - host group name 매핑
            for i in tag_list:
                for j in conversations_flow_results['results']:
                    if j['host']['hostGroupIds'][0] == i.tagid:
                        j['host']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            # host country - flag 매핑
            for i in conversations_flow_results['results']:
                if i['host']['country'] in flag_dict:
                    i['host']['flag'] = flag_dict.get(i['host']['country'])
                else:
                    i['host']['flag'] = ''

        results = {'conversations_flow_results': conversations_flow_results}
        return JsonResponse(results)


# Flow Status
class FlowStatusbyGroup(TemplateView):
    template_name = 'flow_status_by_hostgroups.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)

        # hostgroup이 1이면 inside gorup, 0이면 outside그룹, default=1
        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1
        hostgroups_list = read_json('tag_list.json')
        # hostgroups_list = api_call.get_hostgroup_list()

        if hostgroups_list:
            for i in hostgroups_list[0]['root']:  
                if i['id'] == int(hostgroup):
                    host_list = i['children']
            context['host_list'] = host_list
        else:
            context['host_list'] = None
        context['hostgroup'] = hostgroup
        return context

class FlowStatusbyGroupData(View):
    def get(self, request, hostgroup):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        results = {}

        # hostgroups_traffic = read_json('get_traffic_data.json')
        hostgroups_traffic = api_call.get_hostgroups_traffic()
        # print(hostgroups_traffic)
        
        if hostgroups_traffic: 
            for i in hostgroups_traffic[0]['resultDto']:
                if i['rootTagId'] == int(hostgroup):
                    insidegroup_traffic = i['tagTraffic']
            for i in tag_list:
                for j in insidegroup_traffic:
                    if j['tagId'] == i.tagid:
                        j['name'] = i.name
            results['results'] = insidegroup_traffic
        else: 
            results['results'] = None

        return JsonResponse(results)

class FlowStatusbyGroupDetail(TemplateView):
    template_name = 'flow_status_by_hostgroups_detail.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)

        # hostgroup detail 정보 호출
        # hostgroup_detail = read_json('tag_details.json')
        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])
        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1
        # print(hostgroup)

        # hostgroup 목록 호출
        # hostgroups_list = read_json('tag_list.json')
        hostgroups_list = api_call.get_hostgroup_list()
        if hostgroups_list:
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

class FlowStatusbyGroupDetailData(View):
    def get(self, request, **args):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        # print(self.kwargs['id'])

        # hostgroup flow 호출
        # flow_results = read_json('get_flow_data_group.json')
        flow_results = api_call.get_host_list(source_group = self.kwargs['id'])
        now = datetime.datetime.now()

        if flow_results:
            # hostgroup name 매핑
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            final_list = []
            for i in flow_results:
                # last active time 형태 변경
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S') 

                # application name 매핑
                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
                
                # country - flag 매핑
                if i['subject']['countryCode'] in flag_dict:
                    i['subject']['flag'] = flag_dict.get(i['subject']['countryCode'])
                else:
                    i['subject']['flag'] = ''

                # chart를 그리기 위한 dict생성
                result = {}
                result['ipAddress'] = i['subject']['ipAddress']
                result['firstActiveTime'] = i['statistics']['firstActiveTime']
                if i['subject'].get('hostGroupname'): 
                    result['hostGroupname'] = i['subject']['hostGroupname']
                else:
                    result['hostGroupname'] = i['subject']['hostGroupIds'][0]      
                result['protocol'] = i['peer']['portProtocol']['protocol']
                result['port'] = i['peer']['portProtocol']['port']
                result['applicationName'] = i['applicationName']
                result['countryCode'] = i['subject']['countryCode']
                result['countryflag'] = i['subject']['flag']
                result['bps'] = i['statistics']['byteRate']
                result['rtt'] = i['statistics']['rttAverage']
                result['lastActiveTime'] = i['statistics']['lastActiveTime']
                final_list.append(result)

            df = pd.DataFrame(final_list)
            df['flow_count'] = df.groupby('ipAddress')['ipAddress'].transform('count')
            df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')
            
            host_list = df.drop_duplicates(['ipAddress'], keep='first').to_dict('records')
            port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
            udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
            tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

            # bps array 생성
            chart_df = df.set_index('lastActiveTime', drop=False)
            endtime = now - datetime.timedelta(minutes=5)
            end_timestamp = endtime.strftime('%Y-%m-%d %H:%M:%S')
            time_df = pd.DataFrame({'time_stamp': pd.date_range(end_timestamp, periods=300, freq='S'), 'time_range':[i for i in range(1, 301)]})
            time_df = time_df.set_index('time_stamp')
            result_df = pd.merge(chart_df, time_df, left_index=True, right_index=True, how="right")
            result_df = result_df.fillna(0)
            chart_results = result_df.to_dict('records')

            results = {'host_list': host_list, 'udp_list': udp_list, 'tcp_list': tcp_list, 'chart_results': chart_results, 
                    # 'flow_results': flow_results, 
                    }

        return JsonResponse(results)

# Host Detail
class FlowStatusbyGroupHostDetail(TemplateView):
    template_name = 'flow_status_by_hostgroups_host_detail.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)
       
        # hostgroup_detail = read_json('tag_details.json')
        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])
        context['hostgroup_detail'] = hostgroup_detail
        context['host_ip'] = self.kwargs['ip']

        return context

class FlowStatusbyGroupHostDetailData(View):

    def get(self, request, **args):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        # flow_results = read_json('get_flow_data_ip.json')
        flow_results = api_call.get_host_list(source_ip = self.kwargs['ip'])
        now = datetime.datetime.now()

        if flow_results: 
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            chart_list = []
            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            for i in flow_results:
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')        
                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
                if i['subject'].get('hostGroupname') == None: 
                    i['subject']['hostGroupname'] = i['subject']['hostGroupIds'][0]

                result = {}
                result['protocol'] = i['peer']['portProtocol']['protocol']
                result['port'] = i['peer']['portProtocol']['port']
                result['application'] = i['applicationName']

                result['bps'] = i['statistics']['byteRate']
                result['rtt'] = i['statistics']['rttAverage']
                result['lastActiveTime'] = i['statistics']['lastActiveTime']
                result['destination_ip'] = i['peer']['ipAddress']
                chart_list.append(result)
             
            # bps array 생성
            chart_df = pd.DataFrame(chart_list)
            chart_df = chart_df.set_index('lastActiveTime', drop=False)
            endtime = now - datetime.timedelta(minutes=5)
            end_timestamp = endtime.strftime('%Y-%m-%d %H:%M:%S')
            time_df = pd.DataFrame({'time_stamp':pd.date_range(end_timestamp, periods=300, freq='S'), 'time_range':[i for i in range(1, 301)]})
            time_df = time_df.set_index('time_stamp')
            result_df = pd.merge(chart_df, time_df, left_index=True, right_index=True, how="right")
            result_df = result_df.fillna(0)
            chart_results = result_df.to_dict('records')

            chart_df['port_count'] = chart_df.groupby(['protocol','port'])['protocol'].transform('count')
            port_df = chart_df.drop_duplicates(['protocol', 'port'], keep='first')
            udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
            tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')       
        results = {"flow_results": flow_results, "chart_results": chart_results, 'udp_list': udp_list, 'tcp_list': tcp_list}
        return JsonResponse(results)

# flow by application
class FlowStatusbyApplication(TemplateView):
    template_name = 'flow_status_by_application.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class FlowStatusbyApplicationData(View):
    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)

        # applications_flow_results = read_json('get_reports_top-applications.json')
        applications_flow_results = api_call.get_flow_reports(search_item='top-applications')
        applications_traffic_results = api_call.get_application_traffic()
        # print(applications_traffic_results)

        results = {'applications_flow_results': applications_flow_results, 'applications_traffic_results': applications_traffic_results}
        with open('flow_status_application.txt', 'wb') as f:
            pickle.dump(results, f)
        
        return JsonResponse(results)

class FlowStatusbyApplicationDetail(TemplateView):
    template_name = 'flow_status_by_application_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application_id'] = self.kwargs['id']
        return context

class FlowStatusbyApplicationDetailData(View):
    def get(self, request, **args):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        # flow_results = read_json('get_flow_data_application.json')
        flow_results = api_call.get_host_list(application_id = self.kwargs['id'])

        if flow_results:
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            with open('flow_status_application.txt', 'rb') as f:
                data = pickle.load(f)['applications_flow_results']['results']

            applications_results = {}
            for i in data:
                if i['application']['id'] == self.kwargs['id']:
                    applications_results = i
            application_name = applications_results['application']['name']
            
            final_list = []
            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            for i in flow_results:
                i['application_name'] = applications_results['application']['name']
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')    
                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
                if i['subject']['countryCode'] in flag_dict:
                    i['subject']['flag'] = flag_dict.get(i['subject']['countryCode'])
                else:
                    i['subject']['flag'] = ''

                result = {}
                result['subject_name'] = i['subject']['hostGroupname']
                final_list.append(result)

            df = pd.DataFrame(final_list)
            df['subject_count'] = df.groupby('subject_name')['subject_name'].transform('count')
            subject_list = df.drop_duplicates(['subject_name'], keep='first').to_dict('records')

        results = {'flow_results': flow_results, 'subject_list': subject_list, 'application_name': application_name}
        return JsonResponse(results)


# all flows
class FlowStatusAllFlows(TemplateView):
    template_name = 'flow_status_all_flows.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class FlowStatusAllFlowsData(View):
    def get(self, request):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        flow_results = api_call.get_host_list(record_limit=1000)
        # flow_results = read_json('get_flow_data.json')
        now = datetime.datetime.now()

        if flow_results:
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name
                    
            final_list = []
            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            for i in flow_results:
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')   
                i['subject']['hostGroupIds'] = i['subject']['hostGroupIds'][0]
                i['peer']['hostGroupIds'] = i['peer']['hostGroupIds'][0]

                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
                if i['subject']['countryCode'] in flag_dict:
                    i['subject']['flag'] = flag_dict.get(i['subject']['countryCode'])
                else:
                    i['subject']['flag'] = ''

                # result 딕셔너리 생성
                result = {}
                result['subject_name'] = i['subject']['hostGroupname']
                result['protocol'] = i['peer']['portProtocol']['protocol']
                result['port'] = i['peer']['portProtocol']['port']
                result['application'] = i['applicationName']
                result['bps'] = i['statistics']['byteRate']
                result['rtt'] = i['statistics']['rttAverage']
                result['lastActiveTime'] = i['statistics']['lastActiveTime']
                result['source_ip'] = i['subject']['ipAddress']
                final_list.append(result)

            # final list 딕셔너리로 dataframe 생성
            df = pd.DataFrame(final_list)
            df['subject_count'] = df.groupby('subject_name')['subject_name'].transform('count')
            df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')
            
            subject_list = df.drop_duplicates(['subject_name'], keep='first').to_dict('records')
            port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
            udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
            tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

            # bps array 생성
            chart_df = df.set_index('lastActiveTime', drop=False)
            endtime = now - datetime.timedelta(minutes=5)
            end_timestamp = endtime.strftime('%Y-%m-%d %H:%M:%S')
            time_df = pd.DataFrame({'time_stamp':pd.date_range(end_timestamp, periods=300, freq='S'), 'time_range':[i for i in range(1, 301)]})
            time_df = time_df.set_index('time_stamp')
            result_df = pd.merge(chart_df, time_df, left_index=True, right_index=True, how="right")
            result_df = result_df.fillna(0)
            chart_results = result_df.to_dict('records')
            results = {'results': flow_results, 'subject_list': subject_list, 'udp_list': udp_list, 'tcp_list': tcp_list, 'chart_results': chart_results
            }
        return JsonResponse(results)

class HostListPort(TemplateView):
    template_name = 'host_list_port.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# flow search
class FlowStatusFlowSearch(View):

    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = {}

        if request.GET.get('ip'):
            ip = request.GET.get('ip')
        else:
            ip = ''
        context['ip'] = ip

        # hostgroup이 1이면 inside gorup, 0이면 outside그룹, default=1
        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1
        # hostgroups_list = read_json('tag_list.json')
        hostgroups_list = api_call.get_hostgroup_list()

        if hostgroups_list:
            for i in hostgroups_list[0]['root']:  
                if i['id'] == int(hostgroup):
                    host_list = i['children']
            context['host_list'] = host_list
        else:
            context['host_list'] = None
        context['hostgroup'] = hostgroup

        with open('flow_status_application.txt', 'rb') as f:
            data = pickle.load(f)['applications_flow_results']['results']

        application_list  =[]
        for i in data:
            applications_results = {}
            applications_results['id'] = i['application']['id']
            applications_results['name'] = i['application']['name']
            application_list.append(applications_results)
        context['application_list'] = application_list
        # print(application_list)
        return render(request, 'flow_status_flow_search.html', context)
    
    def post(self, request):
        context = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        date_format = '%Y/%m/%d %H:%M'
        timeq = request.POST['timeq']
        time_list = timeq.split(' - ')
        time_range = (datetime.datetime.strptime(time_list[1], date_format) - datetime.datetime.strptime(time_list[0], date_format)).seconds/60
        # print(time_range)
        record_limit = request.POST['record']
        search_keyword = {'search_time': int(time_range), 'record_limit': int(record_limit)}

        with open('flow_status_application.txt', 'rb') as f:
            data = pickle.load(f)['applications_flow_results']['results']

        if request.POST['applicationid']:
            application_id = request.POST['applicationid']
            search_keyword.update({'application_id': application_id})

            applications_results = {}
            for i in data:
                if i['application']['id'] == int(application_id):
                    applications_results = i['application']
            context['applications'] = applications_results

        if request.POST['sourceip']:
            source_ip = request.POST['sourceip']
            search_keyword.update({'source_ip': source_ip})

        if request.POST['sourceport']:
            source_port = request.POST['sourceport']
            search_keyword.update({'source_port': source_port})

        if request.POST['sourcegroup']:
            source_group = request.POST['sourcegroup']
            search_keyword.update({'source_group': source_group})
            sourcegroup_resuslts = {}
            for i in tag_list:
                if i.tagid == int(source_group):
                    sourcegroup_resuslts['id']= i.tagid
                    sourcegroup_resuslts['name']= i.name
            context['sourcegroup'] = sourcegroup_resuslts

        if request.POST['destinationport']:
            destination_port = request.POST['destinationport']
            search_keyword.update({'destination_port': destination_port})
        
        if request.POST['destinationip']:
            destination_ip = request.POST['destinationip']
            search_keyword.update({'destination_ip': destination_ip})

        if request.POST['destinationgroup']:
            destination_group = request.POST['destinationgroup']
            search_keyword.update({'destination_group': destination_group})
            destinationgroup_resuslts = {}
            for i in tag_list:
                if i.tagid == int(destination_group):
                    destinationgroup_resuslts['id']= i.tagid
                    destinationgroup_resuslts['name']= i.name
            context['destinationgroup'] = destination_group

        # print(search_keyword)
        context['search_keyword'] = search_keyword
        results = api_call.get_host_list(**search_keyword)      
        if results:
            for i in tag_list:
                for j in results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            for i in results:
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], '%Y-%m-%dT%H:%M:%S.%f+0000').replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
            context['results'] = results
        
        return render(request, 'flow_status_searched_flow.html', context)

class FlowStatusFlowSearchData(View):
    def get(self, request):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        flow_results = api_call.get_host_list(record_limit=1000)
        # flow_results = read_json('get_flow_data.json')
        if flow_results: 
            # host group id - host group name 매핑
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            for i in flow_results:
                i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')   
                i['subject']['hostGroupIds'] = i['subject']['hostGroupIds'][0]
                i['peer']['hostGroupIds'] = i['peer']['hostGroupIds'][0]
                if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                    i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
                else:
                    i['applicationName'] = 'Unassigned'
                if i['subject']['countryCode'] in flag_dict:
                    i['subject']['flag'] = flag_dict.get(i['subject']['countryCode'])
                else:
                    i['subject']['flag'] = ''

            results = {'flow_results': flow_results}
        return JsonResponse(results)