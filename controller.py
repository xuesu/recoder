#! /usr/bin/env python
# -*- coding: utf-8 -*-

import connect
import bank
import utils

from errors import *


class Controller(object):
    def __init__(self):
        self.banks = dict()
        self.bank = None
        self.logger = utils.init_logger("controller")

    @staticmethod
    def help():
        print u'Help: help'
        print u'Exit: exit'
        print u'Authorize: authorize'
        print u'Golden: golden <golden>'
        print u'Open: open <bank_name>'
        print u'Save: save <option>? Option r: refresh the date.'
        print u'Task: task Op(c|r|u|d)'
        print u'Task: task c <content> <score> <num>? <mode>?'
        print u'Task: task r <date>?'
        print u'Task: task u <ind> [content <content>]? [score <score>]? [num <num>]? [vol <vol>]?'
        print u'Task: task d <ind>'
        print u'Cost: cost Op(c|r|u|d)'
        print u'Cost: cost c <ind> <num>? <remark>? <option>? Option: f: force to create cost'
        print u'Cost: cost r <date>?'
        print u'Cost: cost u <ind> [num <num>]? [remark <remark>]? [time <time>]?'
        print u'Cost: cost d <ind>'
        print u'Date: format: {}'.format(utils.DATE_FORMAT)
        print u'Datetime: format: {}'.format(utils.DATETIME_FORMAT)

    def authorize(self):
        connect.holder.get_storage().check_authorize()

    def open(self, name):
        if name in self.banks:
            self.bank = self.banks[name]
        else:
            self.bank = bank.Bank(name=name)
            self.banks[name] = self.bank
        print 'Successfully open bank %s.' % name

    def step_save(self, eles):
        kwargs = dict()
        if len(eles) == 2 and eles[1] == 'r':
            kwargs["refresh"] = True
        self.bank.save(**kwargs)

    def step_golden(self, eles):
        if len(eles) == 1:
            print self.bank.bank.get("golden")
        else:
            self.bank.bank["golden"] = float(eles[1])

    def step_task(self, eles):
        kwargs = dict()
        command = eles[1]
        if command == "c":
            kwargs["content"] = eles[2]
            kwargs["score"] = eles[3]
            if len(eles) > 4:
                kwargs["num"] = eles[4]
            if len(eles) > 5:
                kwargs["mode"] = eles[5]
            self.bank.create_task(**kwargs)
        elif command == "r":
            if len(eles) > 2:
                kwargs["date"] = eles[2]
            self.bank.retrieve_tasks(**kwargs)
        elif command == "u":
            for i in range(3, len(eles), 2):
                kwargs[eles[i]] = eles[i + 1]
            kwargs["ind"] = eles[2]
            self.bank.update_task(**kwargs)
        elif command == "d":
            kwargs["ind"] = eles[2]
            self.bank.delete_task(**kwargs)
        else:
            raise UnknownOpException(command)

    def step_cost(self, eles):
        kwargs = dict()
        command = eles[1]
        if command == "c":
            kwargs["ind"] = eles[2]
            if len(eles) > 3:
                kwargs["num"] = eles[3]
            if len(eles) > 4:
                kwargs["remark"] = eles[4]
            if len(eles) > 5:
                if "f" in eles[5]:
                    kwargs["force"] = True
            self.bank.create_cost(**kwargs)
        elif command == "r":
            if len(eles) > 2:
                kwargs["date"] = eles[2]
            self.bank.retrieve_costs(**kwargs)
        elif command == "u":
            for i in range(3, len(eles), 2):
                kwargs[eles[i]] = eles[i + 1]
            kwargs["ind"] = eles[2]
            self.bank.update_cost(**kwargs)
        elif command == "d":
            kwargs["ind"] = eles[2]
            self.bank.delete_cost(**kwargs)
        else:
            raise UnknownOpException(command)

    def run(self):
        self.help()
        while True:
            try:
                op = raw_input(">>").strip()
                eles = op.split(' ')
                eles = [ele.strip() for ele in eles if ele.strip()]
                if eles[0] == 'exit':
                    break
                elif eles[0] == 'help':
                    self.help()
                elif eles[0] == 'authorize':
                    self.authorize()
                elif eles[0] == "open":
                    self.open(eles[1])
                elif eles[0] == 'golden':
                    self.step_golden(eles)
                elif eles[0] == 'save':
                    self.step_save(eles)
                elif eles[0] == 'task':
                    self.step_task(eles)
                elif eles[0] == 'cost':
                    self.step_cost(eles)
                else:
                    raise UnknownOpException(eles[0])
            except EOFError as e:
                break
            except Exception as e:
                self.logger.error(utils.describe_error(e))

if __name__ == '__main__':
    control = Controller()
    control.run()
