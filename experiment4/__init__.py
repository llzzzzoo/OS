import random
from Job import Job

TRACK_NUM = 256  # 磁道数
JOB_NUM = 90  # Job的最大数量
mag_head = 100  # 磁头位置
move_mark = 1  # 移动标记，为1表明向外移，为0表明向内移动
fcfs_head = 100
sstf_head = 100
scan_head = 100
scan_mark = 1
cscan_head = 100
fscan_head = 100

def print_queue(queue):
    for item in queue:
        print("Job id: {0} - Job Track Num: {1}".format(item.job_id, item.track_num))


def get_min(queue):
    min_num = queue[0].track_num
    for item in queue:
        if item.track_num < min_num:
            min_num = item.track_num
    return min_num


def FCFS(queue):
    global mag_head
    num = 0
    for item in queue:
        track_num = item.track_num
        if track_num > mag_head:
            num += track_num - mag_head
        else:
            num += mag_head - track_num
        mag_head = track_num
    mag_head = 100
    return num


def FCFS_d(track_num):
    global fcfs_head
    if track_num > fcfs_head:
        gap_num = track_num - mag_head
    else:
        gap_num = mag_head - track_num
    fcfs_head = track_num
    return gap_num


def SSTF(queue):
    global mag_head
    copy_queue = queue[:]
    num = 0
    mark = 0
    for _ in range(len(queue)):
        index_mark = 0
        exe_count = 0
        min_dif = TRACK_NUM  # 最小差值
        for j in range(len(copy_queue)):
            track_num = copy_queue[j].track_num
            if track_num > mag_head:
                if track_num - mag_head < min_dif:
                    min_dif = track_num - mag_head
                    mark = 0
                    index_mark = j
                    exe_count = 1
            else:
                if mag_head - track_num < min_dif:
                    min_dif = mag_head - track_num
                    mark = 1
                    index_mark = j
                    exe_count = 1
        if exe_count == 1:
            if mark == 0:
                num += copy_queue[index_mark].track_num - mag_head
            else:
                num += mag_head - copy_queue[index_mark].track_num
            mag_head = copy_queue[index_mark].track_num
            copy_queue.pop(index_mark)
    mag_head = 100
    return num


def SSTF_d(queue):
    global sstf_head
    num = 0
    mark = 0
    index_mark = 0
    exe_count = 0
    min_dif = TRACK_NUM  # 最小差值
    for j in range(len(queue)):
        track_num = queue[j].track_num
        if track_num > sstf_head:
            if track_num - sstf_head < min_dif:
                min_dif = track_num - sstf_head
                mark = 0
                index_mark = j
                exe_count = 1
        else:
            if sstf_head - track_num < min_dif:
                min_dif = sstf_head - track_num
                mark = 1
                index_mark = j
                exe_count = 1
    if exe_count == 1:
        if mark == 0:
            num += queue[index_mark].track_num - sstf_head
        else:
            num += sstf_head - queue[index_mark].track_num
        sstf_head = queue[index_mark].track_num
        queue.pop(index_mark)
    return num


def SCAN(queue, mark):
    global mag_head
    global move_mark
    copy_queue = queue[:]
    num = 0
    for _ in range(len(queue)):
        index_mark = -1
        small_mark = 0
        big_mark = 0
        min_dif = TRACK_NUM  # 最小差值
        for j in range(len(copy_queue)):
            track_num = copy_queue[j].track_num
            if move_mark == -1 and track_num < mag_head:
                if mag_head - track_num < min_dif:
                    min_dif = mag_head - track_num
                    index_mark = j
                small_mark = 1
            elif move_mark == 1 and track_num > mag_head:
                if track_num - mag_head < min_dif:
                    min_dif = track_num - mag_head
                    index_mark = j
                big_mark = 1
        if index_mark != -1:
            if move_mark == -1:
                num += mag_head - copy_queue[index_mark].track_num
            elif move_mark == 1:
                num += copy_queue[index_mark].track_num - mag_head
            mag_head = copy_queue[index_mark].track_num
            copy_queue.pop(index_mark)
        if move_mark == -1:
            if small_mark == 0:
                move_mark = 1
        elif move_mark == 1:
            if big_mark == 0:
                move_mark = -1
    if mark != 1:
        mag_head = 100
    return num


def SCAN_d(queue):
    global scan_head
    global scan_mark
    num = 0
    index_mark = -1
    small_mark = 0
    big_mark = 0
    min_dif = TRACK_NUM  # 最小差值
    for j in range(len(queue)):
        track_num = queue[j].track_num
        if scan_mark == -1 and track_num < scan_head:
            if scan_head - track_num < min_dif:
                min_dif = scan_head - track_num
                index_mark = j
            small_mark = 1
        elif scan_mark == 1 and track_num > scan_head:
            if track_num - scan_head < min_dif:
                min_dif = track_num - scan_head
                index_mark = j
            big_mark = 1
    if index_mark != -1:
        if scan_mark == -1:
            num += scan_head - queue[index_mark].track_num
        elif scan_mark == 1:
            num += queue[index_mark].track_num - scan_head
        scan_head = queue[index_mark].track_num
        queue.pop(index_mark)
    if scan_mark == -1:
        if small_mark == 0:
            scan_mark = 1
    elif scan_mark == 1:
        if big_mark == 0:
            scan_mark = -1
    return num


