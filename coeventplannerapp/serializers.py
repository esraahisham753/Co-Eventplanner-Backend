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
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'event', 'user']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        task = Task.objects.create(user=user, **validated_data)
        return task

class TeamSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    image = serializers.ImageField(source='user.image', read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'user', 'event', 'role', 'invitation_status', 'username', 'image']
        read_only_fields = ['user', 'event']

class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'title', 'description', 'amount', 'event']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'code', 'user', 'event']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'created_at', 'sender', 'event']