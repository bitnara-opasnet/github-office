from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[
    path('', views.index, name='index'),

    # user
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('account/<int:pk>/detail', views.UserDetailView.as_view(), name='user_detail'),
    path('account/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('account/<int:pk>/password/', views.PasswordChangeView.as_view(), name='password_change'),

    # settings
    # path('settings/<int:pk>', views.ApiConfigView.as_view(), name='apiconfig'),
    path('settings/', views.ApiConfigView.as_view(), name='apiconfig'),


    path('hostgroups/', views.HostGroupList.as_view(), name='hostgroup_list'),
    path('hostgroups/data/<int:hostgroup>/', views.HostGroupListData.as_view(), name='hostgroup_list_data'),
    path('hostgroups/hostgroupdetail/<int:id>/', views.HostGroupDetail.as_view(), name='hostgroup_detail'),
    path('hostgroups/hostgroupdetail/<int:hostgroup>/<int:id>/data/', views.HostGroupDetailData.as_view(), name='hostgroup_detail_data'),
    path('hostgroups/hostgroupdetail/port', views.HostGroupsDetailPort.as_view(), name='hostgroups_detail_port'),
    path('hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/', views.HostDetail.as_view(), name='host_detail'),
    path('hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/data/', views.HostDetailData.as_view(), name='host_detail_data'),
    path('hostlist/', views.HostList.as_view(), name='host_list'),
    path('hostlist/data/', views.HostListData.as_view(), name='host_list_data'),
    path('hostlist/port/', views.HostListPort.as_view(), name='host_list_port'),

    path('flowsearch/', views.FlowSearch.as_view(), name='flow_search'),

    path('flowreport/', views.TopFlowReport.as_view(), name='flow_report'),
    path('flowreport/hosts/data', views.SummaryFlowHostsData.as_view(), name='summary_flow_host_data'),
    path('flowreport/hosts', views.SummaryFlowHosts.as_view(), name='summary_flow_host'),
    path('flowreport/applications/data', views.SummaryFlowApplicationsData.as_view(), name='summary_flow_applications_data'),
    path('flowreport/applications', views.SummaryFlowApplications.as_view(), name='summary_flow_applications'),
    path('flowreport/conversations/data', views.SummaryFlowConversationsData.as_view(), name='summary_flow_conversations_data'),
    path('flowreport/conversations', views.SummaryFlowConversations.as_view(), name='summary_flow_conversations'),

    path('application/hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/', views.ApplicationHostDetail.as_view(), name='application_host_detail'),
    path('application/hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/data/', views.ApplicationHostDetailData.as_view(), name='application_host_detail_data'),
]