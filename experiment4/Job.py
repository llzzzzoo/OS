class Job:
    job_id = 0  # 作业的id
    track_num = 0  # 磁道号

    def __init__(self, job_id, track_num):
        self.job_id = job_id
        self.track_num = track_num
