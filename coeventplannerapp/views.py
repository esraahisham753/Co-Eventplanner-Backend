from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import User, Event, Task, Team, BudgetItem, Ticket, Message
from .serializers import UserSerializer, EventSerializer, TaskSerializer, TeamSerializer, BudgetItemSerializer, TicketSerializer, MessageSerializer
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes, action
import logging

logger = logging.getLogger(__name__)

# Add these views to your urlpatterns

@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

# Create your views here.
def index(request):
    return render(request, 'coeventplannerapp/index.html')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.action == 'user_detail':
            username = self.kwargs.get('username', None)
            queryset = super().get_queryset()

            if username:
                queryset = queryset.filter(username=username)
                return queryset
        
        return super().get_queryset()
    
    @action(detail=False, methods=['get'], url_path='users/username/(?P<username>\w+)/')
    def user_detail(self, request, username=None):
        print('user_detail')
        self.kwargs['username'] = username
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.action == 'organizer_events':
            queryset = super().get_queryset()
            user = self.request.user
            queryset = queryset.filter(teams__user=user, teams__role='organizer')
            return queryset
        
        return super().get_queryset()
    
    @action(detail=False, methods=['get'], url_path='organizer-events/')
    def organizer_events(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().update(request, *args, **kwargs)
            
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().partial_update(request, *args, **kwargs)
            
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().destroy(request, *args, **kwargs)
            
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):

        if self.action == 'event_tasks':
            print('get_queryset')
            queryset = super().get_queryset()
            event_id = self.kwargs.get('event_id', None)

            if event_id:
                event = Event.objects.get(pk=event_id)

                for member in event.teams.all():
                    if self.request.user == member.user:
                        queryset = queryset.filter(event=event_id)
                        return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().get_queryset()
        
    @action(detail=False, methods=['get'], url_path='event-tasks/(?P<event_id>\d+)')
    def event_tasks(self, request, event_id=None):
        print('event_tasks')
        self.kwargs['event_id'] = event_id
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.event.teams.all():
            if request.user == member.user:
                return super().retrieve(request, *args, **kwargs)

        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    

    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])

        for member in event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().create(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().update(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().partial_update(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().destroy(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.action == 'event_teams':
            event_id = self.kwargs.get('event_id', None)
            queryset = super().get_queryset()

            if event_id:
                event = Event.objects.get(pk=event_id)

                for member in event.teams.all():
                    if self.request.user == member.user:
                        queryset = queryset.filter(event=event_id)
                        return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().get_queryset()
        
    @action(detail=False, methods=['get'], url_path='event-teams/(?P<event_id>\d+)')
    def event_teams(self, request, event_id=None):
        queryset = self.get_queryset().filter(event=event_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        for member in instance.event.teams.all():
            if request.user == member.user:
                return super().retrieve(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])

        for member in event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().create(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def list(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        is_organizer = False

        #print(user)

        for member in instance.event.teams.filter(role='organizer'):
            #print(member.user)
            if user == member.user:
                is_organizer = True
                break
        
        is_invited = instance.user == user and instance.invitation_status == False

        if is_organizer and 'role' in request.data:
            instance.role = request.data['role']
        
        if is_invited and 'invitation_status' in request.data:
            instance.invitation_status = request.data['invitation_status']
        
        if is_organizer or is_invited:
            instance.save()
            return Response(self.get_serializer(instance).data)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().destroy(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

class BudgetItemViewSet(viewsets.ModelViewSet):
    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.action == 'event_budgetitems':
            event_id = self.kwargs.get('event_id', None)
            queryset = super().get_queryset()

            if event_id:
                event = Event.objects.get(pk=event_id)

                for member in event.teams.all():
                    if self.request.user == member.user:
                        queryset = queryset.filter(event=event_id)
                        return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().get_queryset()
        
    @action(detail=False, methods=['get'], url_path='event-budgetitems/(?P<event_id>\d+)')
    def event_budgetitems(self, request, event_id=None):
        self.kwargs['event_id'] = event_id
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info('retrieve')
        
        for member in instance.event.teams.all():
            logger.info(member.user)
            if request.user == member.user:
                logger.info(request.user)
                return super().retrieve(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])
        
        for member in event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().create(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.event.teams.filter(user=request.user, role='organizer').exists():
            return super(BudgetItemViewSet, self).partial_update(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform partial update this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().destroy(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        user = request.user
        user_id = request.data.get('user', None)

        if user_id and int(user_id) == user.id:
            return super().create(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def get_queryset(self):
        if self.action == 'event_tickets':
            event_id = self.kwargs.get('event_id', None)
            queryset = super().get_queryset()

            if event_id:
                event = Event.objects.get(pk=event_id)

                for member in event.teams.all():
                    if self.request.user == member.user:
                        queryset = queryset.filter(event=event_id)
                        return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        elif self.action == 'user_tickets':
            user_id = self.kwargs.get('user_id', None)
            queryset = super().get_queryset()

            if user_id:
                user = User.objects.get(pk=user_id)

                if self.request.user == user:
                    queryset = queryset.filter(user=user_id)
                    return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return super().get_queryset()
    
    @action(detail=False, methods=['get'], url_path='event-tickets/(?P<event_id>\d+)')
    def event_tickets(self, request, event_id=None):
        self.kwargs['event_id'] = event_id
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user-tickets/(?P<user_id>\d+)')
    def user_tickets(self, request, user_id=None):
        self.kwargs['user_id'] = user_id
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        guest = instance.user
        user = request.user
        is_guest = guest == user
        is_staff = False

        for member in instance.event.teams.all():
            if user == member.user:
                is_staff = True
                break
        
        if is_guest or is_staff:
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def update(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.action == 'event_messages':
            event_id = self.kwargs.get('event_id', None)
            queryset = super().get_queryset()

            if event_id:
                event = Event.objects.get(pk=event_id)

                for member in event.teams.all():
                    if self.request.user == member.user:
                        queryset = queryset.filter(event=event_id)
                        return queryset
                
                return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().get_queryset()
    
    @action(detail=False, methods=['get'], url_path='event-messages/(?P<event_id>\d+)')
    def event_messages(self, request, event_id=None):
        self.kwargs['event_id'] = event_id
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        for member in instance.event.teams.all():
            if request.user == member.user:
                return super().retrieve(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])
        sender = request.data['sender']
        #print(sender)
        is_user = sender == request.user.id
        is_member = False

        for member in event.teams.all():
            if request.user == member.user:
                is_member = True
                break
        
        if is_user and is_member:
            return super().create(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.sender:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        is_sender = request.user == instance.sender
        is_organizer = False

        for member in instance.event.teams.filter(role='organizer'):
            if request.user == member.user:
                is_organizer = True
                break

        if is_sender or is_organizer:
            return super().destroy(request, *args, **kwargs)
        else:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


