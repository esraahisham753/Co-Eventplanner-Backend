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
from rest_framework.decorators import api_view, permission_classes

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
        queryset = super().get_queryset()
        event_id = self.kwargs.get('event_id', None)

        print(event_id)

        if event_id:
            event = Event.objects.get(pk=event_id)

            for member in event.teams.all():
                if self.request.user == member.user:
                    queryset = queryset.filter(event=event_id)
                    return queryset
            
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user in instance.event.teams.all():
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])
        
        for member in event.teams.filter(role='organizer'):
            if request.user == member.user:
                return super().create(request, *args, **kwargs)
        
        return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user in instance.event.teams.filter(role='organizer'):
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user in instance.event.teams.filter(role='organizer'):
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user in instance.event.teams.filter(role='organizer'):
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)
    
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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user in instance.event.teams.all():
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        event = Event.objects.get(pk=request.data['event'])
        if not request.user in event.teams.all():
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.sender:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.sender:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.sender:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


