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

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1
        # print(hostgroup)
        hostgroups_list = api_call.get_hostgroup_list()
        # hostgroups_list = read_json('get_tag_list.json')
        if hostgroups_list:
            for i in hostgroups_list[0]['root']:  
                if i['id'] == int(hostgroup):
                    host_list = i['children']
            context['host_list'] = host_list
        else:
            context['hostgroup_detail'] = None
        context['hostgroup'] = hostgroup
        return context

class HostGroupListData(View):
    def get(self, request, hostgroup):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        results = {}
        print(hostgroup)
        hostgroups_traffic = api_call.get_hostgroups_traffic()
        
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

# Host Group Detail
class HostGroupDetail(TemplateView):
    template_name = 'hostgroups_detail.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)

        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])
        # hostgroup_detail = read_json('get_tag_details.json')

        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1
        print(hostgroup)

        hostgroups_list = api_call.get_hostgroup_list()
        # hostgroups_list = read_json('get_tag_list.json')
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

class HostGroupDetailData(View):
    def getKey(self, list) :
        return list['total']

    def get(self, request, id, hostgroup):
        results = {}
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        print(hostgroup)

        if hostgroup == 1:
            traffic_result = api_call.get_traffic(tag_id = id)
        else:
            traffic_result = api_call.get_traffic_outside(tag_id = id)
        
        total_traffic = []
        if traffic_result:
            for i in traffic_result['data']:
                total_traffic.append({'timestamp': datetime.datetime.strptime(i['timestamp'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y/%m/%d %H:%M:%S'), 
                                    'total': i['value']['inboundByteCount']+i['value']['outboundByteCount'], 
                                    'inbound': i['value']['inboundByteCount'], 'outbound': i['value']['outboundByteCount']}) 

        flow_results = api_call.get_host_list(tag_id = id)
        # flow_results = read_json('get_flow_data.json')
        # print(len(flow_results))
        if flow_results:
            for i in tag_list:
                for j in flow_results:
                    if j['subject']['hostGroupIds'][0] == i.tagid:
                        j['subject']['hostGroupname'] = i.name
                    if j['peer']['hostGroupIds'][0] == i.tagid:
                        j['peer']['hostGroupname'] = i.name

            date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
            final_list = []
            for i in flow_results:   
                i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
                i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
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
                result['ipAddress'] = i['subject']['ipAddress']
                result['firstActiveTime'] = i['statistics']['firstActiveTime']
                if i.get('subject').get('hostGroupname'): 
                    result['hostGroupname'] = i['subject']['hostGroupname']
                else:
                    result['hostGroupname'] = i['subject']['hostGroupIds'][0]      
                result['protocol'] = i['peer']['portProtocol']['protocol']
                result['port'] = i['peer']['portProtocol']['port']
                result['applicationName'] = i['applicationName']
                result['countryCode'] = i['subject']['countryCode']
                result['countryflag'] = i['subject']['flag']
                final_list.append(result)

            df = pd.DataFrame(final_list)
            df['flow_count'] = df.groupby('ipAddress')['ipAddress'].transform('count')
            df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')

            host_list = df.drop_duplicates(['ipAddress'], keep='first').to_dict('records')
            port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
            udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
            tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

            results = {'total_traffic': total_traffic, 'udp_list': udp_list, 'tcp_list': tcp_list,
                    'host_list': host_list
                    }
            with open('hostgroup_detail.txt', 'wb') as f:
                pickle.dump(flow_results, f)
        return JsonResponse(results)

# hostgroups detail port        
class HostGroupsDetailPort(TemplateView):
    template_name = 'hostgroups_detail_port.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)

        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])

        if self.request.GET.get('hostgroup'):
            hostgroup = self.request.GET.get('hostgroup')
        else:
            hostgroup = 1

        if hostgroup_detail: 
            context['hostgroup_detail'] = hostgroup_detail
        else:
            context['hostgroup_detail'] = None
        context['hostgroup'] = hostgroup
        return context

# Host Detail
class HostDetail(TemplateView):
    template_name = 'host_detail.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)
       
        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])
        # hostgroup_detail = read_json('get_tag_details.json')
        context['hostgroup_detail'] = hostgroup_detail
        context['host_ip'] = self.kwargs['ip']

        return context

