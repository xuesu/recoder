import datetime
import json

import connect


class Bank(object):
    def __init__(self):
        self.all_bank_fname = "all_bank.json"
        self.all_account_fname = "all_account.json"
        self.all_tasks_fname = "all_tasks.json"
        self.tasks_fname = "{}_tasks.json"
        self.onedrive = connect.OnedriveStorage()
        self.all_tasks = self.onedrive.get_recorder_file_content(self.all_tasks_fname, [])
        self.today = datetime.date.today()
        self.today_tasks_fname = self.tasks_fname.format(self.today)
        self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])

    def add_task(self, content, mode, score, unit=1, num=1, ind=None):
        task = {
            "content": content,
            "score": score,
            "unit": unit,
            "num": num
        }
        if mode == 'a':
            if ind is not None:
                self.all_tasks[ind] = task
            else:
                self.all_tasks.append(task)
        else:
            if ind is not None:
                self.today_tasks[ind] = task
            else:
                self.today_tasks.append(task)

    def print_tasks(self):
        header_format = u"%5s|%5s|%5s|%5s|%s"
        task_format = u"%5s|%5d|%5d|%5d|%s"
        print header_format % ("Mode", "Score", "Num", "Unit", "Content")
        for task in self.all_tasks:
            print task_format.format("a", task["score"], task["num"], task["unit"], task["content"])
        for task in self.today_tasks:
            print task_format.format("t", task["score"], task["num"], task["unit"], task["content"])

    def save_tasks(self):
        self.onedrive.save_recorder_file_content(self.all_tasks_fname, self.all_tasks)
        self.onedrive.save_recorder_file_content(self.today_tasks_fname, self.today_tasks)

