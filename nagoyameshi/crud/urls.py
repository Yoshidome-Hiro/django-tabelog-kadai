from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'crud'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('list/', views.RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurant/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('restaurant/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('restaurant/<int:pk>/reservations/', views.ReservationCreateView.as_view(), name='reservation_create'),
    path('restaurant/<int:pk>/favorite/', views.FavoriteView.as_view(), name='favorite'), 
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='crud/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('mypage/', views.MypageView.as_view(), name='mypage'),
    path('mypage/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('portal/', views.PortalView.as_view(), name='portal'),
]