class HostDetailData(View):

    def get(self, request, id, ip):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()
        flow_results = api_call.get_host_list(source_ip = ip)
        # with open('hostgroup_detail.txt', 'rb') as f:
        #     data = pickle.load(f)
        
        # flow_results = []
        # for i in data:
        #     if i['subject']['ipAddress'] == ip:
        #         flow_results.append(i)

        for i in tag_list:
            for j in flow_results:
                if j['subject']['hostGroupIds'][0] == i.tagid:
                    j['subject']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name

        bps_list = []
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
            i['statistics']['lastActiveTime'] = datetime.datetime.strptime(i['statistics']['lastActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['lastActiveTime'] = i['statistics']['lastActiveTime'].strftime('%Y-%m-%d %H:%M:%S')        
            if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
            else:
                i['applicationName'] = 'Unassigned'
            if i.get('subject').get('hostGroupname') == None: 
                i['subject']['hostGroupname'] = i['subject']['hostGroupIds'][0]

            result = {}
            result['bps'] = i['statistics']['byteRate']
            result['lastActiveTime'] = i['statistics']['lastActiveTime']
            result['destination_ip'] = i['peer']['ipAddress']
            bps_list.append(result)
    
        # bps array 생성
        bps_df = pd.DataFrame(bps_list)
        bps_df = bps_df.set_index('lastActiveTime', drop=False)
        endtime = datetime.datetime.now()-datetime.timedelta(minutes=5)
        end_timestamp = endtime.strftime('%Y-%m-%d %H:%M:%S')
        time_df = pd.DataFrame({'time_stamp':pd.date_range(end_timestamp, periods=300, freq='S'), 'time_range':[i for i in range(1, 301)]})
        time_df = time_df.set_index('time_stamp')
        result_df = pd.merge(bps_df, time_df, left_index=True, right_index=True, how="right")
        result_df = result_df.fillna(0)
        bps = result_df.to_dict('records')

        results = {"flow_results": flow_results, "bps": bps}
        return JsonResponse(results)

# Host List
class HostList(TemplateView):
    template_name = 'host_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class HostListData(View):
    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        flow_results = api_call.get_host_list(record_limit=1000)
        for i in tag_list:
            for j in flow_results:
                if j['subject']['hostGroupIds'][0] == i.tagid:
                    j['subject']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name
        
        # for i in flow_results:
        #     if i['subject'].get('hostGroupname'):
        #         pass
        #     else:
        #         print(i['subject'].get('hostGroupIds'))
                
        application = []
        subject_name = []
        destination_port = []
        destination_protocol = []
        date_format = '%Y-%m-%dT%H:%M:%S.%f+0000'
        for i in flow_results:
            i['statistics']['firstActiveTime'] = datetime.datetime.strptime(i['statistics']['firstActiveTime'], date_format).replace(tzinfo=pytz.utc).astimezone()
            i['statistics']['firstActiveTime'] = i['statistics']['firstActiveTime'].strftime('%Y-%m-%d %H:%M:%S')
            i['subject']['hostGroupIds'] = i['subject']['hostGroupIds'][0]
            i['peer']['hostGroupIds'] = i['peer']['hostGroupIds'][0]

            if str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower() in port_dict:
                i['applicationName'] = port_dict.get(str(i['peer']['portProtocol']['port'])+i['peer']['portProtocol']['protocol'].lower())
            else:
                i['applicationName'] = 'Unassigned'

            subject_name.append(i['subject']['hostGroupname'])
            destination_port.append(i['peer']['portProtocol']['port'])
            destination_protocol.append(i['peer']['portProtocol']['protocol'])
            application.append(i['applicationName'])

        df = pd.DataFrame({'name': subject_name})
        df['count'] = df.groupby('name')['name'].transform('count')
        df = df.drop_duplicates(['name'], keep='first')
        subject_list = df.to_dict('records')

        df = pd.DataFrame({'protocol': destination_protocol, 'port': destination_port, 'application': application})
        df['count'] = df.groupby(['protocol','port'])['protocol'].transform('count')
        df = df.drop_duplicates(['protocol', 'port'], keep='first')
        udp_list = df[df['protocol'] == 'UDP'].to_dict('records')
        tcp_list = df[df['protocol'] == 'TCP'].to_dict('records')
        # portprotocol_list = df.to_dict('records')

        results = {'results': flow_results, 'subject_list': subject_list, 'udp_list': udp_list, 'tcp_list': tcp_list, 
        }
        return JsonResponse(results)

class HostListPort(TemplateView):
    template_name = 'host_list_port.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# Flow Search
class FlowSearch(View):

    def get(self, request):
        if request.GET.get('ip'):
            ip = request.GET.get('ip')
        else:
            ip = ''
        context = {'ip': ip}
        return render(request, 'flow_search.html', context)
    
    def post(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        time_range = request.POST['time']
        record_limit = request.POST['record']
        search_keyword = {'search_time': int(time_range), 'record_limit': int(record_limit)}

        if request.POST['sourceip']:
            source_ip = request.POST['sourceip']
            search_keyword.update({'source_ip': source_ip})

        if request.POST['sourceport']:
            source_port = request.POST['sourceport']
            search_keyword.update({'source_port': source_port})

        if request.POST['destinationport']:
            destination_port = request.POST['destinationport']
            search_keyword.update({'destination_port': destination_port})

        results = api_call.get_host_list(**search_keyword)      

        for i in tag_list:
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

# top flow report 
class TopFlowReport(TemplateView):
    template_name = 'top_flow_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)

        hosts_flow_results = api_call.get_flow_reports(search_item='top-hosts', maxRows=10)
        services_flow_results = api_call.get_flow_reports(search_item='top-services', maxRows=10)
        applications_flow_results = api_call.get_flow_reports(search_item='top-applications', maxRows=10)
        conversations_flow_results = api_call.get_flow_reports(search_item='top-conversations', maxRows=10)

        context['hosts_flow_results'] = hosts_flow_results['results']
        context['services_flow_results'] = services_flow_results['results']
        context['applications_flow_results'] = applications_flow_results['results']
        context['conversations_flow_results'] = conversations_flow_results['results']
        return context

class SummaryFlowHosts(TemplateView):
    template_name = 'summary_host_flow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SummaryFlowHostsData(View):
    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        hosts_flow_results = api_call.get_flow_reports(search_item='top-hosts')

        for i in tag_list:
            for j in hosts_flow_results['results']:
                if j['host']['hostGroupIds'][0] == i.tagid:
                    j['host']['hostGroupname'] = i.name

        for i in hosts_flow_results['results']:
            if i['host']['country'] in flag_dict:
                i['host']['flag'] =  flag_dict.get(i['host']['country'])
            else:
                i['host']['flag'] = ''
        
        results = {'hosts_flow_results': hosts_flow_results}
        return JsonResponse(results)

class SummaryFlowApplications(TemplateView):
    template_name = 'summary_applications_flow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SummaryFlowApplicationsData(View):
    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)

        applications_flow_results = api_call.get_flow_reports(search_item='top-applications')

        results = {'applications_flow_results': applications_flow_results}
        return JsonResponse(results)

class SummaryFlowConversations(TemplateView):
    template_name = 'summary_conversations_flow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SummaryFlowConversationsData(View):
    def get(self, request):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        conversations_flow_results = api_call.get_flow_reports(search_item='top-conversations')
        # conversations_flow_results = read_json('get_reports_top-conversations.json')

        # for i in conversations_flow_results['results']:
        #     if i.get('portProtocol').get('service'):
        #         pass
        #     else:
        #         print(i)

        for i in tag_list:
            for j in conversations_flow_results['results']:
                if j['host']['hostGroupIds'][0] == i.tagid:
                    j['host']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name

        results = {'conversations_flow_results': conversations_flow_results}
        return JsonResponse(results)
    
class ApplicationHostDetail(TemplateView):
    template_name = 'host_detail_application.html'

    def get_context_data(self, **kwargs):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        context = super().get_context_data(**kwargs)

        hostgroup_detail = api_call.get_hostgroup_detail(self.kwargs['id'])
        context['hostgroup_detail'] = hostgroup_detail
        context['host_ip'] = self.kwargs['ip']

        return context

class ApplicationHostDetailData(View):
    def get(self, request, id, ip):
        api_config = ConfingApi().config_api()
        api_call = ApiCall(api_config.ipaddress, api_config.username, api_config.password)
        tag_list = TagList.objects.all()

        conversations_flow_results = api_call.get_flow_reports(search_item='top-conversations', ipaddress=ip)
        for i in tag_list:
            for j in conversations_flow_results['results']:
                if j['host']['hostGroupIds'][0] == i.tagid:
                    j['host']['hostGroupname'] = i.name
                if j['peer']['hostGroupIds'][0] == i.tagid:
                    j['peer']['hostGroupname'] = i.name

        final_list = []
        for i in conversations_flow_results['results']:
            result = {}
            result['protocol'] = i['portProtocol']['protocol']
            result['port'] = i['portProtocol']['port']

            if i.get('portProtocol').get('service').get('name'):
                result['applicationName'] = i.get('portProtocol').get('service').get('name')
                # result['applicationName'] = i['portProtocol']['service']['name']
            else:
                result['applicationName'] = 'Unassigned'

            final_list.append(result)

        df = pd.DataFrame(final_list)
        df['port_count'] = df.groupby(['protocol','port'])['protocol'].transform('count')

        port_df = df.drop_duplicates(['protocol', 'port'], keep='first')
        udp_list = port_df[port_df['protocol'] == 'UDP'].to_dict('records')
        tcp_list = port_df[port_df['protocol'] == 'TCP'].to_dict('records')

        results = {'udp_list': udp_list, 'tcp_list': tcp_list, 'conversations_flow_results': conversations_flow_results}
        return JsonResponse(results)