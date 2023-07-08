import copy
import os
import random
import Util
import Job
import Memory
import IPT
import Page
import Segment


MEMORY_SIZE = 1024
JOB_NUMBER = 20  # 作业的数目
MIN_SIZE = 20  # 不再切割的最小分区大小
QUEUE_SIZE = 5  # 就绪队列的大小
DYNAMIC_ALLOC = 1
BASIC_PAGE = 2
BASIC_SEG = 3
C_IPT = "IPT"
C_JOB = "Job"
C_SEG = "Segment"
time_axis = 0  # 时间轴
JOB_MARK = 1
PAGE_MARK = 2
SEG_MARK = 3


# 创建num个数目的作业
def create_job_queue(number):
    job_queue = []
    for i in range(number):
        size = random.randint(100, 250)
        run_time = random.randint(1, 10)
        residue_time = run_time
        if i == 0:
            reach_time = 0
        else:
            reach_time = i + 1
        job = Job.Job(i + 1, size, run_time, reach_time, residue_time)
        job_queue.append(job)
    return job_queue


def page_job(queue):
    for item in queue:
        residue_size = item.size
        while residue_size > 0:
            alloc_size = Page.Page.p_size
            item.page_table.append(Page.Page(item.job_id, alloc_size))
            residue_size -= alloc_size


def seg_job(queue):
    for item in queue:
        residue_size = item.size
        while residue_size > 20:
            if residue_size % 2 == 0:
                alloc_size = residue_size / 2
                item.segment_table.append(Segment.Segment(item.job_id, int(alloc_size)))
            else:
                alloc_size = (residue_size - 1) / 2
                item.segment_table.append(Segment.Segment(item.job_id, int(alloc_size)))
            residue_size -= int(alloc_size)
        item.segment_table.append(Segment.Segment(item.job_id, residue_size))

def put_job(t_entry, job, alloc_size):
    job.start_address = t_entry.t_address
    job.alloc_size = alloc_size


def put_page(t_entry, page, alloc_size):
    page.p_address = t_entry.t_address
    page.p_alloc_size = alloc_size


def put_seg(t_entry, seg, alloc_size):
    seg.s_address = t_entry.t_address
    seg.s_alloc_size = alloc_size


# 回收内存
def recovery_entry(table, job, mark):
    if mark == DYNAMIC_ALLOC:
        new_entry = IPT.IPT(job.alloc_size, job.start_address)
        exe_mark = 0
        if len(table) == 0:
            table.append(new_entry)
            return
        # 根据id找到对应的表项，然后回收
        for i in range(len(table)):
            if new_entry.t_address < table[i].t_address:
                # 注意是否能合并
                if new_entry.t_address + new_entry.t_size == table[i].t_address:
                    exe_mark = 1
                    table[i].t_address = new_entry.t_address
                    table[i].t_size += new_entry.t_size
                if i - 1 >= 0:
                    if table[i - 1].t_address + table[i - 1].t_size == new_entry.t_address:
                        # 表明与后面合并过一次了
                        if exe_mark == 1:
                            table[i - 1].t_size += table[i].t_size
                            # 去除掉后面的分区
                            table.pop(i)
                        else:
                            table[i - 1].t_size += new_entry.t_size
                            exe_mark = 1
                if exe_mark == 0:
                    table.insert(i, new_entry)
                break
            if i == len(table) - 1:
                # 检测和前面的空闲分区能否合并
                if table[i].t_address + table[i].t_size == new_entry.t_address:
                    table[i].t_size += new_entry.t_size
                else:
                    table.append(new_entry)
    elif mark == BASIC_PAGE:
        for page in job.page_table:
            new_entry = IPT.IPT(page.p_alloc_size, page.p_address)
            exe_mark = 0
            if len(table) == 0:
                table.append(new_entry)
                continue
            # 根据id找到对应的表项，然后回收
            for i in range(len(table)):
                if new_entry.t_address < table[i].t_address:
                    # 注意是否能合并
                    if new_entry.t_address + new_entry.t_size == table[i].t_address:
                        exe_mark = 1
                        table[i].t_address = new_entry.t_address
                        table[i].t_size += new_entry.t_size
                    if i - 1 >= 0:
                        if table[i - 1].t_address + table[i - 1].t_size == new_entry.t_address:
                            # 表明与后面合并过一次了
                            if exe_mark == 1:
                                table[i - 1].t_size += table[i].t_size
                                # 去除掉后面的分区
                                table.pop(i)
                            else:
                                table[i - 1].t_size += new_entry.t_size
                                exe_mark = 1
                    if exe_mark == 0:
                        table.insert(i, new_entry)
                    break
                if i == len(table) - 1:
                    # 检测和前面的空闲分区能否合并
                    if table[i].t_address + table[i].t_size == new_entry.t_address:
                        table[i].t_size += new_entry.t_size
                    else:
                        table.append(new_entry)
    elif mark == BASIC_SEG:
        for seg in job.segment_table:
            new_entry = IPT.IPT(seg.s_alloc_size, seg.s_address)
            exe_mark = 0
            if len(table) == 0:
                table.append(new_entry)
                continue
            # 根据id找到对应的表项，然后回收
            for i in range(len(table)):
                if new_entry.t_address < table[i].t_address:
                    # 注意是否能合并
                    if new_entry.t_address + new_entry.t_size == table[i].t_address:
                        exe_mark = 1
                        table[i].t_address = new_entry.t_address
                        table[i].t_size += new_entry.t_size
                    if i - 1 >= 0:
                        if table[i - 1].t_address + table[i - 1].t_size == new_entry.t_address:
                            # 表明与后面合并过一次了
                            if exe_mark == 1:
                                table[i - 1].t_size += table[i].t_size
                                # 去除掉后面的分区
                                table.pop(i)
                            else:
                                table[i - 1].t_size += new_entry.t_size
                                exe_mark = 1
                    if exe_mark == 0:
                        table.insert(i, new_entry)
                    break
                if i == len(table) - 1:
                    # 检测和前面的空闲分区能否合并
                    if table[i].t_address + table[i].t_size == new_entry.t_address:
                        table[i].t_size += new_entry.t_size
                    else:
                        table.append(new_entry)


