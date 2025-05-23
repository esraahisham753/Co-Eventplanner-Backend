from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'teams', views.TeamViewSet)
router.register(r'budgetitems', views.BudgetItemViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('api/events/<int:event_id>/tasks/', views.TaskViewSet.as_view({'get': 'event_tasks'}), name='event-tasks'),
    path('api/events/<int:event_id>/teams/', views.TeamViewSet.as_view({'get': 'event_teams'}), name='event-teams'),
    path('api/events/<int:event_id>/budgetitems/', views.BudgetItemViewSet.as_view({'get': 'event_budgetitems'}), name='event-budgetitems'),
    path('api/events/<int:event_id>/tickets/', views.TicketViewSet.as_view({'get': 'event_tickets'}), name='event-tickets'),
    path('api/users/<int:user_id>/tickets/', views.TicketViewSet.as_view({'get': 'user_tickets'}), name='user-tickets'),
    path('api/events/<int:event_id>/messages/', views.MessageViewSet.as_view({'get': 'event_messages'}), name='event-messages'),
    path('api/users/username/<str:username>/', views.UserViewSet.as_view({'get': 'user_detail'}), name='user-detail'),
    path('api/me/events/', views.EventViewSet.as_view({'get': 'organizer_events'}), name='organizer-events'),
    path('api/me/teams/pending/', views.TeamViewSet.as_view({'get': 'pending_teams'}), name='pending-teams'),
]