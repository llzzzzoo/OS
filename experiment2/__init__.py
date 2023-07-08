import random
from PCB import PCB
from Process import Process


PROCESS_NUM = 10  # 进程总的运行数
RUN_THREAD = 5  # 可并发执行的进程数
A_NUM = 10  # A类资源的数目
B_NUM = 15  # 阿B的
C_NUM = 8  # 阿C的，其必须为偶数且为三者的最小值
SRC_NUM = 3  # 资源的数目
run_process = None
ready_queue = []  # 就绪队列
backup_queue = []  # 后备队列
block_queue = []  # 阻塞队列
complete_queue = []  # 完成队列
dispatch_count = 0
time_axis = 0
RR = 2
PRE = 1
NON = 2
TIME_SLICE = 2  # 时间片的大小
r_head = 0  # 执行循环队列头部指针
r_rear = 0  # 队列的下一次插入位置
max_queue = [A_NUM, B_NUM, C_NUM]  # 记录最大资源数目
m_avail = []  # 当前可用资源数目
m_max_need = []  # 每个进程对各类资源的最大需求量
m_alloc = []  # 每个进程对各类资源的占有量
m_residue_need = []  # 每个进程对资源的剩余需求量


# -----------------------RR_preemptive--------------------------------
def add_tow_queue(queue1, queue2):
    for i in range(len(queue1)):
        queue1[i] += queue2[i]

def check_complete(process):
    for num in process.m_residue_need:
        if num != 0:
            return False
    return True


# 当queue的值有大于最值的值返回True
def check_out_max(queue):
    for i in range(SRC_NUM):
        if queue[i] > max_queue[i]:
            return True
    return False


# 当src队列的元素全部小于或等于target的元素就返回true
def compare_queue(target, src):
    for i in range(len(target)):
        if src[i] > target[i]:
            return False
    return True


def refresh_wait_time(queue, time, d_way):
    for item in queue:
        if d_way == PRE:
            if time < item.reach_time:
                item.wait_time = 0
            else:
                item.wait_time = time - item.last_exe_time if time - item.last_exe_time > 0 else 0
        elif d_way == NON:
            if time <= item.reach_time:
                item.wait_time = 0
            else:
                item.wait_time = time - item.reach_time


# compute_mark: 1为分配，-1为还原，2为15
def change_info(process, compute_mark):
    if compute_mark == 1:
        for i in range(SRC_NUM):
            m_avail[i] -= process.m_request[i]
            process.m_alloc[i] += process.m_request[i]
            process.m_residue_need[i] -= process.m_request[i]
    elif compute_mark == -1:
        for i in range(SRC_NUM):
            m_avail[i] += process.m_request[i]
            process.m_alloc[i] -= process.m_request[i]
            process.m_residue_need[i] += process.m_request[i]
    elif compute_mark == 2:
        for i in range(SRC_NUM):
            m_avail[i] += process.m_alloc[i]
            process.m_alloc[i] = 0


# 检查请求的安全性
def check_security(queue):
    global m_residue_need
    p_len = len(queue)
    work = m_avail[:]
    finish = [0] * p_len
    for i in range(p_len):
        if finish[i] == 0:
            if compare_queue(work, m_residue_need[i].m_residue_need):
                add_tow_queue(work, m_alloc[i].m_alloc)
                finish[i] = 1
    for i in finish:
        if i == 0:
            return False
    return True


def print_queue(queue, mark):
    if len(queue) == 0:
        print("empty")
        return
    for i in range(len(queue)):
        if mark == 1 and r_rear == i:
            continue
        print(queue[i])


def print_all(mark):
    global run_process
    print("-->Process Stars to run：\n{0}".format("none" if run_process is None else run_process))
    print("-->ready-queue：")
    print_queue(ready_queue, mark)
    print("-->block-queue：")
    print_queue(block_queue, 0)
    print("-->completed-queue：")
    print_queue(complete_queue, 0)


