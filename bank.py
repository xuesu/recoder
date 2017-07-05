# -*- coding: utf-8 -*-

import copy
import datetime

import connect
import utils

from errors import *


def crud_type_check(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            ind = kwargs.get("ind")
            if ind is not None and not isinstance(ind, int):
                kwargs["ind"] = int(ind)
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("ind")
        try:
            content = kwargs.get("content")
            if content is not None and not isinstance(content, unicode):
                kwargs["content"] = unicode(content, "utf8")
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("content")
        try:
            score = kwargs.get("score")
            if score is not None and not isinstance(score, int):
                kwargs["score"] = int(score)
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("score")
        try:
            num = kwargs.get("num")
            if num is not None and not isinstance(num, int):
                kwargs["num"] = int(num)
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("num")
        try:
            vol = kwargs.get("vol")
            if vol is not None and not isinstance(vol, int):
                kwargs["vol"] = int(vol)
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("vol")

        try:
            remark = kwargs.get("remark")
            if remark is not None and not isinstance(remark, unicode):
                kwargs["remark"] = unicode(remark, "utf8")
        except Exception, e:
            self.logger.error(utils.describe_error(e))
            raise InvalidParameterException("remark")

        if kwargs.get("mode") is not None and kwargs.get("mode") not in ["t", "a"]:
            raise InvalidParameterException("mode")

        if kwargs.get("time") is not None:
            datetime.datetime.strptime(kwargs.get("time"), utils.DATETIME_FORMAT)

        if kwargs.get("date") is not None:
            datetime.datetime.strptime(kwargs.get("date"), utils.DATE_FORMAT)

        return func(*args, **kwargs)

    return wrapper


class Bank(object):
    def __init__(self, name="default"):
        self.name = name
        self.logger = utils.init_logger("Bank_%s" % name)
        self.bank_fname = "%s_all_bank.json" % name
        self.all_tasks_fname = "%s_all_tasks.json" % name
        self.tasks_fname = "%s_{}_tasks.json" % name
        self.costs_fname = "%s_{}_cost.json" % name
        self.onedrive = connect.holder.get_storage()
        self.bank = self.onedrive.get_recorder_file_content(self.bank_fname, None)
        self.all_tasks = self.onedrive.get_recorder_file_content(self.all_tasks_fname, [])
        self.today = datetime.date.today()
        self.today_tasks_fname = self.tasks_fname.format(self.today.strftime(utils.DATE_FORMAT))
        self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])
        self.today_costs_fname = self.costs_fname.format(self.today)
        self.today_costs = self.onedrive.get_recorder_file_content(self.today_costs_fname, [])
        self.all_tasks.sort(key=lambda task: (task["score"], task["num"]))
        self.today_tasks.sort(key=lambda task: (task["score"], task["num"]))
        if self.bank is None:
            self.bank = self.init_bank()

    def init_bank(self, golden=0):
        _bank = dict()
        _bank["golden"] = golden
        vols = [-1] * len(self.all_tasks + self.today_tasks)
        for ind, task in enumerate(self.all_tasks):
            vols[ind] = task["num"]
        for ind, task in enumerate(self.today_tasks):
            vols[ind + len(self.all_tasks)] = task["num"]
        _bank["vols"] = vols
        return _bank

    @crud_type_check
    def create_task(self, content, score, num=1, mode="t"):
        task = {
            "content": content,
            "score": score,
            "num": num
        }

        if mode == 'a':
            self.all_tasks.append(task)
            self.bank["vols"].insert(len(self.all_tasks), num)
            self.all_tasks.sort(key=lambda task: (task["score"], task["num"]))
        else:
            self.today_tasks.append(task)
            self.bank["vols"].append(num)
            self.today_tasks.sort(key=lambda task: (task["score"], task["num"]))
        self.retrieve_tasks()

    def retrieve_tasks(self, date=None):
        header_format = u"%5s|%5s|%5s|%5s|%8s|%s"
        task_format = u"%5s|%5s|%5d|%5d|%8d|%s"
        print header_format % ("Mode", "Id", "Score", "Num", "Volume", "Content")
        all_tasks = copy.deepcopy(self.all_tasks)
        for ind, task in enumerate(all_tasks):
            task["vol"] = self.bank["vols"][ind]
        if date is None:
            today_tasks = copy.deepcopy(self.today_tasks)
        else:
            today_tasks = self.onedrive.get_recorder_file_content(self.tasks_fname.format(date), [])
        for ind, task in enumerate(today_tasks):
            task["vol"] = self.bank["vols"][ind + len(self.all_tasks)]
        for ind, task in enumerate(all_tasks):
            print task_format % ("a", ind, task["score"], task["vol"], task["num"], task["content"])
        for ind, task in enumerate(today_tasks):
            print task_format % ("t", ind + len(all_tasks), task["score"], task["vol"], task["num"], task["content"])

    @crud_type_check
    def update_task(self, ind, content=None, score=None, num=None, vol=None):
        if ind is None:
            raise RequiredArgEmptyException("ind")
        if ind < len(self.all_tasks):
            task = self.all_tasks[ind]
        else:
            task = self.today_tasks[ind - len(self.all_tasks)]
        if content is not None:
            task["content"] = content
        if score is not None:
            task["score"] = score
        if num is not None:
            task["num"] = num
        if vol is not None:
            self.bank["vols"][ind] = vol
        self.all_tasks.sort(key=lambda task: (task["score"], task["num"]))
        self.today_tasks.sort(key=lambda task: (task["score"], task["num"]))
        self.retrieve_tasks()

    @crud_type_check
    def delete_task(self, ind):
        if ind < len(self.all_tasks):
            self.all_tasks.pop(ind)
        else:
            self.today_tasks.pop(ind - len(self.all_tasks))
        self.bank["vols"].pop(ind)
        self.retrieve_tasks()

    @crud_type_check
    def create_cost(self, ind, num=1, remark="", force=False):
        task = self.all_tasks[ind] if ind < len(self.all_tasks) else self.today_tasks[ind - len(self.all_tasks)]
        if not force:
            vol = self.bank["vols"][ind]
            if vol != -1 and vol < num:
                self.logger.warning("Task Volume exceeds! Cost %d instead!" % vol)
                num = vol
            if task["score"] < 0 and task["score"] * num + self.bank["golden"] < 0:
                raise GoldenExceedException()

        cost = {
            "task": task,
            "num": num,
            "remark": remark,
            "time": datetime.datetime.now().strftime(utils.DATETIME_FORMAT)
        }
        self.bank["golden"] += task["score"] * num
        self.today_costs.append(cost)

    def retrieve_costs(self, date=None):
        header_format = u"%15s|%5s|%5s|%5s|%s|%s"
        cost_format = u"%15s|%5d|%5d|%5d|%s|%s"
        print header_format % ("Time", "Id", "Score", "Num", "Content", "Remark")
        if date is None:
            today_costs = copy.deepcopy(self.today_costs)
        else:
            today_costs = self.onedrive.get_recorder_file_content(self.costs_fname.format(date), [])
        for ind, cost in enumerate(today_costs):
            print cost_format % (cost["time"], ind, cost["task"]["score"], cost["num"], cost["task"]["content"],
                                 cost["remark"])

    @crud_type_check
    def update_cost(self, ind, num=None, remark=None, time=None):
        cost = self.today_costs[ind]
        if num is not None:
            self.bank["golden"] -= cost["task"]["score"] * cost["num"]
            self.bank["golden"] += cost["task"]["score"] * num
            cost["num"] = num
        if remark is not None:
            cost["remark"] = remark
        if time is not None:
            cost["time"] = time

    @crud_type_check
    def delete_cost(self, ind):
        self.today_costs.pop(ind)
        self.retrieve_costs()

    def save(self, refresh=False):
        self.onedrive.save_recorder_file_content(self.bank_fname, self.bank)
        self.onedrive.save_recorder_file_content(self.all_tasks_fname, self.all_tasks)
        self.onedrive.save_recorder_file_content(self.today_tasks_fname, self.today_tasks)
        self.onedrive.save_recorder_file_content(self.today_costs_fname, self.today_costs)
        if refresh and self.today != datetime.date.today():
            self.today_tasks_fname = self.tasks_fname.format(self.today)
            self.today_costs_fname = self.costs_fname.format(self.today)
            self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])
            self.today_tasks = self.onedrive.get_recorder_file_content(self.today_tasks_fname, [])
            self.bank = self.init_bank(self.bank["golden"])
