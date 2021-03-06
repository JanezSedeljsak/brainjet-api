from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from .helpers import HelperMethods

from django.contrib.auth.models import User
from core.tasks.models import *
from rest_framework.permissions import AllowAny
from core.tasks.serializers import *
from django.core import serializers
from django.db.models import Q
from datetime import *
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED
)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def get_task(request, task_id):

    result = {}

    if not Task.objects.filter(id=task_id).exists():
        return Response({'error': 'The task you are searching for does not exist'}, status=HTTP_404_NOT_FOUND)

    task = Task.objects.get(id=task_id)

    if request.method == 'GET':
        task_serializer = TaskFormSerializer(task)
        task_data = task_serializer.data

        if task_data['user'] == request.user.id:
            result['permissions'] = 'admin'

        else:
            if not TaskCollaborator.objects.filter(task=task_id).exists():
                return Response({'error': "You don't have the rights to view this task!"}, status=HTTP_400_BAD_REQUEST)
            else:
                taskcolab = TaskCollaborator.objects.get(task=task_id)
                taskcolab_serializer = TaskEditPermissionsSerializer(taskcolab)

                result['permissions'] = taskcolab_serializer.data['permissions']
        result['form'] = task_data

    elif request.method == 'PUT':
        task_serializer = TaskFormSerializer(task, data=request.data)
        if task_serializer.is_valid():
            task_serializer.save()
            result['task_data'] = task_serializer.data
            result['success'] = True
        else:
            return Response({'error': task_serializer.errors}, status=HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        operation = task.delete()
        result['success'] = bool(operation)

    return Response(result, status=HTTP_200_OK)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def get_task_detail(request, task_id):

    if not Task.objects.filter(id=task_id).exists():
        return Response({'error': 'The task you are searching for does not exist'}, status=HTTP_404_NOT_FOUND)

    task = Task.objects.get(id=task_id)
    task_serializer = TaskDetailSerializer(task)

    return Response(task_serializer.data, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def create_task(request):
    task = request.data
    
    if task is None:
        return Response({'error': 'Invalid data sent'}, status=HTTP_400_BAD_REQUEST)


    task_serializer = TaskFormSerializer(data=task)
    if task_serializer.is_valid():
        task_serializer.save(user=request.user)
        return Response(task_serializer.data, status=HTTP_201_CREATED)
    return Response(task_serializer.errors, status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def get_all_tasks(request):

    colab_serializer = CollaboratorKeySerializer(
        TaskCollaborator.objects.filter(user=request.user), many=True)
    colabIds = [colab['task_id'] for colab in colab_serializer.data]

    tasks = Task.objects.filter(Q(pk__in=colabIds) | Q(user=request.user))

    serializer = TasksViewSerializer(tasks, many=True)

    tasksWithProgress = HelperMethods.addProgressToTasks(serializer.data)

    return Response(tasksWithProgress, status=HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def get_your_tasks_for_daterange(request):

    # @ FORMAT EXAMPLE: '09/19/18-13:55:26'

    _start = request.data.get("start")
    _end = request.data.get("end")

    if _start is None or _end is None:
        return Response({'error': 'Data sent was invalid'}, status=HTTP_400_BAD_REQUEST)

    datetime_start_date = datetime.strptime(_start, '%d/%m/%y')
    datetime_end_date = datetime.strptime(_end, '%d/%m/%y')

    colab_serializer = CollaboratorKeySerializer(
        TaskCollaborator.objects.filter(user=request.user), many=True)
    colabIds = [colab['task_id'] for colab in colab_serializer.data]

    tasks = Task.objects.filter(
        (Q(pk__in=colabIds) | Q(user=request.user)) &
        Q(due_date__lte=datetime_end_date, due_date__gt=datetime_start_date)
    )

    task_serializer = TaskCalendarViewSerailizer(tasks, many=True)

    tasksWithProgress = HelperMethods.addProgressToTasks(task_serializer.data)

    return Response(tasksWithProgress, status=HTTP_200_OK)
