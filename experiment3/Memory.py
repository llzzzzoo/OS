class Memory:
    size = 0  # 内存大小
    begin = 0  # 内存起始地址
    end = 0  # 内存结束地址

    def __init__(self, size, begin, end):
        self.size = size
        self.begin = begin
        self.end = end
