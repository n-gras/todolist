from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

engine = create_engine('sqlite:///todo.db?check_same_thread=False')

Base = declarative_base()


# create Table class
class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


# Create table in database
Base.metadata.create_all(engine)

# Create SQL session
Session = sessionmaker(bind=engine)
session = Session()


def print_tasks(choice):
    # list of weekdays for use with datetime.weekday() -- strftime("%A") would have same result
    weekdays = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    today = datetime.today()

    # logic for different choices
    if choice == 'Today':
        tasks = session.query(Table).filter(Table.deadline == today.date()).all()
        print(f'\nToday {today.strftime("%d %b")}:')
        if not tasks:
            print('Nothing to do!')
        else:
            for counter, task in enumerate(tasks, 1):
                print(f'{counter}. {task}')

    elif choice == 'Week':
        for days in range(7):
            this_day = today + timedelta(days)
            tasks = session.query(Table).filter(Table.deadline == this_day.date()).all()
            print(f'\n{weekdays[this_day.weekday()]} {this_day.day} {this_day.strftime("%b")}:')  # strftime("%A %d %b") would accomplish the same, easier
            if not tasks:
                print('Nothing to do!')
            else:
                for counter, task in enumerate(tasks, 1):
                    print(f'{counter}. {task}')

    elif choice == 'All':
        tasks = session.query(Table, Table.deadline).order_by(Table.deadline).all()
        if not tasks:
            print('Nothing to do!')
        else:
            for counter, task in enumerate(tasks, 1):
                print(f'{counter}. {task[0]}. {task[1].strftime("%d %b")}')
            return tasks  # returns full ordered tasklist for use with del_task

    elif choice == 'Missed':
        tasks = session.query(Table, Table.deadline).filter(Table.deadline < today.date()).order_by(Table.deadline).all()
        if not tasks:
            print('Nothing to delete!')
        else:
            for counter, task in enumerate(tasks, 1):
                print(f'{counter}. {task[0]}. {task[1].strftime("%d %b")}')


def add_task(task, deadline):
    # create new task object
    insert_task = Table(task=task, deadline=deadline)
    session.add(insert_task)
    session.commit()


def del_task(choice, tasklist):

    # print(tasklist)
    # row = tasklist[0][choice - 1]
    # print(del_choice)

    tasks = session.query(Table, Table.deadline).order_by(Table.deadline).all()
    row = tasks[0][choice - 1]

    session.delete(row)
    session.commit()


def menu():
    while True:
        print("\n1) Today's tasks\n2) Week's tasks\n3) All tasks"
              "\n4) Missed tasks\n5) Add task\n6) Delete task\n0) Exit")
        choice = int(input())
        if choice == 0:
            break
        elif choice == 1:
            print_tasks('Today')
        elif choice == 2:
            print_tasks('Week')
        elif choice == 3:
            print_tasks('All')
        elif choice == 4:
            print_tasks('Missed')
        elif choice == 5:
            print("\nEnter task")
            new_task = input()
            print("Enter deadline")
            # year, month, day = input().split('-')
            new_deadline = datetime.strptime(input(), "%Y-%m-%d")
            add_task(new_task, new_deadline)
        elif choice == 6:
            print('\nChoose the number of the task you want to delete:')
            all_tasks = print_tasks('All')  # create all_task list with all tasks returned from print_task function
            del_choice = int(input())
            del_task(del_choice, all_tasks)
    print("Bye!")


menu()
