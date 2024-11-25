"""
URL configuration for stock_taker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stocker import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    #시작 페이지
    path('', views.login_view, name='login'),
    
    #로그인
    path('signup/', views.signup_view, name='signup'),
    path('index/', views.index_view, name='index'),
    path('logout/', views.logout_view, name='logout'),  # 로그아웃 URL 추가
    path('add_adm/', views.add_adm, name='add_adm'),  # 관리자 페이지 URL 추가
    
    #관리자 페이지에서 이용
    path('add_icategory/', views.add_icategory, name='add_icategory'),
    path('add_lcategory/', views.add_lcategory, name='add_lcategory'),
    path('add_item/', views.add_item, name='add_item'),
    path('add_location/', views.add_location, name='add_location'),
    
    #index 페이지에서 이용
    path('store_item/', views.store_item, name='store_item'),
    path('use_item/', views.use_item, name='use_item'),
    path('recommend_storage/', views.recommend_storage, name='recommend_storage'),
    path('get_items_and_locations/', views.get_items_and_locations, name='get_items_and_locations'),
    
    
    
]
