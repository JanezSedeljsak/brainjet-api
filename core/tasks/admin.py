from django.contrib import admin

# Register your models here.
from .models import Task, SubTask, TaskCollaborator, TaskStatus, TaskPermission

admin.site.register([Task, SubTask, TaskCollaborator, TaskStatus, TaskPermission])