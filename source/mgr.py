import net
import sim
import modem
import utime
import ql_fs
import audio
import AW9523
import _thread
import dataCall
import checkNet
import usys as sys
from queue import Queue
from sensor import Handmic
from misc import Power, PowerKey
import uos
import poc
from usr.hkt66 import HKT66
from usr.location import GNSSUtil, CoordinateSystemConvert
from usr.EventMesh import subscribe, publish, publish_async
from usr.common import Abstract, create_thread, LogAdapter, OSTIMER
from usr.settings import get_config, CONFIG, MEDIA_DIR, PROJECT_NAME, PROJECT_VERSION

log = LogAdapter(__name__)


class Btn:
    def __init__(self, name, num, release_meta, long_meta=None, long_time=2000, sync=True):
        self.name = name
        self.num = num
        self.release_meta = release_meta
        self.long_meta = long_meta
        self.long_time = long_time
        self.long_flag = False
        self.timer = OSTIMER("Btn")
        self.sync = sync

    def press(self):
        self.timer.stop()
        self.timer.start(self.long_time, 0, self.long)
        publish("btn_opt")

    def publish(self, tps):
        if not self.sync:
            if isinstance(tps, list):
                publish_async(*tps)
            else:
                publish_async(tps)
        else:
            if isinstance(tps, list):
                publish(*tps)
            else:
                publish(tps)

    def long(self, *args):
        if self.long_meta:
            self.long_flag = True
            if isinstance(self.long_meta, str):
                self.publish(self.long_meta)
            else:
                self.long_meta(self.name)

    def release(self):
        self.timer.stop()
        if not self.long_flag:
            if isinstance(self.release_meta, str) or isinstance(self.release_meta, list):
                publish("btn_opt")
                self.publish(self.release_meta)
            else:
                publish("btn_opt")
                self.release_meta(self.name)
        self.long_flag = False


class ConfigStoreManager(Abstract):

    def __init__(self):
        self.file_name = "/_bak/config.json"
        _backup_root_dir = '/_bak'
        _fs = uos.VfsLfs1(32, 32, 32, "customer_backup_fs")
        # print("uos.listdir", uos.listdir())
        uos.mount(_fs, _backup_root_dir)
        file_exist = ql_fs.path_exists(self.file_name)
        self.map = ql_fs.read_json(self.file_name) if file_exist else get_config()
        if not file_exist:
            self.__store()

    def post_processor_after_instantiation(self):
        subscribe("config_get", self.__read)
        subscribe("config_update", self.__config_update)
        subscribe("config_store", self.__store)
        subscribe("store_config", self.__store_config)
        subscribe("do_recovery", self.__do_recovery)
        subscribe("do_restore_config", self.__do_restore_config)
        # _thread.start_new_thread(self.__store_file, ())

    def __store_config(self, event, msg):
        ql_fs.touch(self.file_name, self.map)

    def __config_update(self, event, msg):
        self.update(event, msg)

    def __do_recovery(self, event, msg):
        self.update(msg=get_config())
        ql_fs.touch(self.file_name, self.map)
        if ql_fs.path_exists('usr/config.ini'):
            uos.remove('usr/config.ini')

    def __do_restore_config(self, event, msg):
        self.update(msg=CONFIG)
        ql_fs.touch(self.file_name, self.map)

    def __read(self, event=None, msg=None):
        return self.map.get(msg)

    def update(self, event=None, msg=None):
        msg = msg if isinstance(msg, dict) else {}
        self.map.update(msg)

    def __store(self, event=None, msg=None):
        self.update(event, msg)
        ql_fs.touch(self.file_name, self.map)


class LedManager(Abstract):
    """This class is for control LED"""

    def __init__(self):
        """LED object init"""
        self.__led_timer = OSTIMER("LedManager")
        self.__last_task = None
        self.__last_task_name = None
        self.__led_mode = {
            "heartbeat_led": [self.heartbeat_indicator_light, 5000, 1],
            "low_heartbeat_led": [self.low_heartbeat_indicator_light, 1200, 1],
            "net_error": [self.net_state_light, 1000, 1]
        }
        self.__intercom_status_red = 0
        self.__intercom_status_blue = 0

    def post_processor_after_instantiation(self):
        """订阅此类所有的事件到 EventMesh中"""
        subscribe("start_led_timer", self.start_flicker)
        subscribe("stop_led_timer", self.stop_flicker)
        subscribe("reset_led_timer", self.reset_led_timer)
        subscribe("ptt_led", self.press_ptt_light)
        subscribe("ptt_receive_led", self.receive_ptt_light)
        subscribe("get_intercom_status_blue", self.__get_intercom_status_blue)
        # self.start_flicker(data="heartbeat_led")

    def red_on(self):
        """Set led on"""
        if publish("io_u57_get", 8):
            publish("io_u57_set", (8, 0))
        if not publish("io_u57_get", 9):
            publish("io_u57_set", (9, 1))

    def red_off(self):
        """Set led off"""
        # print("Set led off")
        # if self.__intercom_status_red == 0 or self.__intercom_status_blue == 1:
        if publish("io_u57_get", 9):
            publish("io_u57_set", (9, 0))

    def blue_on(self):
        """Set led on"""

        if publish("io_u57_get", 9):
            publish("io_u57_set", (9, 0))
        if not publish("io_u57_get", 8):
            publish("io_u57_set", (8, 1))

    def blue_off(self):
        """Set led off"""
        # if self.__intercom_status_blue == 0 or self.__intercom_status_red == 1:
        if publish("io_u57_get", 8):
            publish("io_u57_set", (8, 0))

    def _heartbeat_indicator_light(self, *args):
        self.blue_on()
        utime.sleep_ms(500)
        self.blue_off()

    def heartbeat_indicator_light(self, args):
        '''心跳指示灯'''
        _thread.start_new_thread(self._heartbeat_indicator_light, ())

    def _low_heartbeat_indicator_light(self, *args):
        self.red_on()
        utime.sleep_ms(800)
        self.red_off()

    def low_heartbeat_indicator_light(self, args):
        '''低于 3.4v 心跳指示灯'''
        _thread.start_new_thread(self._low_heartbeat_indicator_light, ())

    def press_ptt_light(self, topic, data):
        '''按下PTT 灯指示'''
        # print("press_ptt_light:{}".format(data))
        self.__intercom_status_red = data
        if data:
            # ptt按下
            self.stop_flicker()
            self.blue_off()
            self.red_on()
        else:
            # ptt抬起
            self.red_off()
            self.start_flicker()

    def receive_ptt_light(self, topic, data):
        '''接收ptt会话指示灯'''
        # print("receive_ptt_light:{}".format(data))
        self.__intercom_status_blue = data
        if data:

            # 开始说话
            self.stop_flicker()
            self.red_off()
            self.blue_on()
        else:

            # 会话结束
            # print("会话结束")
            self.blue_off()
            self.start_flicker()

    def __get_intercom_status_blue(self, event, mode):
        return self.__intercom_status_blue

    def _net_state_light(self, *args):
        # print("_net_state_light:blue_off")
        for _ in range(2):
            self.blue_on()
            utime.sleep_ms(200)
            self.blue_off()
            utime.sleep_ms(100)

    def net_state_light(self, args):
        '''SIM卡，信号指示灯'''
        _thread.start_new_thread(self._net_state_light, ())

    def start_flicker(self, topic=None, data=None):
        """Start led flicker"""
        if data:
            mode_list = self.__led_mode.get(data)
            self.__last_task = mode_list
            self.__last_task_name = data
        elif self.__last_task:
            mode_list = self.__last_task
        else:
            return
        self.__led_timer.start(mode_list[1], mode_list[2], mode_list[0])

    def stop_flicker(self, topic=None, data=None):
        """Stop LED flicker"""
        self.__led_timer.stop()

    def reset_led_timer(self, topic=None, data=None):
        if data == 2:
            led_task = "heartbeat_led"
        else:
            led_task = "net_error"
        if self.__last_task_name != led_task:
            # print("start flicker")
            self.stop_flicker()
            self.start_flicker(topic, led_task)


