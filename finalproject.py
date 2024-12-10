import argparse
import pickle
import os
from datetime import datetime, timedelta


class Task:
    """Representation of a task.
    
    Attributes:
        task_id (int): Unique identifier for the task.
        name (str): Description of the task.
        priority (int): Priority level (1, 2, or 3).
        created (datetime): Date and time when the task was created.
        due_date (datetime): Optional due date for the task.
        completed (datetime): Date and time when the task was completed.
    """

    def __init__(self, task_id, name, priority=1, due_date=None):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.created = datetime.now()
        self.due_date = datetime.strptime(due_date, '%m/%d/%Y') if due_date else None
        self.completed = None

    def mark_complete(self):
        """Marks the task as complete."""
        self.completed = datetime.now()

    def is_completed(self):
        """Checks if the task is completed."""
        return self.completed is not None

    def age(self):
        """Returns the age of the task in days."""
        delta = datetime.now() - self.created
        return delta.days


class Tasks:
    """A collection of Task objects.
    
    Manages adding, deleting, listing, and marking tasks as complete.
    """

    def __init__(self, file_path='.todo.pickle'):
        self.file_path = file_path
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        """Loads tasks from a pickle file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'rb') as file:
                return pickle.load(file)
        return []

    def save_tasks(self):
        """Serializes tasks to a pickle file."""
        with open(self.file_path, 'wb') as file:
            pickle.dump(self.tasks, file)

    def add_task(self, name, priority, due_date):
        """Adds a new task to the task list."""
        task_id = len(self.tasks) + 1
        task = Task(task_id, name, priority, due_date)
        self.tasks.append(task)
        self.save_tasks()
        return task_id

    def delete_task(self, task_id):
        """Deletes a task by its ID."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]
        self.save_tasks()

    def mark_complete(self, task_id):
        """Marks a task as complete by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                task.mark_complete()
                self.save_tasks()
                return True
        return False

    def list_tasks(self, query=None):
        """Lists tasks that match a query or are not completed."""
        tasks_to_list = [
            task for task in self.tasks if not task.is_completed()
        ]
        if query:
            tasks_to_list = [
                task for task in tasks_to_list if any(q.lower() in task.name.lower() for q in query)
            ]
        tasks_to_list.sort(key=lambda t: (t.due_date or datetime.max, -t.priority))
        return tasks_to_list

    def generate_report(self):
        """Generates a report of all tasks, completed and not."""
        self.tasks.sort(key=lambda t: (t.due_date or datetime.max, -t.priority))
        return self.tasks


def main():
    parser = argparse.ArgumentParser(description="Task Manager Application")
    parser.add_argument('--add', type=str, help="Add a new task")
    parser.add_argument('--priority', type=int, choices=[1, 2, 3], default=1, help="Priority level (default is 1)")
    parser.add_argument('--due', type=str, help="Due date in MM/DD/YYYY format")
    parser.add_argument('--delete', type=int, help="Delete a task by its ID")
    parser.add_argument('--done', type=int, help="Mark a task as complete by its ID")
    parser.add_argument('--list', action='store_true', help="List incomplete tasks")
    parser.add_argument('--query', type=str, nargs='+', help="Search tasks by terms")
    parser.add_argument('--report', action='store_true', help="Generate a report of all tasks")

    args = parser.parse_args()
    tasks = Tasks()

    if args.add:
        task_id = tasks.add_task(args.add, args.priority, args.due)
        print(f"Created task {task_id}")
    elif args.delete:
        tasks.delete_task(args.delete)
        print(f"Deleted task {args.delete}")
    elif args.done:
        if tasks.mark_complete(args.done):
            print(f"Completed task {args.done}")
        else:
            print(f"Task {args.done} not found")
    elif args.list:
        task_list = tasks.list_tasks()
        print("ID   Age  Due Date   Priority   Task")
        print("--   ---  --------   --------   ----")
        for task in task_list:
            due = task.due_date.strftime('%m/%d/%Y') if task.due_date else "-"
            print(f"{task.task_id:<4} {task.age():<3}  {due:<10} {task.priority:<9} {task.name}")
    elif args.query:
        task_list = tasks.list_tasks(query=args.query)
        print("ID   Age  Due Date   Priority   Task")
        print("--   ---  --------   --------   ----")
        for task in task_list:
            due = task.due_date.strftime('%m/%d/%Y') if task.due_date else "-"
            print(f"{task.task_id:<4} {task.age():<3}  {due:<10} {task.priority:<9} {task.name}")
    elif args.report:
        report = tasks.generate_report()
        print("ID   Age  Due Date   Priority   Task                Created                       Completed")
        print("--   ---  --------   --------   ----                ---------------------------   -------------------------")
        for task in report:
            due = task.due_date.strftime('%m/%d/%Y') if task.due_date else "-"
            created = task.created.strftime('%a %b %d %H:%M:%S %Z %Y')
            completed = task.completed.strftime('%a %b %d %H:%M:%S %Z %Y') if task.completed else "-"
            print(f"{task.task_id:<4} {task.age():<3}  {due:<10} {task.priority:<9} {task.name:<20} {created:<30} {completed}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
