import datetime
import json
import os
import sys
from enum import Enum

class Task:
     def __init__(self,id=None,description="",status="",createdAt=None,updatedAt=None):
        self.id=id
        self.description=description
        self.status=status
        self.createdAt=createdAt
        self.updatedAt=updatedAt

class Status(Enum):
    IN_PROGRESS= "IN_PROGRESS"
    DONE="DONE"
    TODO="TODO"

path_file='tasks.json'

def load_tasks():
    if not os.path.exists(path_file):
        return []
    try:
        with open(path_file, 'r') as file:
            if os.stat(path_file).st_size == 0:  # Verificar si el archivo está vacío
                return []
            return json.load(file)
    except json.JSONDecodeError:
        print("El archivo JSON está corrupto o no contiene un formato válido.")
        return []

def task_to_dict(task):
    """Convierte una instancia de Task a un diccionario."""
    if isinstance(task, Task):
        return {
                'id':task.id,
                'description': task.description, 
                'status': task.status,
                'createdAt': task.createdAt.isoformat() if task.createdAt else None,  # Convertir datetime a string
                'updatedAt': task.updatedAt.isoformat() if task.updatedAt else None 
                }
    raise TypeError(f'Object of type {task.__class__.__name__} is not JSON serializable')

def save_tasks(tasks, filename='tasks.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        # Usar el argumento 'default' para convertir objetos Task
        json.dump(tasks, file, indent=4, default=task_to_dict,ensure_ascii=False)

def add_task(tasks,task):
    #tasks.append({"task":task,"state":"not finished"})
    tasks.append(task)
    save_tasks(tasks)

def list_all_tasks_in_status(tasks_loaded, status: Status):
    list_tasks = []
    for task in tasks_loaded:
        if task['status'] == status:
            list_tasks.append(task)
    
    if not list_tasks:
        print(f"No hay tareas con el estado '{status}'.")
    else:
        print(f"Tareas con estado '{status}':\n")
        for task in list_tasks:
            created_at = task['createdAt'] if task['createdAt'] else "Fecha no disponible"
            updated_at = task['updatedAt'] if task['updatedAt'] else "No actualizado"
            print(f"ID: {task['id']}")
            print(f"description: {task['description']}")
            print(f"status: {task['status']}")
            print(f"created at: {created_at}")
            print(f"updated at: {updated_at}")
            print("-" * 40)  # Separador entre tareas
    return list_tasks

def create_task(tasks,task_to_operate:Task,task):
    try:
        task_to_operate.id= get_last_id(tasks) + 1
        task_to_operate.description=task
        task_to_operate.createdAt=datetime.datetime.now().replace(microsecond=0)  # Quitar microsegundos
        task_to_operate.status=Status.TODO.value
        return task_to_operate.id
    except:
        print("cannot create task")
        raise

def update_task(tasks_loaded, id_task, new_task_description):
    try:
        for task in tasks_loaded:
            if task['id'] == int(id_task):  # Asegurarse de que 'id_task' es un número entero
                task['description'] = new_task_description  # Acceder al diccionario correctamente
                task['updatedAt'] = datetime.datetime.now().replace(microsecond=0).isoformat()  # Actualizar la fecha
                break
        else:
            print(f"Task with ID {id_task} not found.")
        save_tasks(tasks_loaded)  # Guardar los cambios después de la actualización
    except Exception as e:  
        print(f"Cannot update task: {e}")              
        raise

def update_status_task(tasks_loaded,id_task,status):
    for task in tasks_loaded:
        if task['id'] == int(id_task):
            task['status'] = status
            task['updatedAt'] = datetime.datetime.now().replace(microsecond=0).isoformat()  # Actualizar la fecha
            break
    save_tasks(tasks_loaded)

def delete_task(tasks_loaded, task_to_delete):
    # Convertir a entero el ID de la tarea a eliminar
    task_id = int(task_to_delete)
    
    # Filtrar la lista de tareas, excluyendo la tarea que se desea eliminar
    tasks_loaded = [task for task in tasks_loaded if task['id'] != task_id]
    
    # Guardar los cambios después de eliminar la tarea
    save_tasks(tasks_loaded)

    print(f"Tarea con ID {task_id} eliminada exitosamente.")


def get_last_id(tasks):
    if tasks:
        last_task = max(tasks, key=lambda task: task['id'])
        return last_task['id']
    return 0

def main():
    tasks_loaded = load_tasks()
    task_to_operate = Task()

    if len(sys.argv)<2:
        print("Please provide a choice: add <task> or list.")
        return
    
    action = sys.argv[1]
    
    if action =="mark-done" or action=='mark-in-progress' and len(sys.argv)==3:
        id_task= sys.argv[2]
        #TODO:revisar la teoria de generadores y comprensiones de listas
        task_getting = next((task for task in tasks_loaded if task['id'] == int(id_task)), None)

        if task_getting:
            print(f"Task found: {task_getting}")
        else:
            print(f"No task found with ID: {id_task}")

        if action =="mark-done":
            task_getting['status']= 'done'
            update_status_task(tasks_loaded,id_task,Status.DONE.value)
        if action =="mark-in-progress":
            update_status_task(tasks_loaded,id_task,Status.IN_PROGRESS.value)
   
    if action== "update" and len(sys.argv)==4:
        task=sys.argv[3]
        id_task=sys.argv[2]
        update_task(tasks_loaded,id_task,task)
        print(f"Task added successfully (ID: {id_task})")


    if action=="list" and len(sys.argv)==3:
        status_request=sys.argv[2].upper()
        if status_request in [status.value for status in Status]:
            list_all_tasks_in_status(tasks_loaded,status_request)

    if action== "add" and len(sys.argv)==3:
        task= sys.argv[2]
        id_created= create_task(tasks_loaded,task_to_operate,task)
        add_task(tasks_loaded,task_to_operate) 
        print(f"Task added successfully (ID: {id_created})")

    if action=="delete" and len(sys.argv)==3:
          id_task= sys.argv[2]
          delete_task(tasks_loaded,id_task)


if __name__ == '__main__':
    main()