from .models import *
from .serializers import *

class HelperMethods:

    @staticmethod
    def addProgressToTasks(tasks, fillEmpty=False):
        newTasks = []
        for task in tasks:
            if task['is_event']:
                newTaskData = task
                if fillEmpty:
                    newTaskData["progress"] = '/'
                newTasks.append(newTaskData)
                continue
            
            prog = 0
            count = 0
            for subtask in task['subtasks']:
                count += 1
                prog += 1 if subtask['status_id'] == 3 else 0

            newTaskData = task
            newTaskData["progress"] = prog / count * 100 if prog > 0 else 0

            newTasks.append(newTaskData)

        return newTasks