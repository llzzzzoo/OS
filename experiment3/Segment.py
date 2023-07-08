class Segment:
    job_id = -1  # 对应的作业编号
    s_size = 0  # 段长
    s_address = 0  # 段的起始地址
    s_alloc_size = 0  # 分配在内存中的大小

    def __init__(self, job_id, s_size):
        self.job_id = job_id
        self.s_size = s_size
