from django.contrib import admin
from .models import User, Event, Task, Team, BudgetItem, Ticket, Message

# Register your models here.
admin.site.register(User)
admin.site.register(Event)
admin.site.register(Task)
admin.site.register(Team)
admin.site.register(BudgetItem)
admin.site.register(Ticket)
admin.site.register(Message)


