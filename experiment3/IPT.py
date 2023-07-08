class IPT:
    t_size = 0  # 分区大小
    t_address = 0  # 分区起始地址

    def __init__(self, t_size, t_address):
        self.t_size = t_size
        self.t_address = t_address