# 依靠首地址排序队列
def sort_by_head(queue, mark):
    if mark == JOB_MARK:
        queue.sort(key=lambda x: x.start_address)
    elif mark == PAGE_MARK:
        queue.sort(key=lambda x: x.p_address)
    elif mark == SEG_MARK:
        queue.sort(key=lambda x: x.s_address)


# 时间片轮转
def RR(queue):
    global time_axis
    min_job = queue[0]
    mark = 0
    for i in range(len(queue)):
        if i == 0:
            continue
        if queue[i].residue_time < min_job.residue_time:
            min_job = queue[i]
            mark = i
    time_axis += queue[mark].residue_time
    # 在队列中删除该元素并返回
    return queue.pop(mark)


def copy_table_deep(table):
    t_copy = []
    for item in table:
        t_copy.append(copy.deepcopy(item))
    return t_copy

def get_seg_queue(job_queue):
    seg_queue = []
    for item in job_queue:
        seg_queue.extend(item.segment_table)
    return seg_queue


# 基于Merge Algorith
def get_memory_situation(table, queue, mark):
    i = 0
    j = 0
    k = 0
    address = 0
    len_sum = len(table) + len(queue)
    memory_table = [None] * len_sum
    for k in range(len_sum):
        if i == len(table) or j == len(queue):
            break
        if mark == JOB_MARK:
            address = queue[j].start_address
        elif mark == PAGE_MARK:
            address = queue[j].p_address
        elif mark == SEG_MARK:
            address = queue[j].s_address
        if table[i].t_address <= address:
            memory_table[k] = table[i]
            i += 1
        else:
            memory_table[k] = queue[j]
            j += 1
    while i <= len(table) - 1:
        memory_table[k] = table[i]
        k += 1
        i += 1
    while j <= len(queue) - 1:
        memory_table[k] = queue[j]
        k += 1
        j += 1
    return memory_table


def print_table(table, queue, mark):
    if mark == DYNAMIC_ALLOC:
        # 先对queue的复制体进行排序
        job_queue = queue[:]
        sort_by_head(job_queue, JOB_MARK)
        m_queue = get_memory_situation(table, job_queue, JOB_MARK)
        print("----------Memory Situation----------")
        for item in m_queue:
            if type(item).__name__ == C_IPT:
                print("Idle Partition - initial address: {0} - size: {1}\n".format(item.t_address, item.t_size))
            elif type(item).__name__ == C_JOB:
                print("Job{0} - initial address: {1} - size: {2}\n".format(item.job_id, item.start_address, item.alloc_size))
    elif mark == BASIC_PAGE:
        seg_queue = get_seg_queue(queue)
        sort_by_head(seg_queue, PAGE_MARK)
        m_queue = get_memory_situation(table, seg_queue, PAGE_MARK)
        print("----------Memory Situation----------")
        for item in m_queue:
            if type(item).__name__ == C_IPT:
                print("Idle Partition - initial address: {0} - size: {1}\n".format(item.t_address, item.t_size))
            elif type(item).__name__ == C_SEG:
                print("Page from Job{0} - initial address: {1} - size: {2}\n".format(item.job_id, item.s_address,
                                                                                    item.s_alloc_size))
    elif mark == BASIC_SEG:
        seg_queue = get_seg_queue(queue)
        sort_by_head(seg_queue, SEG_MARK)
        m_queue = get_memory_situation(table, seg_queue, SEG_MARK)
        print("----------Memory Situation----------")
        for item in m_queue:
            if type(item).__name__ == C_IPT:
                print("Idle Partition - initial address: {0} - size: {1}\n".format(item.t_address, item.t_size))
            elif type(item).__name__ == C_SEG:
                print("Seg from Job{0} - initial address: {1} - size: {2}\n".format(item.job_id, item.s_address,
                                                                                    item.s_alloc_size))


