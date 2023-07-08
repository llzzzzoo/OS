import random
import Util
import Process
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


run_process = None
ready_queue = []
backup_queue = []  # 后备队列
complete_queue = []
dispatch_count = 0
time_axis = 0
PROCESS_NUM = 50
RUN_THREAD = 5
SJF = 1
RR = 2
HRRN = 3
PRE = 1
NON = 2
COMMON_USE = 3
STEP = 1  # 轮询的步长
TIME_SLICE = 2  # 时间片的大小
r_head = 0  # 执行循环队列头部指针
r_rear = 0  # 队列的下一次插入位置


def print_queue(queue, mark):
    if len(queue) == 0:
        print("empty")
        return
    for i in queue:
        if mark > 0:
            mark -= 1
        else:
            print(i)


# 得到在当前时间到达的进程
def get_begin_process(queue, time):
    new_queue = []
    for i in range(len(queue)):
        if i == 0:
            continue
        if queue[i].reach_time == time:
            new_queue.append(queue[i])
    return new_queue


# 从第二位开始，找到当前进程应该所处的位置，根据优先级
def move_by_priority(queue, process):
    index_mark = 1
    queue.remove(process)
    for i in range(len(queue)):
        item = queue[i]
        if i == 0:
            continue
        if item.reach_time <= time_axis:
            if process.residue_time < item.residue_time:
                index_mark = i
                break
    queue.insert(index_mark, process)


# 将队列中的process元素移动到队首
def move_to_head(queue, process):
    p = process
    queue.remove(process)
    queue.insert(0, p)


# 只处理当前时间之前到达的元素，返回它的最大下标，此时队列已按照到达时间排序
def get_reach_max(queue, time):
    index = -1
    for item in queue:
        if item.reach_time <= time:
            index += 1
    return index


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


def refresh_wt_time(queue):
    for item in queue:
        # 写wait和residue是考虑到了动态的情况，即等待时间变化，运行时间变化
        item.average_time = item.wait_time + item.residue_time
        item.weighted_average_time = item.average_time / item.residue_time


def print_all(mark):
    global run_process
    print("-->Process Stars to run：\n{0}".format("none" if run_process is None else run_process))
    print("-->ready-queue：")
    print_queue(ready_queue, mark)
    print("-->completed-queue：")
    print_queue(complete_queue, 0)


# algorithm_mark = 1表明SJF；way_mark = 1表明抢占式，为2表明非抢占式
def insert_sort(queue, start_index, end_index, algorithm_mark, way_mark, new_queue):
    global dispatch_count
    global run_process
    global ready_queue
    global time_axis
    global r_head
    global r_rear
    for i in range(end_index):
        if i < start_index:
            continue
        mark = 0
        if algorithm_mark == SJF:
            if way_mark == PRE:
                # 先按照所需运行时间降序排序，这样迭代完后的队首就是优先级最高的了
                new_queue.sort(key=lambda x: x.run_time, reverse=True)
                for item in new_queue:
                    SJF_dispatch(queue, run_process, time_axis + run_process.residue_time, item)
            elif way_mark == NON or way_mark == COMMON_USE:
                if queue[i + 1].run_time < queue[i].run_time:
                    mark = 1
        elif algorithm_mark == HRRN:
            if way_mark == NON:
                if queue[i + 1].weighted_average_time > queue[i].weighted_average_time:
                    mark = 1
        elif algorithm_mark == RR:
            if way_mark == PRE:
                while len(queue) > 0:
                    # 遍历当前队列，找到已经到达的并且最先执行完的
                    for _ in range(len(queue)):
                        if queue[r_head].reach_time <= time_axis:
                            if queue[r_head].residue_time - TIME_SLICE <= 0:
                                r_rear = r_head
                                r_head = (r_head + 1) % len(queue)
                                return
                            queue[r_head].residue_time -= TIME_SLICE
                            time_axis += TIME_SLICE
                            queue[r_head].last_exe_time = time_axis
                        r_head = (r_head + 1) % len(queue)
        if mark == 1:
            temp = queue[i + 1]
            j = i
            while j >= 0 and queue[j].run_time > temp.run_time:
                queue[j + 1] = queue[j]
                j -= 1
            queue[j + 1] = temp
    return -1


