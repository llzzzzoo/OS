class Page:
    job_id = -1  # 对应的作业编号
    p_size = 1  # 页长
    p_address = 0  # 页的起始地址
    p_alloc_size = 0  # 分配在内存中的大小

    def __init__(self, job_id, p_size):
        self.job_id = job_id
        self.p_size = p_size