class AW9523Manager(Abstract):
    _AW9523_DEFAULT_ADDR_KEY = 0x58
    _AW9523_DEFAULT_ADDR_IO = 0x5B

    def __init__(self, en_gpion, extint_gpio, i2cn):
        self.__en_gpio = Pin(en_gpion, Pin.OUT, Pin.PULL_DISABLE, 1)
        # IO control extention
        self.u57 = AW9523(i2c=i2cn, addr=self._AW9523_DEFAULT_ADDR_IO)
        # IO Key control extention
        self.u58 = AW9523(i2c=i2cn, addr=self._AW9523_DEFAULT_ADDR_KEY, int_pin=extint_gpio,
                          callback=self.u58_key_callback)
        # TODO: Weather to disable GNSS when device power on or not.
        self.__u57io_init()
        self.__u58_uid = None

        self.os_voice_timer = OSTIMER("AW9523Manager")
        self.voice_flag = False
        self.btn_no_dict = {
            0: Btn(None, 0, "btn_up", "btn_up_long", long_time=3000),
            1: Btn(None, 1, "btn_down", "btn_down_long"),
            2: Btn(None, 2, "btn_ok", "poc_switch_voice", sync=True),
            3: Btn(None, 3, "btn_back", "btn_back_long"),
            4: Btn(None, 4, "btn_sos", "btn_sos_long", long_time=3000),
            5: Btn(None, 5, "btn_back", "btn_back_long"),
            6: Btn(None, 6, "btn_sos", "btn_sos_long", long_time=3000),
            12: Btn(None, 12, "btn_group"),
        }
        self.first_line = None
        self.first_line_edge = 0
        self.coder = None
        self.eliminate_first_jitter = False

    def encoder_callback(self, args):
        if args == 2:
            publish("poc_add_vol_event")
        else:
            publish("poc_reduce_vol_event")

    def __u57io_init(self):
        # Enable GNSS
        self.u57_set(msg=(7, 1))
        # Enable TF
        self.u57_set(msg=(11, 1))
        # Disable BT
        self.u57_set(msg=(13, 0))

    def post_processor_after_instantiation(self):
        subscribe("io_u58_get", self.u58_get)
        subscribe("io_u57_set", self.u57_set)
        subscribe("io_u57_get", self.u57_get)

    def initialization(self):
        # self.__u58key_thread_run()
        self.u58.pin(0, mode=1, interrupt_enable=1)
        self.u58.pin(1, mode=1, interrupt_enable=1)
        self.u58.pin(2, mode=1, interrupt_enable=1)
        self.u58.pin(3, mode=1, interrupt_enable=1)
        self.u58.pin(4, mode=1, interrupt_enable=1)
        self.u58.pin(5, mode=1, interrupt_enable=1)
        self.u58.pin(6, mode=1, interrupt_enable=1)
        self.u58.pin(7, mode=1, interrupt_enable=1)
        # TODO: This is NCHRG GPIO.
        # self.u58.pin(9, mode=1, interrupt_enable=1)
        self.u58.pin(10, mode=1, interrupt_enable=1)
        self.u58.pin(11, mode=1, interrupt_enable=1)
        self.u58.pin(12, mode=1, interrupt_enable=1)
        self.u58.pin(13, mode=1, interrupt_enable=1)
        # self.u58.pin(14, mode=1, interrupt_enable=1)
        # self.coder = encoder(Pin.GPIO10, Pin.GPIO13)
        # self.coder.set_callback(self.encoder_callback)

    def enable(self):
        return True if self.__en_gpio.write(1) == 0 else False

    def disable(self):
        return True if self.__en_gpio.write(0) == 0 else False

    def u58_get(self, event=None, msg=None):
        _val = self.u58.read(msg)
        return _val

    def u57_set(self, event=None, msg=None):
        no, val = msg
        if no >= 0 and no <= 14 and val in (0, 1):
            self.u57.pin(no, mode=0, value=val)
            return True
        return False

    def u57_get(self, event=None, msg=None):
        _val = self.u57.read(msg)
        # log.debug("IO U57 get %s, %s" % (msg, _val))
        return _val

    def clear_btn(self, args):
        # print("clear btn...")
        pass

    def consume_switch_btn(self, event):
        pass

    def u58_key_callback(self, event):
        if event[0] == 12 and not self.eliminate_first_jitter:
            self.eliminate_first_jitter = True
            return
        if event[0] == 13:
            return
        if event[0] == 14:
            return
        # 按键回调
        btn = self.btn_no_dict.get(event[0])
        if btn:
            if event[1]:
                btn.release()
            else:
                btn.press()
        else:
            if event[0] == 9:
                publish("battery_charge_callback")
            elif event[0] == 10:
                publish("sd_card_mount")
            elif event[0] == 11:
                publish("btn_ptt", event)


BATTERY_OCV_TABLE = {
    "nix_coy_mnzo2": {
        25: {
            4138: 100, 4068: 95, 4008: 90, 3960: 85, 3918: 80, 3876: 75, 3831: 70, 3790: 65, 3754: 60, 3720: 55,
            3692: 50, 3665: 45, 3640: 40, 3625: 35, 3608: 30, 3599: 25, 3589: 20, 3574: 15, 3511: 10, 3556: 5, 3515: 0,
        },
    },
}

from machine import Pin, ExtInt
from misc import Power, ADC


