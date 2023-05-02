import time


class Snowflake(object):
    def __init__(self, datacenter_id, machine_id, sequence=0):
        self.twepoch = 1288834974657  # 定义起始的时间戳，以毫秒为单位，用于计算id的时间戳部分
        self.datacenter_id = datacenter_id  # 数据中心ID，最大值为31
        self.machine_id = machine_id  # 机器ID，最大值为31
        self.sequence = sequence  # 序列号，最大值为4095
        self.max_sequence = 4095  # 序列号的最大值
        self.last_timestamp = -1  # 上一次生成ID的时间戳，初始化为-1

    def _gen_timestamp(self):
        # 获取当前时间戳，以毫秒为单位
        return int(time.time() * 1000)

    def _next_sequence(self):
        # 生成下一个序列号
        self.sequence = (self.sequence + 1) & self.max_sequence  # 序列号加1，并通过按位与操作保证序列号不超过最大值

        if self.sequence == 0:
            # 如果序列号达到了最大值，需要等待下一个时间片
            timestamp = self._gen_timestamp()
            while timestamp <= self.last_timestamp:
                # 等待下一个时间片
                timestamp = self._gen_timestamp()

            self.last_timestamp = timestamp  # 更新上一次生成ID的时间戳

        return self.sequence

    def generate_id(self):
        # 生成ID
        timestamp = self._gen_timestamp()

        if timestamp < self.last_timestamp:
            # 如果当前时间戳小于上一次生成ID的时间戳，说明时钟回拨了，抛出异常
            raise Exception("Clock moved backwards! Rejecting requests.")

        if timestamp == self.last_timestamp:
            # 如果当前时间戳与上一次生成ID的时间戳相同，说明需要生成下一个序列号
            sequence = self._next_sequence()
            if sequence == 0:
                # 如果序列号达到了最大值，需要等待下一个时间片
                timestamp = self._til_next_millis(self.last_timestamp)
        else:
            # 如果当前时间戳与上一次生成ID的时间戳不同，说明进入了下一个时间片，序列号需要重置为0
            self.sequence = 0

        self.last_timestamp = timestamp  # 更新上一次生成ID的时间戳

        # 生成ID，公式为：(timestamp - twepoch) << 22 | datacenter_id << 17 | machine_id << 12 | sequence
        return ((timestamp - self.twepoch) << 22) | (self.datacenter_id << 17) | (self.machine_id << 12) | self.sequence

    def _til_next_millis(self, last_timestamp):
        # 等待下一个时间片
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp


def id_generate(datacenter_id, machine_id):
    # 初始化Snowflake对象
    sf = Snowflake(datacenter_id, machine_id)

    # 生成一个唯一ID
    unique_id = sf.generate_id()

    # # 将唯一ID转化为字符串
    # unique_id_str = str(unique_id)
    #
    # # 打印唯一ID
    # print("Unique ID: ", unique_id_str)
    return unique_id