def allocate_by_table(table, job, al_mark):
    if al_mark == DYNAMIC_ALLOC:
        # first fit
        for item in table:
            if item.t_size >= job.size:
                # 判断一下是否需要切割
                if item.t_size - job.size <= MIN_SIZE:
                    # 分配
                    put_job(item, job, item.t_size)
                    table.remove(item)
                else:
                    # 分配
                    put_job(item, job, job.size)
                    # 切割
                    item.t_address += job.size
                    item.t_size -= job.size
                return True
    elif al_mark == BASIC_PAGE:
        # basic page allocate
        copy_table = copy_table_deep(table)  # 复制分区
        copy_job_page = job.page_table[:]
        exe_count = 0  # 执行次数
        for page in copy_job_page:
            find_mark = 0
            min_ip_mark = 0
            for i in range(len(copy_table)):
                if copy_table[i].t_size >= page.p_size:
                    find_mark = 1
                    if copy_table[min_ip_mark].t_size > copy_table[i].t_size:
                        min_ip_mark = i
            # 找到位置的标记
            if find_mark == 0:
                break
            else:
                exe_count += 1
                ip = copy_table[min_ip_mark]
                # 判断一下是否需要切割
                if ip.t_size - page.p_size <= MIN_SIZE:
                    # 分配
                    put_page(ip, page, ip.t_size)
                    copy_table.remove(ip)
                else:
                    # 分配
                    put_page(ip, page, page.p_size)
                    # 切割
                    ip.t_address += page.p_size
                    ip.t_size -= page.p_size
        if exe_count > 0 and exe_count == len(job.page_table):
            table.clear()
            job.page_table.clear()
            for item in copy_table:
                table.append(item)
            for item in copy_job_page:
                job.page_table.append(item)
            return True
    elif al_mark == BASIC_SEG:
        # basic seg allocate
        copy_table = copy_table_deep(table)  # 复制分区
        copy_job_seg = job.segment_table[:]
        exe_count = 0  # 执行次数
        for seg in copy_job_seg:
            find_mark = 0
            min_ip_mark = 0
            for i in range(len(copy_table)):
                if copy_table[i].t_size >= seg.s_size:
                    find_mark = 1
                    if copy_table[min_ip_mark].t_size > copy_table[i].t_size:
                        min_ip_mark = i
            # 找到位置的标记
            if find_mark == 0:
                break
            else:
                exe_count += 1
                ip = copy_table[min_ip_mark]
                # 判断一下是否需要切割
                if ip.t_size - seg.s_size <= MIN_SIZE:
                    # 分配
                    put_seg(ip, seg, ip.t_size)
                    copy_table.remove(ip)
                else:
                    # 分配
                    put_seg(ip, seg, seg.s_size)
                    # 切割
                    ip.t_address += seg.s_size
                    ip.t_size -= seg.s_size
        if exe_count > 0 and exe_count == len(job.segment_table):
            table.clear()
            job.segment_table.clear()
            for item in copy_table:
                table.append(item)
            for item in copy_job_seg:
                job.segment_table.append(item)
            return True
    return False