def insert_sort(queue, start_index, end_index, algorithm_mark, way_mark):
    global dispatch_count
    global run_process
    global ready_queue
    global time_axis
    global r_head
    global r_rear
    for i in range(end_index):
        if i < start_index:
            continue
        if algorithm_mark == RR:
            if way_mark == PRE:
                # 遍历当前队列，执行RR算法
                for _ in range(len(queue)):
                    if queue[r_head].reach_time <= time_axis:
                        r_rear = r_head
                        r_head = (r_head + 1) % len(queue)
                        return
                    r_head = (r_head + 1) % len(queue)
    return -1


def sort_RR_pre():
    insert_sort(ready_queue, 0, 1, RR, PRE)


def RR_pre_exe(queue):
    global run_process
    global time_axis
    global dispatch_count
    global r_head
    global r_rear
    complete_mark = 0
    if len(queue) == 0:
        return
    # 不管完成与否，都要消耗一个时间片
    time_axis += TIME_SLICE
    run_process = queue[r_rear]
    run_process.last_exe_time = time_axis
    m_request = []
    if len(run_process.m_request) == 0:
        for i in range(SRC_NUM):
            # 发起请求
            if run_process.m_residue_need[i] == 0:
                m_request.append(0)
            else:
                m_request.append(random.randint(0, run_process.m_residue_need[i] + 2))
        run_process.m_request = m_request
    if not compare_queue(run_process.m_residue_need, run_process.m_request) or check_out_max(run_process.m_request):
        # 清空，方便下次请求
        run_process.m_request.clear()
        return
    if not compare_queue(m_avail, run_process.m_request):
        # 放入阻塞队列，并结束
        # 阻塞状态
        run_process.run_status = Process.BLOCK
        # 加入到阻塞队列后要把资源回收
        change_info(run_process, 2)
        block_queue.append(run_process)
        # 从就绪队列中删除
        queue.pop(r_rear)
        return
    # 先分配
    change_info(run_process, 1)
    # 判断是否有安全序列，若有  才分配
    if check_security(queue):
        # 分配后未完成则继续放入就绪队列，即不做改变
        if check_complete(run_process):
            complete_mark = 1
    else:
        # 还原
        change_info(run_process, -1)
        # 放入阻塞队列，并结束
        # 阻塞状态
        run_process.run_status = Process.BLOCK
        # 加入到阻塞队列后要把资源回收
        change_info(run_process, 2)
        block_queue.append(run_process)
        # 从就绪队列中删除
        queue.pop(r_rear)
        return
    run_process.run_status = Process.RUN
    dispatch_count += 1
    print("----NO.", dispatch_count, "dispatch----")
    print_all(1)
    print("\n")
    run_process.run_status = Process.WAIT
    if complete_mark == 1:
        # 改变在矩阵中的值
        add_tow_queue(m_avail, run_process.m_max_need)
        m_max_need.remove(run_process)
        m_alloc.remove(run_process)
        m_residue_need.remove(run_process)
        run_process.residue_time = 0
        run_process.run_status = Process.FINISH
        # 更新等待时间
        refresh_wait_time(queue, time_axis, PRE)
        run_process.completed_time = time_axis
        run_process.wait_time = 0
        run_process.average_time = time_axis - run_process.reach_time
        run_process.weighted_average_time = run_process.average_time / run_process.run_time
        # 从就绪队列中删除
        queue.pop(r_rear)
        # 加入完成队列
        complete_queue.append(run_process)
        run_process = None
        # 将位于阻塞队列的进程唤醒
        if len(block_queue) > 0:
            queue.insert(r_rear, block_queue.pop(0))
    else:
        # 清空，方便下次请求
        run_process.m_request.clear()
        run_process = None


