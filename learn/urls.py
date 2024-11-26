from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Course URLs
    path('', views.home , name="/"),
    path('service/', views.service),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/update/<int:pk>/', views.course_update, name='course_update'),
    path('courses/delete/<int:pk>/', views.course_delete, name='course_delete'),
    path('staff_list/', views.staff_list, name='staff_list'),
    path('add-question/', views.add_question_and_answers, name='add_question'),
    path('course_view/', views.course_list_view, name='course_list_view'),
    path('select-exam/', views.select_exam, name='select_exam'),
    path('your_courses/',views.your_courses, name='your_courses'),
    path('exam/<int:course_id>/<int:subject_id>/', views.exam_portal, name='exam_portal'),
    path('exam/<int:course_id>/<int:subject_id>/submit/', views.submit_exam, name='submit_exam'),

    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/update/<int:pk>/', views.subject_update, name='subject_update'),
    path('subjects/delete/<int:pk>/', views.subject_delete, name='subject_delete'),
    path('assign_course_and_subjects/', views.assign_course_and_subjects, name='assign_course_and_subjects'),
    path('subjects/subject_view/', views.subject_list_view, name='subject_list_view'),
    path('add-question/question_list/', views.question_list, name='question_list'),

    #register and login
    path('staff/register/', views.staff_register, name='staff_register'),
    path('student/register/', views.student_register, name='student_register'),
    path('login/', views.login_view, name='login'),
    path('login/', views.logout_view, name='logout'),

    #dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('approve_user/<int:user_id>/<str:user_type>/', views.approve_user, name='approve_user'),
    path('admin/reject_user/<int:user_id>/<str:user_type>/', views.reject_user, name='reject_user'),
]  

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
