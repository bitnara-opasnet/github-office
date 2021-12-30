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
    path('account/<int:pk>/password', views.PasswordChangeView.as_view(), name='password_change'),

    # settings
    # path('settings/<int:pk>', views.ApiConfigView.as_view(), name='apiconfig'),
    path('settings', views.ApiConfigView.as_view(), name='apiconfig'),


    path('hostgroups/', views.HostGroupList.as_view(), name='hostgroup_list'),
    path('hostgroups/data/<int:hostgroup>', views.HostGroupListData.as_view(), name='hostgroup_list_data'),
    path('hostgroups/hostgroupdetail/<int:id>', views.HostGroupDetail.as_view(), name='hostgroup_detail'),
    path('hostgroups/hostgroupdetail/<int:hostgroup>/<int:id>/data', views.HostGroupDetailData.as_view(), name='hostgroup_detail_data'),
    path('hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>', views.HostDetail.as_view(), name='host_detail'),
    path('hostgroups/hostgroupdetail/<int:id>/hostdetail/<str:ip>/data', views.HostDetailData.as_view(), name='host_detail_data'),
    path('hostlist/', views.HostList.as_view(), name='host_list'),
    path('hostlist/data', views.HostListData.as_view(), name='host_list_data'),
    path('flowsearch/', views.FlowSearch.as_view(), name='flow_search'),


]