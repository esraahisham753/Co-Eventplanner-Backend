from rest_framework import serializers
from .models import User, Event, Task, Team, BudgetItem, Ticket, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'image', 'job_title', 'groups', 'user_permissions']
    
    def create(self, validated_data):
        print(validated_data)
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            job_title=validated_data.get('job_title', ''),
            image=validated_data.get('image', None)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.job_title = validated_data.get('job_title', instance.job_title)
        instance.image = validated_data.get('image', instance.image)
        password = validated_data.get('password', None)

        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class EventSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image', 'price', 'location', 'date', 'role']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        event = Event.objects.create(**validated_data)
        Team.objects.create(user=user, event=event, role='organizer', invitation_status=True)
        return event

class TaskSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    image = serializers.ImageField(source='user.image', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'event', 'user', 'username', 'image']
        read_only_fields = ['username', 'image']
    
    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        return task

class TeamSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    image = serializers.ImageField(source='user.image', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_image = serializers.ImageField(source='event.image', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'user', 'event', 'role', 'invitation_status', 'username', 'image', 'event_title', 'event_image']

class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'title', 'description', 'amount', 'event']

class TicketSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_date = serializers.DateTimeField(source='event.date', read_only=True)
    event_location = serializers.CharField(source='event.location', read_only=True)
    event_price = serializers.DecimalField(source='event.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'code', 'user', 'event', 'event_title', 'event_date', 'event_location', 'event_price']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_image = serializers.ImageField(source='sender.image', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'content', 'image', 'created_at', 'sender', 'event', 'sender_username', 'sender_image']