def RR_pre():
    global time_axis
    global r_head
    global r_rear
    exist_process = 0
    # 创建五个进程
    for i in range(RUN_THREAD):
        # 进程所需时间在[1,10]
        run_time = random.randint(1, 10)
        if i == 0:
            reach_time = 0
            a_need = random.randint(1, A_NUM - 5)
            b_need = random.randint(1, B_NUM - 5)
            c_need = random.randint(1, 5)
        else:
            reach_time = random.randint(0, RUN_THREAD - 1)
            a_need = random.randint(1, A_NUM - 5)
            b_need = random.randint(1, B_NUM - 5)
            c_need = random.randint(1, 5)
        process = Process(i + 1, run_time, reach_time, [a_need, b_need, c_need])
        m_max_need.append(process)
        m_alloc.append(process)
        m_residue_need.append(process)
        exist_process += 1
        if process.reach_time <= time_axis:
            ready_queue.insert(r_rear, process)
            r_rear += 1
        else:
            backup_queue.append(process)
    # 根据到达时间排序
    ready_queue.sort(key=lambda x: x.reach_time)
    print("INITIAL: ")
    print_all(1)
    print("\n")
    # 执行RR的抢占算法
    if len(ready_queue) != 0:
        sort_RR_pre()
        RR_pre_exe(ready_queue)
    while len(backup_queue) > 0:
        insert_mark = 0  # 插入的标记
        if exist_process < PROCESS_NUM:
            process_id = exist_process + 1
            run_time = random.randint(1, 10)
            reach_time = random.randint(0, PROCESS_NUM - 1) + time_axis
            a_need = random.randint(1, A_NUM - 5)
            b_need = random.randint(1, B_NUM - 5)
            c_need = random.randint(1, 5)
            process = Process(process_id, run_time, reach_time, [a_need, b_need, c_need])
            m_max_need.append(process)
            m_alloc.append(process)
            m_residue_need.append(process)
            exist_process += 1
            backup_queue.append(process)
            # 根据到达时间排序
            backup_queue.sort(key=lambda x: x.reach_time)
        for item in backup_queue:
            if item.reach_time <= time_axis:
                insert_mark = 1
                ready_queue.insert(r_rear, item)
                r_rear += 1
                backup_queue.remove(item)
        if r_rear >= len(ready_queue) - 1:
            if r_head < r_rear:
                # 当rear不指向末尾的时候，插入或者不插入都应该执行
                r_head = r_rear - 1
            else:
                r_head = r_rear
        # 如果下一个进程的到达时间在当前时间之后，那就等待
        if insert_mark == 0:
            if len(backup_queue) > 0:
                time_axis = backup_queue[0].reach_time
        if len(ready_queue) > 0:
            sort_RR_pre()
            RR_pre_exe(ready_queue)
    # 执行就绪队列剩下的值
    while len(ready_queue) > 0 or len(block_queue) > 0:
        if r_rear >= len(ready_queue) - 1:
            if r_head < r_rear:
                # 当rear不指向末尾的时候，插入或者不插入都应该执行
                r_head = r_rear - 1
            else:
                r_head = r_rear
        sort_RR_pre()
        RR_pre_exe(ready_queue)
    print("END:")
    print_all(1)
    # 完成队列的平均周转时间求平均
    average_sum = 0
    weighted_average_sum = 0
    for item in complete_queue:
        average_sum += item.average_time
        weighted_average_sum += item.weighted_average_time
    print("-->average_time：{0}".format(average_sum / PROCESS_NUM))
    print("-->weighted_average_time：{0:.2f}".format(weighted_average_sum / PROCESS_NUM))

# -----------------------RR_preemptive--------------------------------


def execute():
    m_avail.append(A_NUM)
    m_avail.append(B_NUM)
    m_avail.append(C_NUM)
    RR_pre()


def main():
    print("-------------------Link Start---------------------")
    execute()
    print("--------Looking Forward To Your Next Visit--------")

if __name__ == '__main__':
      main()