# -----------------------SJF_preemptive--------------------------------
def SJF_dispatch(queue, process, end_time, next_process):
    if next_process is None:
        # 不改变列表的顺序
        return
    else:
        residue_time = process.residue_time
        inner_reach_time = next_process.reach_time
        inner_run_time = next_process.run_time  # 中途插入，必然为新进程
        inner_finish_time = inner_reach_time + inner_run_time
        process.residue_time -= next_process.reach_time - time_axis  # 修改剩余运行时间
        if inner_finish_time < end_time:
            move_to_head(queue, next_process)
            # 修改状态
            process.run_status = Process.Process.WAIT
            next_process.run_status = Process.Process.RUN
        else:
            if residue_time > inner_run_time:
                move_to_head(queue, next_process)
                # 修改状态
                process.run_status = Process.Process.WAIT
                next_process.run_status = Process.Process.RUN
            else:
                move_by_priority(queue, next_process)


# mark为1表明是第一次排序
def sort_SJF(mark, new_queue):
    global run_process
    global ready_queue
    # 进行SJF算法，每次调度后都要打印信息
    if mark == 1:
        reach_time = ready_queue[0].reach_time
        max_index = 0
        for i in range(len(ready_queue)):
            if i == 0:
                continue
            if ready_queue[i].reach_time == reach_time:
                # 得到同样到达时间的元素组的最大下标
                max_index = i
            else:
                break
        if max_index != 0:
            # 进行SJF的调度
            # 第一次执行，不是抢占式的
            insert_sort(ready_queue, 0, max_index, SJF, COMMON_USE, None)
    else:
        insert_sort(ready_queue, 0, 1, SJF, PRE, new_queue)


def SJF_exe():
    global run_process
    global time_axis
    global dispatch_count
    global ready_queue
    # 监督执行过程中是否有新到的优先级更高的进程
    # 采用轮询的方式，每一秒执行一次检查
    mark = 1
    while len(ready_queue) > 0:
        run_process = ready_queue[0]
        if run_process.reach_time > time_axis:
            time_axis = run_process.reach_time
        run_process.run_status = Process.Process.RUN
        if mark == 1:
            dispatch_count += 1
            # 更新等待时间
            refresh_wait_time(ready_queue, time_axis, PRE)
            print("----NO.", dispatch_count, "dispatch----")
            print_all(1)
            print("\n")
        # 进程执行完毕
        if run_process.residue_time == 0:
            break
        # 过程需要看一下是否有优先级高的进程中间到了
        new_process = get_begin_process(ready_queue, time_axis)
        if len(new_process) > 0:
            sort_SJF(0, new_process)
            mark = 1
        else:
            mark = 0
        time_axis += STEP  # step
        ready_queue[0].residue_time -= STEP  # 用队首是因为此时可能已经换了
        run_process.last_exe_time = time_axis
    if len(ready_queue) == 0:
        return
    # 让时间轴加上这个进程需要运行的时间
    time_axis += run_process.residue_time
    run_process.residue_time = 0
    run_process.wait_time = 0
    run_process.run_status = Process.Process.FINISH
    run_process.completed_time = time_axis
    run_process.average_time = time_axis - run_process.reach_time
    run_process.weighted_average_time = run_process.average_time / run_process.run_time
    print("time:{0}".format(time_axis))
    print("aver:{0} ".format(run_process.average_time))
    print("weigh: {0}".format(run_process.weighted_average_time))
    # 通过break离开循环，表明执行完了，则离开就绪队列
    ready_queue.remove(run_process)
    # 加入完成队列
    complete_queue.append(run_process)
    run_process = None


