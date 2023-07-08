from PCB import PCB


class Process(PCB):
    def __init__(self, process_identifier, run_time, reach_time, m_max_need):
        self.process_identifier = process_identifier
        self.run_status = self.WAIT
        self.run_time = run_time
        self.residue_time = run_time  # 未运行，剩余时间等于运行所需时间
        self.reach_time = reach_time
        self.wait_time = 0
        self.last_exe_time = 0
        self.completed_time = 0
        self.m_max_need = m_max_need  # 最大需求矩阵
        self.m_alloc = [0] * len(m_max_need)  # 已分配的矩阵
        self.m_residue_need = m_max_need[:]  # 剩余需求矩阵
        self.m_request = []  # 请求矩阵

    def modify_status(self, status):
        self.run_status = status

    # 打印PCB的信息：进程运行所需时间，剩余时间，线程状态，完成的时间
    def __str__(self):
        if self.completed_time == 0:
            self.completed_time = None
        return "Process_id: {0} - run_status: {1} - require_run_time: {2} - wait_time: {3} " \
               "reach_time:{4} - completed_time:{5} - allocate: [{6}] - residue: [{7}] - max: [{8}]".format(
                self.process_identifier,
                self.run_status,
                self.run_time,
                self.wait_time,
                self.reach_time,
                self.completed_time,
                ','.join(map(str, self.m_alloc)),
                ','.join(map(str, self.m_residue_need)),
                ','.join(map(str, self.m_max_need)))