def dynamic_alloc():
    global time_axis
    # 空闲分区表
    ip_table = [IPT.IPT(MEMORY_SIZE, 0)]
    # 后备队列
    job_queue = create_job_queue(JOB_NUMBER)
    # 就绪队列
    ready_queue = []
    while len(job_queue) > 0:
        job = job_queue[0]
        if job.reach_time <= time_axis and len(ready_queue) <= QUEUE_SIZE:
            if allocate_by_table(ip_table, job, DYNAMIC_ALLOC):
                job_queue.pop(0)
                ready_queue.append(job)
                # 打印内存情况
                print_table(ip_table, ready_queue, DYNAMIC_ALLOC)
                # 回到起始，查看是否还有其他当前和时间到达作业
                continue
        if len(ready_queue) != 0:
            # 按照时间片轮转法运行作业
            finish_job = RR(ready_queue)
            if finish_job is None:
                print("Failed to recovery memory!")
                return
            recovery_entry(ip_table, finish_job, DYNAMIC_ALLOC)
            # 打印内存情况
            print_table(ip_table, ready_queue, DYNAMIC_ALLOC)
        else:
            # 如果为空，则将时间轴移动到下一个元素到达的时间
            time_axis = job.reach_time
    while len(ready_queue) > 0:
        # 按照时间片轮转法运行作业
        finish_job = RR(ready_queue)
        if finish_job is None:
            print("Failed to recovery memory!")
            return
        recovery_entry(ip_table, finish_job, DYNAMIC_ALLOC)
        # 打印内存情况
        print_table(ip_table, ready_queue, DYNAMIC_ALLOC)


def basic_page():
    global time_axis
    # 空闲分区表
    ip_table = [IPT.IPT(MEMORY_SIZE, 0)]
    # 后备队列
    job_queue = create_job_queue(JOB_NUMBER)
    # 就绪队列
    ready_queue = []
    # 将作业分页
    page_job(job_queue)
    while len(job_queue) > 0:
        job = job_queue[0]
        if job.reach_time <= time_axis and len(ready_queue) <= QUEUE_SIZE:
            if allocate_by_table(ip_table, job, BASIC_PAGE):
                job_queue.pop(0)
                ready_queue.append(job)
                # 打印内存情况
                print_table(ip_table, ready_queue, BASIC_PAGE)
                # 回到起始，查看是否还有其他当前和时间到达作业
                continue
        if len(ready_queue) != 0:
            # 按照时间片轮转法运行作业
            finish_job = RR(ready_queue)
            recovery_entry(ip_table, finish_job, BASIC_PAGE)
            # 打印内存情况
            print_table(ip_table, ready_queue, BASIC_PAGE)
        else:
            # 如果为空，则将时间轴移动到下一个元素到达的时间
            time_axis = job.reach_time
    while len(ready_queue) > 0:
        # 按照时间片轮转法运行作业
        finish_job = RR(ready_queue)
        if finish_job is None:
            print("Failed to recovery memory!")
            return
        recovery_entry(ip_table, finish_job, BASIC_PAGE)
        # 打印内存情况
        print_table(ip_table, ready_queue, BASIC_PAGE)


def basic_seg():
    global time_axis
    # 空闲分区表
    ip_table = [IPT.IPT(MEMORY_SIZE, 0)]
    # 后备队列
    job_queue = create_job_queue(JOB_NUMBER)
    # 就绪队列
    ready_queue = []
    # 将作业分段
    seg_job(job_queue)
    while len(job_queue) > 0:
        job = job_queue[0]
        if job.reach_time <= time_axis and len(ready_queue) <= QUEUE_SIZE:
            if allocate_by_table(ip_table, job, BASIC_SEG):
                job_queue.pop(0)
                ready_queue.append(job)
                # 打印内存情况
                print_table(ip_table, ready_queue, BASIC_SEG)
                # 回到起始，查看是否还有其他当前和时间到达作业
                continue
        if len(ready_queue) != 0:
            # 按照时间片轮转法运行作业
            finish_job = RR(ready_queue)
            recovery_entry(ip_table, finish_job, BASIC_SEG)
            # 打印内存情况
            print_table(ip_table, ready_queue, BASIC_SEG)
        else:
            # 如果为空，则将时间轴移动到下一个元素到达的时间
            time_axis = job.reach_time
    while len(ready_queue) > 0:
        # 按照时间片轮转法运行作业
        finish_job = RR(ready_queue)
        if finish_job is None:
            print("Failed to recovery memory!")
            return
        recovery_entry(ip_table, finish_job, BASIC_SEG)
        # 打印内存情况
        print_table(ip_table, ready_queue, BASIC_SEG)


def execute(algorithm_mark):
    if algorithm_mark == DYNAMIC_ALLOC:
        dynamic_alloc()
    if algorithm_mark == BASIC_PAGE:
        basic_page()
    if algorithm_mark == BASIC_SEG:
        basic_seg()


def main():
    while 1:
        print("1.Dynamic partition allocation")
        print("2.Basic pagination")
        print("3.Basic segmentation")
        num = input("please enter your choice: ")
        if Util.check_algorith_input(num, 3):
            os.system("cls")
            algorithm = int(num)
            execute(algorithm)  # 开始执行
            break
        else:
            os.system("cls")
            print("bro what's your fking problem!!!")


if __name__ == '__main__':
    main()
