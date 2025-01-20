from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'budgetitems', views.BudgetItemViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/csrf/', views.get_csrf_token, name='get_csrf_token')
]