def SJF_pre():
    global time_axis
    exist_process = 0
    execute_count = 0
    # 创建五个进程
    for i in range(RUN_THREAD):
        # 进程所需时间在[1,10]
        run_time = random.randint(1, 10)
        if i == 0:
            reach_time = 0
        else:
            reach_time = random.randint(0, RUN_THREAD - 1)
        process = Process.Process(i + 1, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
    # 根据到达时间排序
    ready_queue.sort(key=lambda x: x.reach_time)
    print("INITIAL: ")
    print_all(0)
    print("\n")
    # 执行SJF的抢占算法
    if len(ready_queue) != 0:
        execute_count += 1
        sort_SJF(1, None)
        SJF_exe()
    # 不能等于，因为process_id为此时进程数加1
    while exist_process < PROCESS_NUM:
        process_id = exist_process + 1
        run_time = random.randint(1, 10)
        reach_time = random.randint(0, PROCESS_NUM - 1) + time_axis
        process = Process.Process(process_id, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
        execute_count += 1
        SJF_exe()
    # 将最后几个进程顺序执行就可以了
    for _ in range(RUN_THREAD - 1):
        SJF_exe()
    print("END:")
    print_all(0)
    # 完成队列的平均周转时间求平均
    average_sum = 0
    weighted_average_sum = 0
    for item in complete_queue:
        average_sum += item.average_time
        weighted_average_sum += item.weighted_average_time
    print("-->average_time：{0:.2f}".format(average_sum / PROCESS_NUM))
    print("-->weighted_average_time：{0:.2f}".format(weighted_average_sum / PROCESS_NUM))

# -----------------------SJF_preemptive--------------------------------


# -----------------------SJF_non_preemptive--------------------------------
def SJF_non_exe(queue):
    global run_process
    global time_axis
    global dispatch_count
    run_process = ready_queue.pop(0)
    run_process.run_status = Process.Process.RUN
    dispatch_count += 1
    print("----NO.", dispatch_count, "dispatch----")
    print_all(0)
    print("\n")
    run_process.residue_time = 0
    run_process.run_status = Process.Process.FINISH
    # 让时间轴加上这个进程需要运行的时间
    time_axis += run_process.run_time
    # 更新等待时间
    refresh_wait_time(queue, time_axis, NON)
    run_process.completed_time = time_axis
    run_process.wait_time = 0
    run_process.average_time = time_axis - run_process.reach_time
    run_process.weighted_average_time = run_process.average_time / run_process.run_time
    # 加入完成队列
    complete_queue.append(run_process)
    run_process = None
    # 如果下一个进程的到达时间在当前时间之后，那就等待
    if len(ready_queue) > 0 and time_axis < ready_queue[0].reach_time:
        time_axis = ready_queue[0].reach_time


# order为1表明是第一次排序
def sort_SJF_non(order):
    # 进行SJF算法，每次调度后都要打印信息
    if order == 1:
        reach_time = ready_queue[0].reach_time
        max_index = 0
        for i in range(len(ready_queue)):
            if i == 0:
                continue
            if ready_queue[i].reach_time == reach_time:
                # 统计同样到达时间的元素组的最大下标
                max_index = i
            else:
                break
        if max_index != 0:
            # 进行SJF的调度
            insert_sort(ready_queue, 0, max_index, SJF, NON, None)
    else:
        # 下标为位于当前时间轴内部的进程（当前时间其实是上一个进程的完成时间）
        index = get_reach_max(ready_queue, time_axis)
        if index > 0:
            insert_sort(ready_queue, 0, index, SJF, NON, None)


def SJF_non_pre():
    global time_axis
    exist_process = 0
    # 创建五个进程
    for i in range(RUN_THREAD):
        # 进程所需时间在[1,10]
        run_time = random.randint(1, 10)
        if i == 0:
            reach_time = 0
        else:
            reach_time = random.randint(0, RUN_THREAD - 1)
        process = Process.Process(i+1, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
    # 根据到达时间排序
    ready_queue.sort(key=lambda x: x.reach_time)
    print("INITIAL: ")
    print_all(0)
    print("\n")
    # 执行SJF的非抢占算法
    if len(ready_queue) != 0:
        sort_SJF_non(1)
        SJF_non_exe(ready_queue)
    # 不能等于，因为process_id为此时进程数加1
    while exist_process < PROCESS_NUM:
        process_id = exist_process + 1
        run_time = random.randint(1, 10)
        reach_time = random.randint(0, PROCESS_NUM - 1) + time_axis
        process = Process.Process(process_id, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
        # 按照到达时间排序
        ready_queue.sort(key=lambda x: x.reach_time)
        sort_SJF_non(0)
        SJF_non_exe(ready_queue)
    # 执行最后几个进程
    for _ in range(RUN_THREAD - 1):
        sort_SJF_non(0)
        SJF_non_exe(ready_queue)
    print("END:")
    print_all(0)
    # 完成队列的平均周转时间求平均
    average_sum = 0
    weighted_average_sum = 0
    for item in complete_queue:
        average_sum += item.average_time
        weighted_average_sum += item.weighted_average_time
    print("-->average_time：{0}".format(average_sum / PROCESS_NUM))
    print("-->weighted_average_time：{0:.2f}".format(weighted_average_sum / PROCESS_NUM))

# -----------------------SJF_non_preemptive--------------------------------


# -----------------------RR_preemptive--------------------------------

def sort_RR_pre():
    insert_sort(ready_queue, 0, 1, RR, PRE, None)


def RR_pre_exe(queue):
    global run_process
    global time_axis
    global dispatch_count
    global r_head
    global r_rear
    if len(queue) == 0:
        return
    run_process = queue.pop(r_rear)
    run_process.run_status = Process.Process.RUN
    dispatch_count += 1
    print("----NO.", dispatch_count, "dispatch----")
    print_all(0)
    print("\n")
    run_process.residue_time = 0
    run_process.run_status = Process.Process.FINISH
    # 让时间轴加上这个进程剩余需要的时间，不是时间片大小，如果在时间片之内完成，就直接结束了
    time_axis += run_process.residue_time
    run_process.last_exe_time = time_axis
    # 更新等待时间
    refresh_wait_time(queue, time_axis, PRE)
    run_process.completed_time = time_axis
    run_process.wait_time = 0
    run_process.average_time = time_axis - run_process.reach_time
    run_process.weighted_average_time = run_process.average_time / run_process.run_time
    # 加入完成队列
    complete_queue.append(run_process)
    run_process = None



def RR_pre():
    global time_axis
    global r_head
    global r_rear
    global ready_queue
    exist_process = 0
    # 创建五个进程
    for i in range(RUN_THREAD):
        # 进程所需时间在[1,10]
        run_time = random.randint(1, 10)
        if i == 0:
            reach_time = 0
        else:
            reach_time = random.randint(0, RUN_THREAD - 1)
        process = Process.Process(i + 1, run_time, reach_time, 0)
        exist_process += 1
        if process.reach_time <= time_axis:
            ready_queue.insert(r_rear, process)
            r_rear += 1
        else:
            backup_queue.append(process)
    # 根据到达时间排序
    ready_queue.sort(key=lambda x: x.reach_time)
    print("INITIAL: ")
    print_all(0)
    print("\n")
    # 执行RR的抢占算法
    if len(ready_queue) != 0:
        sort_RR_pre()
        RR_pre_exe(ready_queue)
    # 不能等于，因为process_id为此时进程数加1
    while len(backup_queue) > 0:
        insert_mark = 0  # 插入的标记
        if exist_process < PROCESS_NUM:
            process_id = exist_process + 1
            run_time = random.randint(1, 10)
            reach_time = random.randint(0, PROCESS_NUM - 1) + time_axis
            process = Process.Process(process_id, run_time, reach_time, 0)
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
    # 执行最后几个进程
    for _ in range(len(ready_queue)):
        if r_rear >= len(ready_queue) - 1:
            if r_head < r_rear:
                # 当rear不指向末尾的时候，插入或者不插入都应该执行
                r_head = r_rear - 1
            else:
                r_head = r_rear
        sort_RR_pre()
        RR_pre_exe(ready_queue)
    print("END:")
    print_all(0)
    # 完成队列的平均周转时间求平均
    average_sum = 0
    weighted_average_sum = 0
    for item in complete_queue:
        average_sum += item.average_time
        weighted_average_sum += item.weighted_average_time
    print("-->average_time：{0}".format(average_sum / PROCESS_NUM))
    print("-->weighted_average_time：{0:.2f}".format(weighted_average_sum / PROCESS_NUM))

# -----------------------RR_preemptive--------------------------------


# -----------------------HRRN_non_preemptive--------------------------------

def sort_HRRN_non(order):
    if order == 1:
        reach_time = ready_queue[0].reach_time
        max_index = 0
        for i in range(len(ready_queue)):
            if i == 0:
                continue
            if ready_queue[i].reach_time == reach_time:
                # 得到同样到达时间的元素组的最大下标
                max_index = i
            else:
                break
        if max_index != 0:
            # 进行HRRN的调度
            insert_sort(ready_queue, 0, max_index, HRRN, NON, None)
    else:
        # 下标为位于当前时间轴内部的进程（当前时间其实是上一个进程的完成时间）
        index = get_reach_max(ready_queue, time_axis)
        if index > 0:
            insert_sort(ready_queue, 0, index, HRRN, NON, None)


def HRRN_non_exe(queue):
    global run_process
    global time_axis
    global dispatch_count
    run_process = queue.pop(0)
    run_process.run_status = Process.Process.RUN
    dispatch_count += 1
    print("----NO.", dispatch_count, "dispatch----")
    print_all(0)
    print("\n")
    run_process.residue_time = 0
    run_process.run_status = Process.Process.FINISH
    # 让时间轴加上这个进程需要运行的时间
    time_axis += run_process.run_time
    # 更新等待时间
    refresh_wait_time(queue, time_axis, NON)
    # 更新权值
    refresh_wt_time(queue)
    run_process.completed_time = time_axis
    run_process.wait_time = 0
    run_process.average_time = time_axis - run_process.reach_time
    run_process.weighted_average_time = run_process.average_time / run_process.run_time
    # 加入完成队列
    complete_queue.append(run_process)
    run_process = None
    # 如果下一个进程的到达时间在当前时间之后，那就等待
    if len(ready_queue) > 0 and time_axis < ready_queue[0].reach_time:
        time_axis = ready_queue[0].reach_time


def HRRN_non_pre():
    global time_axis
    exist_process = 0
    # 创建五个进程
    for i in range(RUN_THREAD):
        # 进程所需时间在[1,10]
        run_time = random.randint(1, 10)
        if i == 0:
            reach_time = 0
        else:
            reach_time = random.randint(0, RUN_THREAD - 1)
        process = Process.Process(i+1, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
    # 根据到达时间排序
    ready_queue.sort(key=lambda x: x.reach_time)
    print("INITIAL: ")
    print_all(0)
    print("\n")
    # 执行HRRN的非抢占算法
    if len(ready_queue) != 0:
        sort_HRRN_non(1)
        HRRN_non_exe(ready_queue)
    # 不能等于，因为process_id为此时进程数加1
    while exist_process < PROCESS_NUM:
        process_id = exist_process + 1
        run_time = random.randint(1, 10)
        reach_time = random.randint(0, PROCESS_NUM - 1) + time_axis
        process = Process.Process(process_id, run_time, reach_time, 0)
        exist_process += 1
        ready_queue.append(process)
        # 按照到达时间排序
        ready_queue.sort(key=lambda x: x.reach_time)
        sort_HRRN_non(0)
        HRRN_non_exe(ready_queue)
    # 执行最后几个进程
    for _ in range(RUN_THREAD - 1):
        sort_HRRN_non(0)
        HRRN_non_exe(ready_queue)
    print("END:")
    print_all(0)
    # 完成队列的平均周转时间求平均
    average_sum = 0
    weighted_average_sum = 0
    for item in complete_queue:
        average_sum += item.average_time
        weighted_average_sum += item.weighted_average_time
    print("-->average_time：{0}".format(average_sum / PROCESS_NUM))
    print("-->weighted_average_time：{0:.2f}".format(weighted_average_sum / PROCESS_NUM))

# -----------------------HRRN_non_preemptive--------------------------------


def RR_non_pre():
    print("Ah oh, Program error!")


def HRRN_pre():
    print("Ah oh, Program error!")


def execute(number, d_way):
    if number == "1":
        if d_way == "1":
            SJF_pre()
        else:
            SJF_non_pre()
    if number == "2":
        if d_way == "1":
            RR_pre()
        else:
            RR_non_pre()
    if number == "3":
        if d_way == "1":
            HRRN_pre()
        else:
            HRRN_non_pre()


def main():
    while 1:
        print("1.SJF")
        print("2.RR")
        print("3.HRRN")
        num = input("please enter your choice: ")
        if Util.check_algorith_input(num, 1):
            os.system("cls")
            print("1.Preemptive Scheduling")
            print("2.Non-preemptive Scheduling")
            way = input("please enter your choice: ")
            if Util.check_way_input(way, 1):
                break
            else:
                os.system("cls")
                print("I already give you chance!")
        else:
            os.system("cls")
            print("bro what's your fking problem!!!")
    os.system("cls")
    execute(num, way)  # 开始执行


if __name__ == '__main__':
        main()
