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

    # conversation
    path('conversation/summary/data/', views.ConversationTransactionSummaryData.as_view(), name='conversation_transaction_summary_data'),
    path('conversation/summary/', views.ConversationTransactionSummary.as_view(), name='conversation_transaction_summary'),
    path('conversation/flows/data/', views.ConversationTransactionFlowsData.as_view(), name='conversation_transaction_flow_data'),
    path('conversation/flows/', views.ConversationTransactionFlows.as_view(), name='conversation_transaction_flow'),

    # Flow status
    path('flowstatus/hostgroups/', views.FlowStatusbyGroup.as_view(), name='flow_status_by_hostgroups'),
    path('flowstatus/hostgroups/data/<int:hostgroup>/', views.FlowStatusbyGroupData.as_view(), name='flow_status_by_hostgroups_data'),
    path('flowstatus/hostgroups/hostgroupdetail/<int:id>/', views.FlowStatusbyGroupDetail.as_view(), name='flow_status_by_hostgroup_detail'),
    path('flowstatus/hostgroups/hostgroupdetail/<int:hostgroup>/<int:id>/data/', views.FlowStatusbyGroupDetailData.as_view(), name='flow_status_by_hostgroup_detail_data'),
    path('flowstatus/hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/', views.FlowStatusbyGroupHostDetail.as_view(), name='flow_status_by_hostgroup_host_detail'),
    path('flowstatus/hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/data/', views.FlowStatusbyGroupHostDetailData.as_view(), name='flow_status_by_hostgroup_host_detail_data'),
    path('flowstatus/applications/', views.FlowStatusbyApplication.as_view(), name='flow_status_by_application'),
    path('flowstatus/applications/data/', views.FlowStatusbyApplicationData.as_view(), name='flow_status_by_application_data'),
    path('flowstatus/applications/<int:id>/', views.FlowStatusbyApplicationDetail.as_view(), name='flow_status_by_application_detail'),
    path('flowstatus/applications/<int:id>/data/', views.FlowStatusbyApplicationDetailData.as_view(), name='flow_status_by_application_detail_data'),
    path('flowstatus/allflows/', views.FlowStatusAllFlows.as_view(), name='flow_status_all_flows'),
    path('flowstatus/allflows/data/', views.FlowStatusAllFlowsData.as_view(), name='flow_status_all_flows_data'),
    path('flowstatus/flowsearch/', views.FlowStatusFlowSearch.as_view(), name='flow_status_flow_search'),
    path('flowstatus/flowsearch/data', views.FlowStatusFlowSearchData.as_view(), name='flow_status_flow_search_data'),

    # path('hostgroups/hostgroupdetail/port', views.HostGroupsDetailPort.as_view(), name='hostgroups_detail_port'),
    path('flowstatus/allflows/port/', views.HostListPort.as_view(), name='host_list_port'),

]