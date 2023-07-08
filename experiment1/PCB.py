class PCB:
    WAIT = 'W'
    RUN = 'R'
    FINISH = 'F'
    process_identifier = 0  # 进程标识符
    run_status = None  # 运行状态
    run_time = 0  # 运行时间
    wait_time = 0  # 等待CPU时间
    reach_time = 0  # 到达时刻
    completed_time = 0  # 完成时刻