class Battery(object):
    """This class is for battery info.

    This class can get battery voltage and energy.
    if adc_args is not None, use cbc to read battery

    adc_args: (adc_num, adc_period, factor)

        adc_num: ADC channel num
        adc_period: Cyclic read ADC cycle period
        factor: calculation coefficient
    """

    def __init__(self, adc_args=None, chrg_gpion=None, stdby_gpion=None):
        self.__energy = 100
        self.__temp = 25

        # ADC params
        self.__adc = None
        if adc_args:
            self.__adc_num, self.__adc_period, self.__factor = adc_args
            if not isinstance(self.__adc_num, int):
                raise TypeError("adc_args adc_num is not int number.")
            if not isinstance(self.__adc_period, int):
                raise TypeError("adc_args adc_period is not int number.")
            if not isinstance(self.__factor, float):
                raise TypeError("adc_args factor is not int float.")
            self.__adc = ADC()

        # Charge params
        self.__charge_callback = None
        self.__charge_status = None
        self.__chrg_gpion = chrg_gpion
        self.__stdby_gpion = stdby_gpion
        self.__chrg_gpio = None
        self.__stdby_gpio = None
        self.__chrg_exint = None
        self.__stdby_exint = None
        if self.__chrg_gpion is not None and self.__stdby_gpion is not None:
            self.__init_charge()

    def __chrg_callback(self, args):
        self.__update_charge_status()
        if self.__charge_callback is not None:
            self.__charge_callback(self.__charge_status)

    def __stdby_callback(self, args):
        self.__update_charge_status()
        if self.__charge_callback is not None:
            self.__charge_callback(self.__charge_status)

    def __update_charge_status(self):
        if self.__chrg_gpio.read() == 1 and self.__stdby_gpio.read() == 1:
            self.__charge_status = 0
        elif self.__chrg_gpio.read() == 0 and self.__stdby_gpio.read() == 1:
            self.__charge_status = 1
        elif self.__chrg_gpio.read() == 1 and self.__stdby_gpio.read() == 0:
            self.__charge_status = 2
        else:
            raise TypeError("CHRG and STDBY cannot be 0 at the same time!")

    def __init_charge(self):
        self.__chrg_gpio = Pin(self.__chrg_gpion, Pin.IN, Pin.PULL_DISABLE)
        self.__stdby_gpio = Pin(self.__stdby_gpion, Pin.IN, Pin.PULL_DISABLE)
        self.__chrg_exint = ExtInt(self.__chrg_gpion, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, self.__chrg_callback)
        self.__stdby_exint = ExtInt(self.__stdby_gpion, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU,
                                    self.__stdby_callback)
        self.__chrg_exint.enable()
        self.__stdby_exint.enable()
        self.__update_charge_status()

    def __get_soc_from_dict(self, key, volt_arg):
        """Get battery energy from map"""
        if key in BATTERY_OCV_TABLE["nix_coy_mnzo2"]:
            volts = sorted(BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].keys(), reverse=True)
            pre_volt = 0
            volt_not_under = 0  # Determine whether the voltage is lower than the minimum voltage value of soc.
            for volt in volts:
                if volt_arg > volt:
                    volt_not_under = 1
                    soc1 = BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].get(volt, 0)
                    soc2 = BATTERY_OCV_TABLE["nix_coy_mnzo2"][key].get(pre_volt, 0)
                    break
                else:
                    pre_volt = volt
            if pre_volt == 0:  # Input Voltarg > Highest Voltarg
                return soc1
            elif volt_not_under == 0:
                return 0
            else:
                return soc2 - (soc2 - soc1) * (pre_volt - volt_arg) // (pre_volt - volt)

    def __get_soc(self, temp, volt_arg, bat_type="nix_coy_mnzo2"):
        """Get battery energy by temperature and voltage"""
        if bat_type == "nix_coy_mnzo2":
            if temp > 30:
                return self.__get_soc_from_dict(55, volt_arg)
            elif temp < 10:
                return self.__get_soc_from_dict(0, volt_arg)
            else:
                return self.__get_soc_from_dict(25, volt_arg)

    def __get_power_vbatt(self):
        test_vbatt = sum([Power.getVbatt() for i in range(100)])
        return int(test_vbatt / 100)

    def __get_adc_vbatt(self):
        self.__adc.open()
        utime.sleep_ms(self.__adc_period)
        adc_list = list()
        for i in range(self.__adc_period):
            adc_list.append(self.__adc.read(self.__adc_num))
            utime.sleep_ms(self.__adc_period)
        adc_list.remove(min(adc_list))
        adc_list.remove(max(adc_list))
        adc_value = int(sum(adc_list) / len(adc_list))
        self.__adc.close()
        vbatt_value = adc_value * (self.__factor + 1)
        return vbatt_value

    def set_temp(self, temp):
        """Set now temperature."""
        if isinstance(temp, int) or isinstance(temp, float):
            self.__temp = temp
            return True
        return False

    def get_voltage(self):
        """Get battery voltage"""

        if self.__adc is None:
            return self.__get_power_vbatt()
        else:
            return self.__get_adc_vbatt()

    def get_energy(self):
        """Get battery energy"""
        self.__energy = self.__get_soc(self.__temp, self.get_voltage())
        # self.__energy = self.get_voltage()
        return self.__energy

    def set_charge_callback(self, charge_callback):
        if self.__chrg_gpion is not None and self.__stdby_gpion is not None:
            if callable(charge_callback):
                self.__charge_callback = charge_callback
                return True
        return False

    def get_charge_status(self):
        return self.__charge_status


class BatteryManager(Abstract):
    def __init__(self):
        """电池管理器"""
        self.battery = Battery()
        self.low_battery = False
        self.__callback = print

    def get_battery(self, event=None, msg=None):
        battery = self.battery.get_energy()
        return battery

    def post_processor_after_instantiation(self):
        subscribe("battery_charge_state", self.charge_state)
        subscribe("battery_level", self.level)
        subscribe("battery_charge_callback", self.__chrg_callback)

    def __chrg_callback(self, event=None, msg=None):
        log.debug("Battery Charge State change.")
        publish("top_bottom_info_init")
        self.__callback(self.charge_state())

    def set_callback(self, callback):
        self.__callback = callback

    def charge_state(self, event=None, msg=None):
        # TODO: Now NCHRG GPIO can not check charge status.
        # return publish("io_u58_get", 9)
        return 1

    def level(self, event=None, msg=None):
        return self.get_battery()


class MapManager(Abstract):

    def __init__(self, wk2114):
        self.__gnss = GNSSUtil(wk2114)
        self.__csc = CoordinateSystemConvert()
        self.gps_info_flag = True
        self.longitude = ""
        self.latitude = ""
        self.lng_direct = ""
        self.lat_direct = ""
        self.stars = ""
        self.timer = OSTIMER("MapManager")

    def post_processor_after_instantiation(self):
        subscribe("get_location_map", self.get_location_map)
        subscribe("map_gnss_state", self.gnss_state)
        subscribe("map_gnss_enable", self.gnss_enable)
        subscribe("map_gnss_disable", self.gnss_disable)
        subscribe("get_gps_info", self.get_gps_info)
        subscribe("get_gps_flag", self.get_gps_flag)

    def initialization(self):
        if publish("config_gps_enable"):
            _thread.start_new_thread(self.get_location, ())

    def get_location(self, *args):
        while True:
            if publish("config_gps_enable"):
                try:
                    self.do_location()
                except Exception:
                    pass
                utime.sleep(2)
            else:
                break

    def do_location(self, event=None, msg=None):
        if publish("config_gps_enable"):
            self.gnss_enable()
            gnss_data = self.__gnss.data(5)
            if gnss_data:
                self.lng_direct = gnss_data["lng_direct"]
                self.lat_direct = gnss_data["lat_direct"]
                self.stars = gnss_data["stars"]
                # log.debug("gnss_data: %s" % str(gnss_data))
                self.longitude, self.latitude = self.__csc.wgs84_to_gcj02(float(gnss_data["Longitude"]),
                                                                          float(gnss_data["Latitude"]))
                self.gps_info_flag = True
                publish("push_gps_enable", self.gps_info_flag)
                publish("push_gps_upload", [self.longitude, self.latitude])
                return 1
            else:
                self.gps_info_flag = False
                publish("push_gps_enable", self.gps_info_flag)
        self.longitude = ""
        self.latitude = ""
        self.lng_direct = ""
        self.lat_direct = ""
        self.stars = ""
        return -2

    def get_location_map(self, event=None, msg=None):
        # GNSS VCC & V_BAVKUP enable.
        # res = self.do_location()
        res = -2
        # print("--------", self.longitude, self.latitude)
        if self.longitude and self.latitude:
            res = publish("poc_loc_map", (self.longitude, self.latitude, 250, 125))
        return res

    def get_gps_flag(self, event, msg):
        return self.gps_info_flag

    def get_gps_info(self, event, msg):
        return {
            "longitude": str(self.longitude),
            "latitude": str(self.latitude),
            "stars": self.stars,
            "lng_direct": self.lng_direct,
            "lat_direct": self.lat_direct
        }

    def gnss_state(self, event=None, msg=None):
        return publish("io_u57_get", 7)

    def gnss_enable(self, event=None, msg=None):
        if self.gnss_state() == 0:
            publish("io_u57_set", (7, 1))
        return self.gnss_state()

    def gnss_disable(self, event=None, msg=None):
        if self.gnss_state() == 1:
            publish("io_u57_set", (7, 0))
        return self.gnss_state()


