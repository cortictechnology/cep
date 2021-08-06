""" 
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021

"""

import logging
import time
from abc import abstractmethod
import collections
from curt.utils import circularlist


class BaseService:
    def __init__(self, service_type=None):
        self.service_type = service_type
        self.task_list = collections.deque(maxlen=30)
        # List of list[task, guid, msg.topic, data]
        self.workers = {}
        self.executing_task = False
        self.on_finishing_handler = lambda *_, **__: None
        self.average_execution_time = {}

    def add_task(self, task_info):
        if isinstance(task_info, list):
            self.task_list.append(task_info)
            # print("*******************")
            # print(task_info[0])
        else:
            logging.warning("task_info data is not a list, data format mismatched.")

    def task_data_has_match(self, source_guid, worker):
        has_match = False
        for task in self.task_list:
            if isinstance(task[1], list):
                if source_guid in task[1]:
                    has_match = True
            elif isinstance(task[1], dict):
                i = 0
                for render_window in task[1]:
                    if source_guid in task[1][render_window]:
                        has_match = True
                    i = i + 1
            else:
                if task[1] == source_guid:
                    has_match = True
        return has_match

    def fill_in_task_data(self, source_guid, worker, task_data):
        filled_task_data = False
        for task in self.task_list:
            if isinstance(task[1], list):
                if source_guid in task[1]:
                    task[4][0][source_guid] = [worker, task_data]
                    # print("Filled data for:", task[0])
                    filled_task_data = True
            elif isinstance(task[1], dict):
                i = 0
                for render_window in task[1]:
                    if source_guid in task[1][render_window]:
                        task[4][0][i][render_window][source_guid] = [worker, task_data]
                        filled_task_data = True
                    i = i + 1
            else:
                if task[1] == source_guid:
                    task[4][0] = task_data
                    filled_task_data = True
        return filled_task_data

    @abstractmethod
    def execute_function(self, worker, data):
        pass

    def execute_next_task(self):
        if not self.executing_task:
            self.executing_task = True
            for task in list(self.task_list):
                all_data_ready = True
                task_data = None
                if isinstance(task[1], list):
                    all_data = {}
                    if "ready_data" in task[4][0]:
                        all_data["ready_data"] = task[4][0]["ready_data"]
                        for guid in task[1]:
                            if guid not in task[4][0]:
                                all_data_ready = False
                                break
                            else:
                                all_data[guid] = task[4][0][guid][1]
                    else:
                        for guid in task[1]:
                            if guid not in task[4][0]:
                                all_data_ready = False
                                break
                            else:
                                all_data[task[4][0][guid][0]] = task[4][0][guid][1]
                    task_data = [all_data, task[4][1]]
                elif isinstance(task[1], dict):
                    all_data = {}
                    i = 0
                    for render_window in task[1]:
                        all_data[render_window] = {}
                        for guid in task[1][render_window]:
                            if guid not in task[4][0][i][render_window]:
                                all_data_ready = False
                                break
                            else:
                                all_data[render_window][
                                    task[4][0][i][render_window][guid][0]
                                ] = task[4][0][i][render_window][guid][1]
                        i = i + 1
                    task_data = [all_data, task[4][1]]
                else:
                    if task[4][0] is None:
                        all_data_ready = False
                    task_data = task[4]
                if all_data_ready:
                    # if task[4][0] is not None:
                    # t1 = time.monotonic()
                    # logging.warning("executing: " + str(task[0]))
                    worker = self.workers[task[0]]
                    result = self.execute_function(worker, task_data)
                    if task in self.task_list:
                        self.task_list.remove(task)
                    self.executing_task = False
                    self.on_finishing_handler(
                        task[0], task[1], task[2], task[3], result, self.service_type
                    )
                    # logging.warning("Finished task")
                    # if worker in self.average_execution_time:
                    #     self.average_execution_time[worker].append(
                    #         time.monotonic() - t1
                    #     )
                    # else:
                    #     self.average_execution_time[worker] = circularlist(20)
                    #     self.average_execution_time[worker].append(
                    #         time.monotonic() - t1
                    #     )
                    # logging.warning(
                    #     str(self.service_type)
                    #     + ": average execution time: "
                    #     + str(self.average_execution_time[worker].calc_average())
                    # )
                    self.execute_next_task()
            self.executing_task = False

    def get_load(self):
        return len(self.task_list)
