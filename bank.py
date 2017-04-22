#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json

import connect
import utils


class Bank(object):
    def __init__(self):
        self.logger = utils.init_logger("Bank")
        self.all_bank_fname = "all_bank.json"
        self.all_account_fname = "all_account.json"
        self.all_tasks_fname = "all_tasks.json"
        self.tasks_fname = "{}_tasks.json"
        self.all_cost_fname = "all_cost.json"
        self.cost_fname = "{}_cost.json"
        self.onedrive = connect.OnedriveStorage()
        self.all_tasks = self.onedrive.get_recorder_file_content(self.all_tasks_fname, [])
        self.all_cost = self.onedrive.get_recorder_file_content(self.all_cost_fname, [])
        self.today = datetime.date.today()
        self.today_tasks_fname = self.tasks_fname.format(self.today)
        self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])
        self.today_cost_fname = self.cost_fname.format(self.today)
        self.today_cost = self.onedrive.get_recorder_file_content(self.today_cost_fname, [])

    def create_update_task(self, mode, content, score, unit=1, num=1, ind=None):
        if score is not None and not isinstance(score, int):
            score = int(score)
        if unit is not None and not isinstance(unit, int):
            unit = int(unit)
        if num is not None and not isinstance(num, int):
            num = int(num)
        if ind is not None and not isinstance(ind, int):
            ind = int(ind)
        if not isinstance(content, unicode):
            content = unicode(content, "utf8")

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
        self.retrieve_tasks()

    def retrieve_tasks(self):
        header_format = u"%5s|%5s|%5s|%5s|%5s|%s"
        task_format = u"%5s|%5s|%5d|%5d|%5d|%s"
        print header_format % ("Mode", "Id", "Score", "Num", "Unit", "Content")
        for ind, task in enumerate(self.all_tasks):
            print task_format % ("a", ind, task["score"], task["num"], task["unit"], task["content"])
        for ind, task in enumerate(self.today_tasks):
            print task_format % ("t", ind, task["score"], task["num"], task["unit"], task["content"])

    def delete_tasks(self, mode, ind):
        if ind is not None and not isinstance(ind, int):
            ind = int(ind)
        if mode == "a":
            self.all_tasks.pop(ind)
        else:
            self.today_tasks.pop(ind)
        self.retrieve_tasks()

    def create_update_cost(self, mode, content, score, unit=1, ind=None):
        if score is not None and not isinstance(score, int):
            score = int(score)
        if unit is not None and not isinstance(unit, int):
            unit = int(unit)
        if ind is not None and not isinstance(ind, int):
            ind = int(ind)
        if not isinstance(content, unicode):
            content = unicode(content, "utf8")

        cost = {
            "content": content,
            "score": score,
            "unit": unit
        }
        if mode == 'a':
            if ind is not None:
                self.all_cost[ind] = cost
            else:
                self.all_cost.append(cost)
        else:
            if ind is not None:
                self.today_cost[ind] = cost
            else:
                self.today_cost.append(cost)
        self.retrieve_cost()

    def retrieve_cost(self):
        header_format = u"%5s|%5s|%5s|%5s|%s"
        cost_format = u"%5s|%5s|%5d|%5d|%s"
        print header_format % ("Mode", "Id", "Score", "Unit", "Content")
        for ind, cost in enumerate(self.all_cost):
            print cost_format % ("a", ind, cost["score"], cost["unit"], cost["content"])
        for ind, cost in enumerate(self.today_cost):
            print cost_format % ("t", ind, cost["score"], cost["unit"], cost["content"])

    def delete_cost(self, mode, ind):
        if ind is not None and not isinstance(ind, int):
            ind = int(ind)
        if mode == "a":
            self.all_cost.pop(ind)
        else:
            self.today_cost.pop(ind)
        self.retrieve_cost()

    def save(self, refresh=False):
        self.onedrive.save_recorder_file_content(self.all_tasks_fname, self.all_tasks)
        self.onedrive.save_recorder_file_content(self.today_tasks_fname, self.today_tasks)
        if refresh and self.today != datetime.date.today():
            self.today_tasks_fname = self.tasks_fname.format(self.today)
            self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])

    def help(self):
        print u'Task: t Op(c|r|u|d) Mode(a|t) id content score unit num, For example: t c a 背英语单词 5 20 20'
        print u'Cost: c Op(c|r|u|d) Mode(a|t) id content score unit, For example: c c t Lunch-Normal 5'

    def run(self):
        self.help()
        while True:
            try:
                op = raw_input(">>").strip()
                eles = op.split(' ')
                eles = [ele.strip() for ele in eles if ele.strip()]
                if eles[0] == 'e':
                    break
                elif eles[0] == 'h':
                    self.help()
                elif eles[0] == 's':
                    refresh = False
                    if len(eles) == 2 and eles[1] == 'r':
                        refresh = True
                    self.save(refresh)
                elif eles[0] == 't':
                    if eles[1] == "c":
                        self.create_update_task(eles[2], eles[3], eles[4],
                                                eles[5] if len(eles) > 5 else 1, eles[6] if len(eles) > 6 else 1)
                    elif eles[1] == "r":
                        self.retrieve_tasks()
                    elif eles[1] == "u":
                        self.create_update_task(eles[2], eles[4], eles[5],
                                                eles[6] if len(eles) > 6 else 1,
                                                eles[7] if len(eles) > 7 else 1, eles[3])
                    elif eles[1] == "d":
                        self.delete_tasks(eles[2], eles[3])
                    else:
                        print "Unknown op"
                elif eles[0] == 'c':
                    if eles[1] == "c":
                        self.create_update_cost(eles[2], eles[3], eles[4],
                                                eles[5] if len(eles) > 5 else 1, )
                    elif eles[1] == "r":
                        self.retrieve_cost()
                    elif eles[1] == "u":
                        self.create_update_cost(eles[2], eles[4], eles[5],
                                                eles[6] if len(eles) > 6 else 1, eles[3])
                    elif eles[1] == "d":
                        self.delete_cost(eles[2], eles[3])
                    else:
                        print "Unknown op"
                else:
                    print 'Unknown op'
            except EOFError as e:
                break
            except Exception as e:
                self.logger.error(e)

if __name__ == '__main__':
    bank = Bank()
    bank.run()
