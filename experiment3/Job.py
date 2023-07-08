from JCB import JCB


class Job(JCB):
    alloc_size = 0  # 在内存中分配的内存大小
    residue_time = 0  # 作业剩余的执行时间

    def __init__(self, job_id, size, run_time, reach_time, residue_time):
        self.job_id = job_id
        self.size = size
        self.run_time = run_time
        self.reach_time = reach_time
        self.residue_time = residue_time
        self.page_table = []  # 页表
        self.segment_table = []  # 段表