class DeviceInfoManager(Abstract):

    def __init__(self, horn_gpion):
        self.__city = None
        self.__location = None
        self.__power_key = PowerKey()
        self.timer = OSTIMER("DeviceInfoManager")
        self.shut_flag = False
        self.__power_key.powerKeyEventRegister(self.pwk_callback, 1)
        self.__horn_gpio = Pin(horn_gpion, Pin.OUT, Pin.PULL_PU, 0)
        self.__noise_p = Pin(Pin.GPIO46, Pin.OUT, Pin.PULL_DISABLE, 0)
        self.net_timer = OSTIMER("net_timer")
        self.sim_flag = False
        net.setCallback(self.net_callback)

    def set_horn(self, event, msg):
        if msg:
            self.__horn_gpio.write(0)
            self.__horn_gpio = Pin(Pin.GPIO42, Pin.OUT, Pin.PULL_PU, 1)
        else:
            self.__horn_gpio.write(0)
            self.__horn_gpio = Pin(Pin.GPIO3, Pin.OUT, Pin.PULL_PU, 1)

    def post_processor_after_instantiation(self):
        # 订阅此类所有的事件到 EventMesh中
        subscribe("screen_get_ope", self.get_device_ope)
        subscribe("screen_get_sig", self.get_signal)
        subscribe("screen_get_time", self.get_time)
        subscribe("about_get_imei", self.get_imei)
        subscribe("about_get_iccid", self.get_iccid)
        subscribe("about_get_phonenum", self.get_phone_num)
        subscribe("about_get_sysversion", self.get_sysversion)
        subscribe("about_get_product", self.get_product)
        subscribe("about_get_module", self.get_module)
        subscribe("screen_get_battery", self.get_battery)
        subscribe("get_poc_fw_version", self.get_device_fw_version)
        subscribe("get_sn_num", self.get_sn_num)
        subscribe("get_ip_addr", self.get_ip_addr)
        subscribe("get_sim_status", self.get_sim_status)
        subscribe("get_standby_time", self.get_standby_time)
        subscribe("sim_slot_get", self.sim_slot_get)
        subscribe("sim_slot_switch", self.sim_slot_switch)
        subscribe("sd_status_get", self.sd_status_get)
        subscribe("sd_card_mount", self.sd_card_mount)
        subscribe("sd_card_mount", self.sd_card_mount)
        subscribe("horn_open", self.horn_open)
        subscribe("horn_close", self.horn_close)
        subscribe("set_noise_mode", self.set_noise_mode)
        subscribe("set_horn", self.set_horn)
        subscribe("check_net", self.check_net)
        publish("set_noise_mode", int(publish("config_get", "noise_onoff")))
        sim.setSwitchcardCallback(self.sim_callback)

    def net_callback(self, *args):
        self.net_timer.stop()
        self.net_timer.start(180000, 0, self.check_net)

    def check_net(self, topic=None, msg=None):
        if not dataCall.getInfo(1, 0)[2][0]:
            self.__sim_slot_switch()

    def set_noise_mode(self, event=None, msg=None):
        self.__noise_p.write(msg)

    def get_product(self, event, msg):
        product_name = publish("config_get", "product_name")
        if not product_name:
            product_name = "--"
        return product_name

    def get_module(self, event, msg):
        return modem.getDevFwVersion()[:10]

    def initialization(self):
        publish("sd_card_mount")

    def get_device_ope(self, event, msg):
        # 获取设备运营商信息
        net_ope_map = {
            "UNICOM": "中国联通",
            "CMCC": "中国移动",
            "CT": "中国电信"
        }
        short_eons = "--"
        full_eons = "--"
        try:
            operator_info = net.operatorName()
            if isinstance(operator_info, tuple):
                short_eons = operator_info[1]
                full_eons = operator_info[0]
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))
        return net_ope_map.get(short_eons, full_eons) if publish("config_get", "language") == "CN" else full_eons

    def get_signal(self, event=None, msg=None):
        # 获取信号事件
        return net.csqQueryPoll()

    def get_time(self, event=None, msg=None):
        # 获取时间事件
        local_time = utime.localtime()
        if publish("config_get", "language") == "CN":
            week_num = {
                0: "周一",
                1: "周二",
                2: "周三",
                3: "周四",
                4: "周五",
                5: "周六",
                6: "周日",
            }
        else:
            week_num = {
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
                6: "Saturday",
            }
        date = "{0:02d}-{1:02d}-{2:02d} {3}".format(local_time[0], local_time[1], local_time[2],
                                                    week_num.get(local_time[6], ""))
        time = "{0:02d}:{1:02d}".format(local_time[3], local_time[4])
        result = [date, time]
        return result

    def get_imei(self, event, msg):
        # 获取imsi号s事件
        return modem.getDevImei()

    def get_iccid(self, event, msg):
        # 获取ic cid事件
        iccid = sim.getIccid()
        if iccid == -1:
            iccid = ""
        return iccid

    def get_phone_num(self, event, msg):
        # 获取电话号码事件
        return sim.getPhoneNumber()

    def get_battery(self, event=None, msg=None):
        # 获取电池事件,暂时没支持
        battery_level = int(publish("battery_level") / 20)
        if battery_level == 5:
            battery_level = 4
        if battery_level == 0:
            battery_level = 1
        if publish("battery_charge_state") == 0:
            img_path = MEDIA_DIR + "charge_" + str(battery_level) + ".png"
        else:
            img_path = MEDIA_DIR + "battery_" + str(battery_level) + ".png"
        return img_path

    def get_device_fw_version(self, *args):
        # 获取设备固件版本号
        fw_version = modem.getDevFwVersion()
        return fw_version if isinstance(fw_version, str) else "--"

    def get_sysversion(self, event=None, msg=None):
        return PROJECT_VERSION

    def get_sn_num(self, event=None, msg=None):
        return modem.getDevSN() if modem.getDevSN() else "--"

    def get_ip_addr(self, event=None, msg=None):
        ip = "0.0.0.0"
        try:
            net_info = dataCall.getInfo(1, 0)
            if net_info != -1 and isinstance(net_info, tuple):
                ip = net_info[2][2]
        except Exception as e:
            log.error(str(e))
        return ip

    def get_sim_status(self, event=None, msg=None):
        return sim.getStatus()

    def get_standby_time(self, *args):
        # 获取设备单次开机待机时间
        time_msg = utime.time()
        # The int call removes the decimals.  Conveniently, it always rounds down.  int(2.9) returns 2 instead of 3, for example.
        d = int(time_msg / 86400)
        # This updates the value of x to show that the already counted seconds won't be double counted or anything.
        time_msg -= (d * 86400)
        h = int(time_msg / 3600)
        time_msg -= (h * 3600)
        m = int(time_msg / 60)
        time_msg -= (m * 60)
        s = time_msg
        result = "{}天{}小时{}分{}秒".format(d, h, m, s)
        return result

    def sim_slot_get(self, topic=None, msg=None):
        return sim.getCurSimid()

    def sim_slot_switch(self, topic=None, slot=None):
        # sim 卡槽切换
        # :return: 切换sim卡卡槽  0 切换成功, 1 无需切换, -1 切换失败
        # print("sim slot {} {}".format(self.sim_slot_get(), slot))
        if self.sim_slot_get() == slot:
            state = 1
        else:
            state = self.__sim_slot_switch(slot)
        return state

    def __sim_slot_switch(self, mode=None):
        slot = self.sim_slot_get()
        if mode:
            return sim.switchCard(mode)
        else:
            return sim.switchCard(1 - slot)

    def sim_callback(self, args):
        if sim.getImsi() == -1:
            # 证明sim 不存在
            self.sim_flag = True
            self.__sim_slot_switch()
        else:
            if self.sim_flag:
                publish("sim_switch_show", 0)
            else:
                publish("sim_switch_show", 1)
            publish("push_sim_slot", self.sim_slot_get())
            self.sim_flag = False

    def sd_card_state(self):
        return publish("io_u58_get", 10)

    def sd_card_mount(self, event=None, msg=None):
        _state = self.sd_card_state()
        log.debug("sd_card_state %s" % _state)
        if _state == 0:
            log.debug("SD Card In.")
            if "sd" not in uos.listdir("/"):
                try:
                    udev = uos.VfsSd("sd_fs")
                    uos.mount(udev, "/sd")
                except Exception as e:
                    sys.print_exception(e)
                    log.error(str(e))
        else:
            log.debug("SD Card Out.")
            if "sd" in uos.listdir("/"):
                try:
                    uos.umount("/sd")
                except Exception as e:
                    sys.print_exception(e)
                    log.error(str(e))
        publish("push_sd_status", self.sd_card_state())

    def sd_status_get(self, event=None, msg=None):
        return self.sd_card_state()

    def horn_open(self, event=None, msg=None):
        publish("io_u57_set", (1, 0))
        publish("io_u57_set", (4, 0))
        publish("io_u57_set", (0, 0))
        publish("io_u57_set", (5, 0))
        self.__horn_gpio.write(1)

    def horn_close(self, event=None, msg=None):
        self.__horn_gpio.write(0)

    def shutdown(self, *args):
        self.shut_flag = False
        publish("do_shutdown")

    def pwk_callback(self, args):
        if self.shut_flag:
            return
        publish("lcd_state_manage")
        if args == 1:
            self.timer.start(3000, 0, self.shutdown)
        else:
            self.timer.stop()


