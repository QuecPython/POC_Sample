import log
import modem
import osTimer
import poc
import ql_fs
import sim
from machine import UART
from usr.EventMesh import subscribe, publish

# 设置日志输出级别
log.basicConfig(level=log.INFO)
uart_log = log.getLogger("UART")
G_PWD = ""
uart_log_send_data = []
uart_log_recv_data = []
cfg_data = []


def read_cfg_from_file():
    global cfg_data
    if not cfg_data:
        cfg_data = poc.get_cfg_from_file()
    return cfg_data


class CFGConfig:

    @classmethod
    def cal_checked_num(cls, data):
        res = 0x00
        for t in data:
            res += t
        return int(res & 0xff).to_bytes(1, "big")

    @classmethod
    def pack(cls, order, data):
        if isinstance(data, str):
            data = data.encode()
        agent = cls.get_agent_pwd()
        frame = b'AT+SET='
        frame += len(agent[1]).to_bytes(1, "big")
        frame += agent[1].encode()
        frame += int(order).to_bytes(1, "big")
        data_len = len(data)
        frame += int(data_len).to_bytes(1, "big")
        frame += data
        frame += cls.cal_checked_num(data)
        frame += b'\r\n'
        return frame

    @classmethod
    def get_ip(cls, *args, **kwargs):
        print("get_ip")
        conf = read_cfg_from_file()
        if conf:
            return conf[0]

    @classmethod
    def set_default_ip(cls, *args, **kwargs):
        pass

    @classmethod
    def get_account(cls, *args, **kwargs):
        print("get_account")
        conf = read_cfg_from_file()
        if conf:
            return conf[1]
        else:
            return modem.getDevImei()[-12:]

    @classmethod
    def set_default_account(cls, *args, **kwargs):
        pass

    @classmethod
    def get_pwd(cls, *args, **kwargs):
        print("get_pwd")
        conf = read_cfg_from_file()
        if conf:
            return conf[2]
        else:
            return "111111"

    @classmethod
    def set_default_pwd(cls, *args, **kwargs):
        pass

    @classmethod
    def get_apn_name(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[3]
        else:
            return ""

    @classmethod
    def get_apn_acc(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[4]
        else:
            return ""

    @classmethod
    def get_apn_pwd(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[5]
        else:
            return ""

    @classmethod
    def get_agent_pwd(cls, *args, **kwargs):
        default_pwd = "123456"
        conf = poc.get_cfg()
        if conf:
            default_pwd = conf[6] if conf[6] else default_pwd
        return ["TYTYD998", default_pwd]

    @classmethod
    def set_default_agent(cls, *args, **kwargs):
        pass

    @classmethod
    def get_single_call_enable(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[7]
        else:
            return 0

    @classmethod
    def set_default_single(cls, *args, **kwargs):
        pass

    @classmethod
    def get_gps_enable(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[8]
        else:
            return 1

    @classmethod
    def set_default_gps(cls, *args, **kwargs):
        pass

    @classmethod
    def get_offline(cls, *args, **kwargs):
        conf = read_cfg_from_file()
        if conf:
            return conf[9]
        else:
            return 0

    @classmethod
    def set_default_offline(cls, *args, **kwargs):
        pass

    @classmethod
    def init(cls):
        subscribe("config_get_ip", cls.get_ip)
        subscribe("config_get_account", cls.get_account)
        subscribe("config_get_pwd", cls.get_pwd)
        subscribe("config_single_call_enable", cls.get_single_call_enable)
        subscribe("config_gps_enable", cls.get_gps_enable)


class UartManager(object):
    def __init__(self, no=UART.UART3, bate=115200, data_bits=8, parity=0, stop_bits=1, flow_control=0):
        self.uart = None
        self.resolver = None
        self.no = no
        self.bate = bate
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.flow_control = flow_control
        self.timer = osTimer()
        CFGConfig.init()

    def start(self):
        subscribe("uart_switch", self.switch)
        if self.resolver:
            self.resolver.start()
        if not ql_fs.path_exists('usr/config.ini'):
            ql_fs.touch('usr/config.ini', '')
            self.resolver.init()

    def switch(self, event, msg):
        if not self.uart:
            self.start_usb()
        else:
            self.close_usb()
        # self.timer.start(30000, 0, self.close_usb)

    def start_usb(self):
        self.uart = UART(self.no, self.bate, self.data_bits, self.parity, self.stop_bits, self.flow_control)
        self.uart.set_callback(self.callback)
        tts_msg = "打开USB"
        publish("poc_tts_play", tts_msg)

    def close_usb(self, *args):
        self.uart.close()
        self.uart = None
        tts_msg = "关闭USB"
        publish("poc_tts_play", tts_msg)

    def set_resolver(self, resolver):
        self.resolver = resolver

    def close(self, *args):
        self.uart.close()

    def callback(self, para):
        uart_log.info("call para:{}".format(para))
        if (0 == para[0]):
            self.uartRead(para[2])

    def write(self, data):
        # print("data:{}".format(data))
        # uart_log_send_data.append(data)
        self.uart.write(data)

    def uartRead(self, _len):
        utf8_msg = self.uart.read(_len)
        # uart_log_recv_data.append(utf8_msg)
        # uart_log.info("UartRead msg: {}".format(utf8_msg))
        self.resolver.resolve(self, utf8_msg)


class ATMeta:
    BYTES_NO_MAP = {0x30: 0, 0x31: 1, 0x32: 2}
    NO_BYTES_MAP = {0: 0x30, 1: 0x31, 2: 0x32}
    NAME = "any"
    MODE = 0

    def __init__(self, at, pwd, order, val, end=b'\r\n', msg=None):
        self.at = at
        self.pwd = pwd
        self.order = order
        self.val = val
        self.end = end
        self.msg = msg
        self.uart = None

    def set_uart(self, uart):
        self.uart = uart

    @classmethod
    def read_build(cls, at, msg):
        pos = len(at)
        pos = pos
        pwd_len = msg[pos]
        pos += 1
        pwd = msg[pos:pos + pwd_len]
        pos = pos + pwd_len
        order = msg[pos]
        return cls(at, pwd, order, None, msg=msg)

    @classmethod
    def set_build(cls, at, msg):
        pos = len(at)
        pos = pos
        pwd_len = msg[pos]
        pos += 1
        pwd = msg[pos:pos + pwd_len]
        pos = pos + pwd_len
        order = msg[pos]
        pos = pos + 1
        val_len = msg[pos]
        pos += 1
        val = msg[pos:pos + val_len]
        return cls(at, pwd, order, val, msg=msg)

    @staticmethod
    def cal_checked_num(data):
        res = 0x00
        for t in data:
            res += t
        return int(res & 0xff).to_bytes(1, "big")

    def pack(self, data):
        res = self.at + len(self.pwd).to_bytes(1, "big") + self.pwd + int(self.order).to_bytes(1, "big")

        if self.MODE:
            data_len = 1
            data = int(data).to_bytes(1, "big")
        else:
            data_len = len(data)
        res += int(data_len).to_bytes(1, "big")
        res += data
        res += self.cal_checked_num(data)
        res += self.end
        return res

    def err(self, state=0x01):
        res = b"AT+ERR=" + len(self.pwd).to_bytes(1, "big") + self.pwd + int(self.order).to_bytes(abs(state), "big")
        res += b'\x01\x01\x01\r\n'
        return self.uart.write(res)

    @staticmethod
    def get_config(meta):
        return publish("config_get", meta)

    def get(self, meta):
        data = self.get_config(meta)
        if isinstance(data, str):
            data = data.encode()
        return data

    def read(self):
        # global uart_log_send_data
        # uart_log_send_data.append("111")
        data = self.get(self.NAME)
        if self.MODE:
            data = self.NO_BYTES_MAP[data]
        return self.uart.write(self.pack(data))

    def write(self):
        if self.MODE:
            if isinstance(self.val, bytes):
                self.val = self.val[0]
            self.val = self.BYTES_NO_MAP[self.val]
        res = poc.set_cfg(self.msg)
        if res == 1:
            return self.uart.write(self.msg)
        else:
            return self.err(res)

    @classmethod
    def init(cls):
        pass

    @classmethod
    def set_default(cls):
        pass


class AT02(ATMeta):
    NO = 2
    NAME = "apn_id"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_apn_acc()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(2, "")


class AT03(ATMeta):
    NO = 3
    NAME = "apn_pwd"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_apn_pwd()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(3, "")


class AT04(ATMeta):
    NO = 4
    NAME = "poc_username"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_account()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(4, modem.getDevImei()[-12:])


class AT05(ATMeta):
    NO = 5
    NAME = "poc_password"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_pwd()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(5, "111111")


class AT06(ATMeta):
    NO = 6
    NAME = "poc_ip"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_ip()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(6, "114.141.132.4")


class AT07(ATMeta):
    NO = 7
    NAME = "user_pwd"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_agent_pwd()[1]

    # @classmethod
    # def set_default(cls):
    #     return CFGConfig.pack(7, "123456")


class AT08(ATMeta):
    NO = 8
    NAME = "gps_enable"
    MODE = 1

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_gps_enable()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(8, '0')


class AT09(ATMeta):
    NO = 9
    NAME = "offline_voice_enable"
    MODE = 1

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_offline()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(9, '0')


class AT10(ATMeta):
    NO = 10
    NAME = "single_call_enable"
    MODE = 1

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_single_call_enable()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(10, '0')


class AT11(ATMeta):
    NO = 11

    def write(self):
        super(AT11, self).write()
        # 关机
        self.uart.write(self.msg)
        # self.uart.close()
        # print("shut down...")
        publish("do_shutdown", 1)

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(11, '0')


class AT13(ATMeta):
    NO = 13
    NAME = "apn_name"

    @staticmethod
    def get_config(meta):
        return CFGConfig.get_apn_name()

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(13, '')


class AT17(ATMeta):
    NO = 17
    NAME = "iccid_enable"
    MODE = 1

    @staticmethod
    def get_config(meta):
        return poc.get_login_from_file()[1]

    @classmethod
    def set_default(cls):
        return CFGConfig.pack(17, '0')


class AT18(ATMeta):
    NO = 18
    NAME = "gps_ip"


class AT19(ATMeta):
    NO = 19
    NAME = "gps_port"


class AT20(ATMeta):
    NO = 20
    NAME = "iccid"

    @staticmethod
    def get_config(meta):
        cid = sim.getIccid()
        if cid == -1:
            cid = ""
        return cid


class ATResolver(object):
    AT_RED = b"AT+RED="
    AT_SET = b"AT+SET="

    def __init__(self):
        self.meta = None
        self.order_map = {}

    def add_order_cmd(self, order):
        self.order_map[order.NO] = order

    def resolve(self, uart, msg):
        if msg.startswith(self.AT_RED) or msg.startswith(self.AT_SET):
            pos = len(self.AT_RED)
            pwd_len = msg[pos]
            pwd = msg[pos + 1:pos + pwd_len + 1]
            pwd = pwd.decode()
            pos = pos + pwd_len + 1
            order = msg[pos]
            if msg.startswith(self.AT_RED):
                meta = self.order_map[order].read_build(self.AT_RED, msg)
                meta.set_uart(uart)
                if pwd.decode() in CFGConfig.get_agent_pwd():
                    return meta.read()
                else:
                    return meta.err()
            else:
                meta = self.order_map[order].set_build(self.AT_SET, msg)
                meta.set_uart(uart)
                return meta.write()

    def start(self):
        for val in self.order_map.values():
            val.init()

    def init(self):
        for val in self.order_map.values():
            stat = val.set_default()
            if stat:
                res = poc.set_cfg(stat)


if __name__ == '__main__':
    import _thread
    import ql_fs
    from usr.common import Abstract
    from usr.settings import get_config, CONFIG


    class ConfigStoreManager(Abstract):

        def __init__(self):
            self.file_name = "/usr/config.json"
            self.lock = _thread.allocate_lock()
            file_exist = ql_fs.path_exists(self.file_name)
            self.map = ql_fs.read_json(self.file_name) if file_exist else get_config()
            if not file_exist:
                self.__store()

        def post_processor_after_instantiation(self):
            subscribe("config_get", self.__read)
            subscribe("config_store", self.__store)
            subscribe("do_recovery", self.__do_recovery)
            subscribe("do_restore_config", self.__do_restore_config)

        def __do_recovery(self, event, msg):
            self.__store(msg=get_config())

        def __do_restore_config(self, event, msg):
            self.__store(msg=CONFIG)

        def __read(self, event=None, msg=None):
            with self.lock:
                return self.map.get(msg)

        def __store(self, event=None, msg=None):
            msg = msg if isinstance(msg, dict) else {}
            with self.lock:
                self.map.update(msg)
                ql_fs.touch(self.file_name, self.map)


    config = ConfigStoreManager()
    config.post_processor_after_instantiation()
    r = ATResolver()
    r.add_order_cmd(AT02)
    r.add_order_cmd(AT03)
    r.add_order_cmd(AT04)
    r.add_order_cmd(AT05)
    r.add_order_cmd(AT06)
    r.add_order_cmd(AT07)
    r.add_order_cmd(AT08)
    r.add_order_cmd(AT09)
    r.add_order_cmd(AT10)
    r.add_order_cmd(AT13)
    r.add_order_cmd(AT17)
    r.add_order_cmd(AT18)
    r.add_order_cmd(AT19)
    r.add_order_cmd(AT20)
    r.add_order_cmd(AT11)
    um = UartManager()
    um.set_resolver(r)
    um.start()
