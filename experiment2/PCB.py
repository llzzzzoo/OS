class PCB:
    WAIT = 'W'
    RUN = 'R'
    BLOCK = 'B'
    FINISH = 'F'
    process_identifier = 0  # 进程标识符
    run_status = None  # 运行状态
    total_sr = 0  # 需要的资源总数
    alloc_sr = 0  # 分配的资源总数