class NetManager(Abstract):
    THRESHOLD = 10

    def __init__(self):
        self.__data_call = dataCall
        self.__data_call.setCallback(self.__datacall_cb)
        self.__net = net
        self.check_net = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
        self.timer = OSTIMER("NetManager")
        self.check_net_timeout = 100 * 1000
        self.error_count = 0
        self.net_state = 0

    def post_processor_after_instantiation(self, *args, **kwargs):
        subscribe("set_net_check_time", self.set_keepalive)

    def initialization(self, *args, **kwargs):
        self.check_net.poweron_print_once()
        self.wait_connect(10)

    def __datacall_cb(self, args):
        pdp = args[0]
        nw_sta = args[1]
        if nw_sta == 1:
            self.net_state = 2
            log.debug("*** network %d connected! ***" % pdp)
            publish("reset_led_timer", 2)
        else:
            self.net_state = 3
            log.debug("*** network %d not connected! ***" % pdp)
            publish("reset_led_timer", 1)

    def start_keepalive(self):
        self.timer.start(self.check_net_timeout, 1, self.__check)

    def set_keepalive(self, event, msg):
        self.timer.stop()
        self.check_net_timeout = msg
        self.start_keepalive()

    def __check(self, args):
        self.net_state = self.get_net_status()
        if self.net_state == 2:
            if self.error_count:
                self.error_count = 0
        else:
            self.error_count += 1

    def wait_connect(self, timeout):
        # self.check_net.wait_network_connected(timeout)
        # if res[0] == 3 and res[1] == 1:
        #     publish("reset_led_timer", 2)
        # else:
        #     publish("reset_led_timer", 1)
        pass

    def get_net_status(self):
        data_call_res = self.__data_call.getInfo(1, 0)
        if data_call_res != -1:
            return 2 if data_call_res[2][0] else 3
        else:
            return 3


class BluetoothManager(Abstract):

    def __init__(self, aw9523, wk2114):
        self.__hkt66 = HKT66(aw9523, wk2114)
        self.__hkt66.set_callback(self.__callback)
        self.__queue = Queue()
        self.__uid = None
        self.__state = 0
        self.__search_tid = None

    def post_processor_after_instantiation(self, *args, **kwargs):
        subscribe("bluetooth_state", self.state)
        subscribe("bluetooth_open", self.open)
        subscribe("bluetooth_close", self.close)

    def initialization(self):
        if publish("config_get", "bluetooth_onoff"):
            self.open()

    def __start_bt_callback(self):
        self.__uid = create_thread(self.__bt_callback, stack_size=0x4000)

    def __stop_bt_callback(self):
        if self.__uid:
            try:
                _thread.stop_thread(self.__uid)
            except Exception as e:
                sys.print_exception(e)
        self.__uid = None

    def __callback(self, args):
        self.__queue.put(args)

    def __bt_callback(self):
        while True:
            args = self.__queue.get()
            log.debug("BluetoothManager callback args: %s" % str(args))
            if args[0] in (3, 4):
                self.__state = args[0]
                if self.__state == 3:
                    publish("horn_close")
                    self.__hkt66.voice_connect()
                if self.__state == 4:
                    self.__hkt66.voice_disconnect()
                    publish("horn_open")
                publish("top_bottom_info_init")
            elif args[0] in (0xFD, 0x01):
                publish("poc_speak", 1)
            elif args[0] in (0xFE, 0x02):
                publish("poc_speak", 0)
            elif args[0] == 0xC3:
                publish("load_screen", {"screen": "member_screen", "init": True})
            elif args[0] == 0xC4:
                publish("btn_ok")
            elif args[0] == 0xC5:
                publish("btn_ok")

    def __search_device(self):
        while publish("config_get", "bluetooth_onoff") and self.__state != 3:
            try:
                start_time = utime.ticks_ms()
                change_mode_res = self.__hkt66.change_mode()
                log.debug("change_mode_res: %s" % change_mode_res)
                self.__state = change_mode_res
                if self.__state == 3:
                    publish("horn_close")
                    self.__hkt66.voice_connect()
                    publish("top_bottom_info_init")
                    break
                else:
                    self.__hkt66.voice_disconnect()
                    publish("horn_open")
                    search_match_res = self.__hkt66.search_match()
                    log.debug("search_match_res: %s" % search_match_res)
                    wait_time = utime.ticks_diff(utime.ticks_ms(), start_time)
                    utime.sleep_ms((15 * 1000 - wait_time) if wait_time < (15 * 1000 - 5) else 5)
            except Exception as e:
                sys.print_exception(e)
                utime.sleep_ms(15 * 1000)

    def state(self, event=None, msg=None):
        """Blue tooth state

        Args:
            event ([type]): [description] (default: `None`)
            msg ([type]): [description] (default: `None`)

        Returns:
            int:
                0 - close
                1 - open
                3 - connected
                4 - not connected
        """
        return self.__state

    def open(self, event=None, msg=None):
        self.__start_bt_callback()
        self.__hkt66.running()
        res = self.__hkt66.enable()
        log.debug("self.__hkt66.enable() %s" % res)
        log.debug("self.__hkt66.enable() %s" % res)
        self.__state = self.__hkt66.state
        log.debug("self.__hkt66.state %s" % self.__state)
        self.__search_tid = create_thread(self.__search_device, stack_size=0x2000)
        # change_mode_res = self.__hkt66.change_mode()
        # log.debug("change_mode_res: %s" % change_mode_res)
        # if change_mode_res == 4:
        #     search_match_res = self.__hkt66.search_match()
        #     log.debug("search_match_res: %s" % search_match_res)
        #     change_mode_res = self.__hkt66.change_mode()
        #     log.debug("change_mode_res: %s" % change_mode_res)
        # self.__state = change_mode_res
        # if self.__state == 3:
        #     publish("horn_close")
        #     self.__hkt66.voice_connect()
        # else:
        #     self.__hkt66.voice_disconnect()
        #     publish("horn_open")
        # publish("top_bottom_info_init")

    def close(self, event=None, msg=None):
        self.__hkt66.disconnect()
        self.__hkt66.stop()
        self.__hkt66.disable()
        self.__state = self.__hkt66.state
        self.__stop_bt_callback()
        publish("horn_open")
        publish("top_bottom_info_init")
        return self.state()