def CSCAN(queue):
    global mag_head
    copy_queue = queue[:]
    num = 0
    count = 0
    while True:
        count += 1
        if count == len(queue):
            break
        index_mark = -1
        exe_mark = 0
        min_dif = TRACK_NUM  # 最小差值
        for j in range(len(copy_queue)):
            track_num = copy_queue[j].track_num
            if track_num > mag_head:
                if track_num - mag_head < min_dif:
                    min_dif = track_num - mag_head
                    index_mark = j
                exe_mark = 1
        if index_mark != -1:
            num += copy_queue[index_mark].track_num - mag_head
            mag_head = copy_queue[index_mark].track_num
            copy_queue.pop(index_mark)
        if exe_mark == 0:
            # 把最小磁道号给磁头
            mag_head = get_min(copy_queue)
            count -= 1
    mag_head = 100
    return num


def CSCAN_d(queue):
    global cscan_head
    num = 0
    index_mark = -1
    exe_mark = 0
    min_dif = TRACK_NUM  # 最小差值
    for j in range(len(queue)):
        track_num = queue[j].track_num
        if track_num > cscan_head:
            if track_num - cscan_head < min_dif:
                min_dif = track_num - cscan_head
                index_mark = j
            exe_mark = 1
    if index_mark != -1:
        num += queue[index_mark].track_num - cscan_head
        cscan_head = queue[index_mark].track_num
        queue.pop(index_mark)
    if exe_mark == 0:
        # 把最小磁道号给磁头
        cscan_head = get_min(queue)
        num = -1
    return num


def FSCAN(i_queue, new_queue):
    return SCAN(i_queue, 1) + SCAN(new_queue, 1)


def FSCAN_d(i_queue, new_queue):
    return SCAN_d(i_queue) + SCAN_d(new_queue)


def execute():
    # 作业队列
    job_queue = []
    for i in range(10):
        job_queue.append(Job(i + 1, random.randint(1, 256)))
    print("-----------------Ten Job--------------------------")
    print_queue(job_queue)
    print("FCFS Average Seek Length: {0}".format(int(FCFS(job_queue) / 10)))
    print("SSTF Average Seek Length: {0}".format(int(SSTF(job_queue) / 10)))
    print("SCAN Average Seek Length: {0}".format(int(SCAN(job_queue, 0) / 10)))
    print("CSCAN Average Seek Length: {0}".format(int(CSCAN(job_queue) / 10)))
    print("FSCAN Average Seek Length: {0}".format(int(FSCAN(job_queue[:4], job_queue[5:]) / 10)))
    print("--------------------------------------------------\n")
    print("--------------One Hundred Job---------------------")
    exist_job = 0
    job_queue.clear()
    fcfs_num = 0
    sstf_num = 0
    scan_num = 0
    cscan_num = 0
    fscan_num = 0
    fcfs_queue = []
    sstf_queue = []
    scan_queue = []
    cscan_queue = []
    fscan_i_queue = []
    fscan_n_queue = []
    copy_queue = []
    count = 0
    for i in range(10):
        new_job = Job(exist_job + 1, random.randint(1, 256))
        job_queue.append(new_job)
        fcfs_queue.append(new_job)
        sstf_queue.append(new_job)
        scan_queue.append(new_job)
        cscan_queue.append(new_job)
        fscan_i_queue.append(new_job)
        exist_job += 1
    while True:
        count += 1
        if count == JOB_NUM:
            break
        while random.randint(1, 4) > 2 and exist_job < JOB_NUM:
            new_job = Job(exist_job + 1, random.randint(1, 256))
            job_queue.append(new_job)
            fcfs_queue.append(new_job)
            sstf_queue.append(new_job)
            scan_queue.append(new_job)
            cscan_queue.append(new_job)
            fscan_n_queue.append(new_job)
            exist_job += 1
        if len(fcfs_queue) == 0:
            continue
        fcfs_num += FCFS_d(fcfs_queue[0].track_num)
        fcfs_queue.pop(0)
        copy_queue.append(job_queue.pop(0))
        sstf_num += SSTF_d(sstf_queue)
        scan_num += SCAN_d(scan_queue)
        num = CSCAN_d(cscan_queue)
        if num == -1:
            count -= 1
        else:
            cscan_num += num
        fscan_num += FSCAN_d(fscan_i_queue, fscan_n_queue)
    print_queue(copy_queue)
    print("FCFS Average Seek Length: {0}".format(int(fcfs_num / exist_job)))
    print("SSTF Average Seek Length: {0}".format(int(sstf_num / exist_job)))
    print("SCAN Average Seek Length: {0}".format(int(scan_num / exist_job)))
    print("CSCAN Average Seek Length: {0}".format(int(cscan_num / exist_job)))
    print("FSCAN Average Seek Length: {0}".format(int(fscan_num / exist_job)))
    print("--------------------------------------------------\n")


def main():
    print("-------------------Link Start---------------------")
    execute()
    print("--------Looking Forward To Your Next Visit--------")


if __name__ == '__main__':
    main()
