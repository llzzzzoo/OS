from PCB import PCB


class Process(PCB):
    residue_time = 0  # 剩余执行时间
    last_exe_time = 0  # 上一次执行的时刻
    average_time = 0  # 平均周转时间
    weighted_average_time = 0  # 带权平均周转时间

    def __init__(self, process_identifier, run_time, reach_time, completed_time):
        self.process_identifier = process_identifier
        self.run_status = self.WAIT
        self.run_time = run_time
        self.residue_time = run_time  # 未运行，剩余时间等于运行所需时间
        self.reach_time = reach_time
        self.completed_time = completed_time
        self.weighted_average_time = 1  # 初始化，权值总是为1

    def modify_status(self, status):
        self.run_status = status

    # 打印PCB的信息：进程运行所需时间，剩余时间，线程状态，完成的时间
    def __str__(self):
        if self.completed_time == 0:
            self.completed_time = None
        return "Process_id: {0} - run_status: {1} - require_run_time: {2} - wait_time: {3} - execute_time: {4} - " \
               "reach_time:{5} - completed_time:{6}".format(
                self.process_identifier,
                self.run_status,
                self.run_time,
                self.wait_time,
                self.run_time - self.residue_time,
                self.reach_time,
                self.completed_time)