class HandMicManager(Abstract):

    def __init__(self):
        self.__handmic = Handmic(40, self.__btn_callback)
        self.__btn_timer = OSTIMER("HandMicManager")
        self.__btn_no = None
        self.__btn_level = None
        self.__btn_handle_time = 0
        self.__nums_key = []
        self.btn_no_dict = {
            0: Btn(None, 0, "btn_ok", "poc_switch_voice", sync=True),
            1: Btn(None, 1, "btn_up", "btn_up_long"),
            2: Btn(None, 2, "btn_down", "btn_down_long"),
            15: Btn("1", 15, self.release_btn, self.btn_handle),
            16: Btn("2", 16, self.release_btn, self.btn_handle),
            17: Btn("3", 17, self.release_btn, self.btn_handle),
            18: Btn(None, 18, ["load_screen", {"screen": "group_screen", "init": True}], "group_btn_long"),
            11: Btn("4", 11, self.release_btn, self.btn_handle),
            12: Btn("5", 12, self.release_btn, self.btn_handle),
            13: Btn("6", 13, self.release_btn, self.btn_handle),
            14: Btn(None, 14, ["load_screen", {"screen": "member_screen", "init": True}]),
            7: Btn("7", 7, self.release_btn, self.btn_handle),
            8: Btn("8", 8, self.release_btn, self.btn_handle),
            9: Btn("9", 9, self.release_btn, self.btn_handle),
            10: Btn(None, 10, ["load_screen", {"screen": "friend_screen", "init": True}]),
            3: Btn(None, 3, "btn_back", self.btn_handle),
            4: Btn("0", 4, self.release_btn, self.btn_handle),
            # 5: Btn("MEMBER", ["load_screen", {"screen": "group_screen", "init": True}]),
        }

    def release_btn(self, args):
        publish("btn_num_click", args)

    def btn_handle(self, *args):
        publish("btn_handle", args[0])
        # publish("poc_tts_play", "快捷键设置成功" if publish("config_get", "language") == "CN" else "")

    def post_processor_after_instantiation(self, *args, **kwargs):
        subscribe("hand_mic_open", self.open)
        subscribe("hand_mic_close", self.close)
        subscribe("hand_mic_ptt_callback", self.__extfun)

    def initialization(self):
        if publish("bluetooth_state") != 3:
            publish("horn_open")
        self.open()

    def open(self, event=None, msg=None):
        publish("io_u57_set", (14, 1))
        self.__handmic.start()

    def close(self, event=None, msg=None):
        publish("io_u57_set", (14, 0))

    def __extfun(self, event=None, args=None):
        publish("poc_speak", 1 - args[1])

    def __btn_callback(self, args):
        # log.debug("__btn_callback args: %s" % str(args))
        btn = self.btn_no_dict.get(args[1])
        if btn:
            if args[0] == 1:
                btn.press()
            else:
                btn.release()


class SPEAK_MODE:
    NONE = 0
    RECV_CALL = 1
    SEND_CALL = 2


class ALLOW_SPEAK_MODE:
    YES = 1
    NO = 1


