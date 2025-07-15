from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('job/create/', views.job_create, name='job_create'),
    path('user/create/', views.user_create, name='user_create'),
    path('job/<int:job_id>/allot/', views.job_allotment, name='job_allotment'),
    path('job/<int:job_id>/report/', views.report_submit, name='report_submit'),
    path('report/<int:report_id>/verify/', views.report_verify, name='report_verify'),
    path('report/<int:report_id>/supervisor_verify/', views.supervisor_verify_user_report, name='supervisor_verify_user_report'),
    path('job/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
]

urlpatterns += [
    path('dashboard/admin/section/<str:section>/', views.admin_section, name='admin_section'),
    path('dashboard/admin/legacy/', views.legacy_admin_dashboard, name='legacy_admin_dashboard'),
    path('ajax/user_search/', views.ajax_user_search, name='ajax_user_search'),
    path('ajax/user_reset_password/', views.ajax_user_reset_password, name='ajax_user_reset_password'),
    path('user/section/<str:section>/', views.user_section, name='user_section'),
    path('supervisor/section/<str:section>/', views.supervisor_section, name='supervisor_section'),
] 