class PocManager(Abstract):
    def __init__(self, noise_reduction_gpion):
        self.__ip = ""
        self.__username = ""
        self.__password = ""
        self.__login_info = []
        self.__state = 0
        # 记录更新的数据, 方便中英文变更后推送变更消息
        self.__last_update_state_info = None
        self.__sos_start_flag = False
        self.__call_usr = None
        self.__call_user_info = None
        self.__callusr_resp = {}
        self.__group_id = None
        self.__group_name = None
        self.__member_dict = {}
        self.__group_list = []
        self.__group_number_list = {}
        self.__members = []
        self.__weather_data = {}
        self.__nr_onoff_gpio = Pin(noise_reduction_gpion, Pin.OUT, Pin.PULL_DISABLE, 1)
        self.__record_state = 0
        self.__audio = None
        self.__tts_ready = 0
        self.__speak_tag = SPEAK_MODE.NONE
        self.vol = None
        self.last_volume = 3
        self.__call_timer = OSTIMER("call_timer")
        self.__allow_break = ALLOW_SPEAK_MODE.YES
        self.__weather_refresh = 0
        self.__first_join_group = True
        self.call_state = 0
        self.__single_call_state = 4
        audio.set_earphoneDet(self.det_call)
        state = audio.get_earphoneStatus()
        if state:
            publish("set_horn", 1)
        self.audi_det = audio.Audio(0)
        self.vol_no_map = {
            0: 0,
            1: 4,
            2: 5,
            3: 6,
            4: 7,
            5: 8,
            6: 9,
            7: 10,
            8: 11,
        }
        self.no_vol_map = {
            0: 0,
            4: 1,
            5: 2,
            6: 3,
            7: 4,
            8: 5,
            9: 6,
            10: 7,
            11: 8,
        }
        self.call_level_map = {
            0: 15,
            1: 13,
            2: 10,
            3: 8,
            4: 6,
            5: 4,
            6: 2
        }
        self.poc_timer = OSTIMER("poc_time")
        self.poc_timer.start(15000, 1, self.refresh_callback)
        self.__single_call_usr_name = ""

    def refresh_callback(self, *args):
        publish_async("top_bottom_info_init")

    def det_call(self, para):
        # print("earphone det:", para)
        if para == 1:
            publish("set_horn", 1)
        elif para == 2:
            publish("set_horn", 0)

    def post_processor_after_instantiation(self, *args, **kwargs):
        subscribe("poc_current_group", self.current_group)
        subscribe("poc_groups", self.groups)
        subscribe("poc_members", self.members)
        subscribe("poc_weather", self.weather)
        subscribe("poc_joingroup", self.joingroup)
        subscribe("poc_speak", self.speak)
        subscribe("poc_calluser", self.calluser)
        subscribe("poc_loginstate", self.get_login_state)
        subscribe("poc_userstate", self.userstate)
        subscribe("poc_record_onoff", self.record_onoff)
        subscribe("poc_query_records", self.query_records)
        subscribe("poc_play_record", self.play_record)
        subscribe("poc_stop_play_record", self.stop_play_record)
        subscribe("poc_delete_record", self.delete_record)
        subscribe("poc_tts_play", self.tts_play)
        subscribe("poc_tts_ready", self.tts_ready)
        subscribe("poc_switch_voice", self.poc_switch_voice)
        subscribe("poc_loc_map", self.loc_map)
        subscribe("poc_get_login_info", self.get_login_info)
        subscribe("about_get_user", self.about_get_user)
        subscribe("push_gps_upload", self.push_gps_upload)

        subscribe("audio_volume", self.get_volume)
        subscribe("audio_volume_get", self.audio_volume_get)
        subscribe("audio_add_volume", self.add_volume)
        subscribe("audio_reduce_volume", self.reduce_volume)
        subscribe("push_state_info", self.push_state_info)
        subscribe("push_store_vol", self.store_vol)
        subscribe("get_speak_state", self.get_speak_state)

        subscribe("noise_switch", self.noise_switch)
        subscribe("call_level_sel", self.call_level_sel)
        subscribe("tts_play_group", self.tts_play_group)
        subscribe("start_sos", self.start_sos)
        subscribe("language_update", self.language_update)
        subscribe("poc_record_get_folder_list", self.poc_record_get_folder_list)
        subscribe("poc_stop_sos", self.stop_sos)
        # subscribe("store_vol", self.store_vol)

    def poc_record_get_folder_list(self, event, msg):
        return poc.record_get_folder_list()

    def push_gps_upload(self, event, msg):
        poc.gps_send_location(*msg)

    def language_update(self, event, msg):
        publish("config_store", {"language": msg})
        if self.__last_update_state_info:
            self.push_state_info(*self.__last_update_state_info)

    def get_speak_state(self, event=None, msg=None):
        return self.__speak_tag

    def noise_switch(self, event=None, msg=None):
        publish("config_set", {"noise_onoff": msg})

    def call_level_sel(self, event=None, msg=None):
        poc.set_icmic_gain(6, self.call_level_map.get(msg))
        publish("config_set", {"call_level_no": msg})

    def initialization(self):
        # TODO: Init audio for recording.
        # self.__audio = audio.Audio(1)
        self.__volume_init()
        # 开启录音回路
        self.__nr_onoff_gpio.write(0)
        publish("io_u57_set", (12, 1))
        call_level_no = publish("config_get", "call_level_no")
        self.call_level_sel(msg=call_level_no)

    def about_get_user(self, event, msg):
        return self.get_login_info()[2]

    def poc_init(self):
        self.__ip = publish("config_get_ip")
        self.__username = publish("config_get_account")
        self.__password = publish("config_get_pwd")
        log.debug("poc config ip: %s, username: %s, password %s" % (self.__ip, self.__username, self.__password))
        if self.__ip and self.__username and self.__password:
            self.open()

    def __poc_init_callback(self, args):
        log.debug("__poc_init_callback args: %s" % str(args))
        publish("push_state_info")

    def __join_group_callback(self, args):
        log.debug("__join_group_callback args: %s" % str(args))
        self.__group_name, self.__group_id = args
        publish("push_state_info")
        publish("poc_join_group")
        self.get_member_list()
        # publish("main_screen_weather_refresh")
        # tts_msg = ("加入群组%s" % self.__group_name) if publish("config_get", "language") == "CN" else ("Join group %s" % self.__group_name)
        tts_msg = ("加入群组%s" % self.__group_name) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        publish("top_bottom_info_init")
        if self.__first_join_group:
            self.__first_join_group = False
            publish("reset_led_timer", 2)
            publish_async("main_screen_weather_refresh")

    def get_member_list(self):
        self.__member_dict = {}
        for member in poc.get_memberlist(self.__group_id):
            self.__member_dict[member[0]] = member

    def tts_play_group(self, event, msg):
        if self.__group_name:
            tts_msg = ("加入群组%s" % self.__group_name) if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            print("poc_tts_play", tts_msg)

    def __listupdate_callback(self, args):
        log.debug("__listupdate_callback args: %s" % str(args))
        if args == 1:
            self.groups()
        elif args == 2:
            self.members(msg=self.__group_id)

    def __notify_speak_callback(self, args):
        self.__call_timer.stop()
        self.call_state = args[1]
        publish("speak_notify", 0)
        if args[1]:
            self.__allow_break = args[0]
            self.__speak_tag = SPEAK_MODE.RECV_CALL
            self.push_state_info(msg=2, speak_tag=4)
            if self.__single_call_usr_name:
                call_name = self.__single_call_usr_name
            else:
                call_obj = self.__member_dict.get(args[1])
                if not call_obj:
                    self.get_member_list()
                    call_obj = self.__member_dict.get(args[1])
                call_name = call_obj[1]
            # print("msg = {} call_name = {} speak_tag = {}".format(2, call_name, 4))
            self.push_state_info(msg=2, member_name=call_name, speak_tag=4)
            publish("ptt_receive_led", 1)
            publish("lcd_state_manage")
            publish("single_call_notify", 1)
        else:
            if self.__speak_tag == SPEAK_MODE.SEND_CALL:
                self.__speak_tag = SPEAK_MODE.NONE
                if self.__allow_break:
                    publish("ptt_led", 1)
                    self.push_state_info(msg=1, speak_tag=4)
                    self.__allow_break = args[0]
                    return
            elif self.__speak_tag == SPEAK_MODE.RECV_CALL:
                self.__speak_tag = SPEAK_MODE.NONE
            self.push_state_info()
            publish("ptt_receive_led", 0)
            publish("single_call_notify", 0)
            self.__allow_break = args[0]

    def get_login_info(self, event=None, msg=None):
        self.__login_info = poc.get_loginstate()
        if not self.__login_info:
            self.__login_info = [0, -1, modem.getDevImei()[-12:]]
        return self.__login_info

    def get_login_state(self, event=None, msg=None):
        self.get_login_info()
        self.__state = self.__login_info[0]
        return self.__state

    def push_state_info(self, event=None, msg=0, member_name=None, speak_tag=None):
        self.__last_update_state_info = [event, msg, member_name, speak_tag]
        self.get_login_info()
        group_data = self.current_group()
        group_name = group_data[0] if group_data and group_data[0] else "--"
        member_name = member_name if member_name else self.__login_info[-1]
        state = [msg, group_name, self.userstate(speak_tag=speak_tag), member_name]
        publish("call_info_refresh", state)

    def userstate(self, event=None, msg=None, speak_tag=None):
        if not speak_tag:
            speak_tag = self.__speak_tag
        default_state = "--"
        if publish("config_get", "language") == "CN":
            user_states = {
                0: "离线",
                1: "登陆中",
                2: "在线",
                3: "注销中",
                4: "正在说话",
            }
        else:
            user_states = {
                0: "Offline",
                1: "Logging in",
                2: "Online",
                3: "Logging out",
                4: "Talking",
            }
        return user_states.get(self.get_login_state() if speak_tag == 0 else 4, default_state)

    def ctrl_pa_cb(self, args):
        publish("record_pa_ctrl", args)

    def open(self):
        if self.__state == 0:
            poc.init(self.__poc_init_callback)
            poc.register_join_group_cb(self.__join_group_callback)
            poc.register_listupdate_cb(self.__listupdate_callback)
            poc.register_notify_spker_cb(self.__notify_speak_callback)
            poc.register_invite_info_cb(self.register_invite_info_cb)
            poc.register_sos_cb(self.register_sos_cb)
            poc.register_ctrl_pa_cb(self.ctrl_pa_cb)
            res = poc.open_app(True)
            self.record_onoff(msg=1)
            log.debug("PocManager open over")
            return self.get_login_state()

    def start_sos(self, event=None, msg=None):
        if not self.__sos_start_flag:
            poc.report_alarm(0.00, 0.00)
            self.__sos_start_flag = True
            publish("sos_notify", self.__username)
        else:
            self.stop_sos()
            self.__sos_start_flag = False
            publish("sos_notify", 0)

    def stop_sos(self, event=None, msg=None):
        if self.__sos_start_flag:
            poc.stop_alarm()
            self.__sos_start_flag = False
            publish("load_screen", {"screen": "menu_screen"})

    def register_sos_cb(self, args):
        publish("lcd_state_manage")
        publish("sos_notify", args)
        if args:
            self.__sos_start_flag = True
        else:
            self.__sos_start_flag = False

    def register_invite_info_cb(self, args):
        publish("lcd_state_manage")
        if args[0] == 5:
            # 别人拉入单呼群组
            self.__single_call_state = 5
            self.__single_call_usr_name = args[1]
            publish("load_screen", {"screen": "SingleCallScreen", "info": args})
            tts_msg = str(self.__single_call_usr_name) + "呼叫我" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
        elif args[0] == 4:
            # 别人退出单呼 | 自己退出单呼
            self.__single_call_state = 4
            self.__single_call_usr_name = ""
            publish("poc_speak", 0)
            tts_msg = "退出单[=dan1]呼" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            publish("load_screen", {"screen": "menu_screen"})
        elif args[0] == 6:
            tts_msg = "账户或者密码错误" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
        elif args[0] == 0:
            # 自己主呼
            self.__single_call_state = 0
            self.__single_call_usr_name = args[1]
            tts_msg = "呼叫成功" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            publish("load_screen", {"screen": "SingleCallScreen", "info": self.__call_user_info})
        elif args[0] == 3 or args[0] == 2:
            self.__single_call_state = 4
            self.__single_call_usr_name = ""
            publish("poc_speak", 0)
            if args[0] == 2:
                tts_msg = "单[=dan1]呼失败" if publish("config_get", "language") == "CN" else ""
            else:
                tts_msg = "呼叫失败" if publish("config_get", "language") == "CN" else ""
            print("poc_tts_play {}".format(tts_msg))
            publish("poc_tts_play", tts_msg)
            publish("load_screen", {"screen": "menu_screen"})

    def current_group(self, event=None, msg=None):
        return (self.__group_name, self.__group_id)

    def groups(self, event=None, msg=None):
        if self.__group_list:
            return self.__group_list
        if self.__state == 2:
            grouplist = poc.get_grouplist()
            # log.debug("poc.get_grouplist(): %s" % str(grouplist))
            self.__group_list = list(grouplist) if isinstance(grouplist, tuple) and grouplist else []
        else:
            self.__group_list = []
        return self.__group_list

    def members(self, event=None, msg=None):
        self.__members = []
        group_id = msg if msg else self.__group_id
        if self.__state == 2 and group_id is not None:
            if msg is not None:
                memberlist = poc.get_memberlist(0)
            else:
                memberlist = poc.get_memberlist(group_id)
            self.__members = list(memberlist) if isinstance(memberlist, tuple) and memberlist else []
        return self.__members

    def weather(self, event=None, msg=None):
        if poc.get_loginstate() and utime.mktime(utime.localtime()) > self.__weather_refresh:
            data = poc.request_weather_info()
            if isinstance(data, tuple) and data:
                self.__weather_data["city"] = data[0]
                self.__weather_data["weathers"] = data[1:]
                self.__weather_refresh = utime.mktime(utime.localtime()) + 2 * 60 * 60
        return self.__weather_data

    def joingroup(self, event=None, msg=None):
        res = -1
        group_id = msg
        if self.__state == 2 and group_id is not None:
            res = poc.joingroup(group_id)
        return res

    def noise_reduction(self, tag):
        if tag == 1:
            # Enable noice reduction
            self.__nr_onoff_gpio.write(0)
            publish("io_u57_set", (12, 1))
        """
        else:
            # Disable noice reduction
            self.__nr_onoff_gpio.write(1)
            publish("io_u57_set", (12, 0))
        # log.debug("self.__nr_onoff_gpio.read(): %s" % self.__nr_onoff_gpio.read())
        """

    def speak(self, event=None, msg=None):
        res = -1
        if self.__state == 2 and msg is not None and self.__allow_break:
            publish("speak_notify", 0)
            if not msg:
                self.__call_usr = None
                res = poc.speak(msg)
            self.noise_reduction(msg)
            if msg:
                res = poc.speak(msg)
            if self.__allow_break and msg:
                self.__speak_tag = SPEAK_MODE.SEND_CALL
            else:
                self.__speak_tag = msg
            print("speak {}".format(self.__speak_tag))
            if msg:
                publish("ptt_led", 1)
                self.push_state_info(msg=1, speak_tag=4)
                if msg == 1:
                    self.__call_timer.start(50 * 1000, 0,
                                            self.call_timer_callback)
                publish("single_call_notify", msg)
            else:
                publish("ptt_led", 0)
                self.__call_timer.stop()
                publish("push_state_info")
                publish("single_call_notify", msg)
        return res

    def call_timer_callback(self, *args):
        self.speak(msg=0)

    def __callusr_callback(self, args):
        log.debug("__callusr_callback args %s" % str(args))

    def calluser(self, event=None, msg=None):
        res = -1
        usr_id = msg
        if msg:
            usr_id = msg[0]
            self.__call_user_info = msg
        if self.__state == 2 and usr_id is not None:
            res = poc.calluser(usr_id, self.__callusr_callback)
            log.debug("poc.calluser usr_id %s res %s" % (usr_id, res))
            if res == 0:
                self.__call_usr = usr_id
        return res

    def record_onoff(self, event=None, msg=None):
        onoff = msg
        if onoff in (0, 1):
            try:
                poc.record_onoff(onoff)
                self.__record_state = onoff
            except Exception as e:
                sys.print_exception(e)
                log.error(str(e))

    def query_records(self, event=None, msg=None):
        records = ()
        try:
            records = poc.record_get_file_list(msg)
            if not isinstance(records, tuple):
                records = ()
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))
        return records

    def play_record(self, event=None, msg=None):
        try:
            poc.record_play(msg)
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))

    def delete_record(self, event=None, msg=None):
        if "sd" in uos.listdir("/"):
            try:
                uos.remove("/sd/" + msg)
                return True
            except Exception as e:
                sys.print_exception(e)
                log.error(str(e))
        return False

    def stop_play_record(self, event=None, msg=None):
        try:
            poc.record_stop_play()
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))

    def __tts_play_callback(self, args):
        log.deug("POC TTS play args id: %s, status: %s" % args)

    def tts_play(self, event=None, msg=None):
        try:
            if not publish("get_speak_state"):
                if self.__tts_ready == 1 and hasattr(poc, "tts_play"):
                    poc.tts_play(msg)
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))

    def tts_ready(self, event=None, msg=None):
        self.__tts_ready = 1

    def __volume_init(self):
        try:
            poc.set_vol(2, publish("config_get", "vol"))
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))

    def get_volume(self, event=None, msg=None):
        try:
            vol = poc.get_vol(2)
            self.vol = self.no_vol_map.get(vol, None)
            return self.vol
        except Exception as e:
            sys.print_exception(e)
            log.error(str(e))
        return -1

    def audio_volume_get(self, event=None, msg=None):
        return self.vol if self.vol is not None else self.get_volume()

    def set_volume(self, event=None, msg=None):
        if 8 >= msg >= 0:
            if msg:
                self.last_volume = msg
            msg = self.vol_no_map[msg]
            poc.set_vol(2, msg)
            self.vol = msg
        publish("show_volume_img", msg)
        return self.vol

    def store_vol(self, event=None, msg=None):
        publish("config_store", {"vol": msg})

    def add_volume(self, event=None, msg=None):
        _vol = self.get_volume() + 1
        self.set_volume(msg=_vol)
        return self.audio_volume_get()

    def reduce_volume(self, event=None, msg=None):
        _vol = self.get_volume() - 1
        self.set_volume(msg=_vol)
        return self.audio_volume_get()

    def poc_switch_voice(self, event=None, msg=None):
        if self.get_volume() > 0:
            self.set_volume(msg=0)
            publish("push_store_vol")
        else:
            self.set_volume(msg=self.last_volume)
            publish("push_store_vol")

    def loc_map(self, event=None, msg=None):
        res = -1
        try:
            if hasattr(poc, "get_map"):
                lng, lat, length, width = msg
                # print("开始定位...")
                res = poc.get_map(lng, lat, length, width)
                # print("定位OK...{}", res)
        except Exception as e:
            sys.print_exception(e)
        return res
