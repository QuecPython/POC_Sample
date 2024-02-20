# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file      :hkt66.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2023-01-04 10:27:52
@copyright :Copyright (c) 2022
"""

import utime
import _thread
import usys as sys
from queue import Queue
from usr.common import create_thread,LogAdapter

log = LogAdapter(__name__)


class HKT66:

    def __init__(self, aw9523, wk2114, timeout=1000):
        self.__aw9523_u57 = aw9523
        self.__uart = wk2114
        self.__uart.set_callback(1, self.__uart_callback)
        self.__uart.slave_uart_init(1, 9600)
        self.__uart.slave_uart_disable(1)
        self.__send_header = bytearray([0x01, 0xE0, 0xFC])
        self.__recive_header = bytearray([0x04, 0x0E])
        self.__timeout = timeout
        self.__rxt_queue = Queue()
        self.__resp_lock = _thread.allocate_lock()
        self.__thread_id = None
        self.__data = b""
        self.__resps = []
        self.__callback = print
        self.__conn_flag = 0
        self.__conn_state = 0x04

    def __uart_callback(self, data):
        self.__rxt_queue.put(1)

    def __write(self, cmd):
        data = self.__send_header + bytearray([len(cmd)]) + cmd
        log.debug("__write data: %s" % data)
        return True if self.__uart.write(1, data) == len(data) else False

    def __read(self):
        return self.__uart.read(1, self.__uart.any(1))

    def __resp(self, num):
        with self.__resp_lock:
            resp = self.__data[:num]
            self.__data = self.__data[num:]
            return resp

    def __response(self, cmd, ack_code=None, timeout=None, ack_cmd=True):
        res = -1
        _ms = 100
        over_count = int(timeout / _ms) if timeout else (self.__timeout / _ms)
        count = 0
        while count <= over_count:
            if self.__resps and res == -1:
                log.debug("self.__resps[0]: %s, cmd: %s" % (self.__resps[0], cmd))
                if cmd == 0xDB:
                    if self.__resps[0][3] in (0x03, 0x04):
                        res = self.__resps[0][3]
                        self.__resps.pop(0)
                        break
                if self.__resps[0][3] == cmd:
                    self.__resps.pop(0)
                    res = 1
            if ack_cmd is False:
                if res == 1:
                    break
            else:
                if self.__resps and res == 1:
                    if len(self.__resps[0]) >= 4:
                        res = self.__resps[0][3]
                        if res == ack_code:
                            self.__resps.pop(0)
                            break
            utime.sleep_ms(_ms)
            count += 1
            if self.__resps:
                self.__resps.pop(0)
        return res

    def __recive_data(self):
        while True:
            tag = self.__rxt_queue.get()
            if tag:
                with self.__resp_lock:
                    _new_data = self.__read()
                    if not self.__data:
                        if not _new_data.startswith(bytes(self.__send_header)) and not _new_data.startswith(bytes(self.__recive_header)):
                            if _new_data.find(bytes(self.__send_header)) != -1:
                                _new_data = _new_data[_new_data.find(bytes(self.__send_header)):]
                            elif _new_data.find(bytes(self.__recive_header)) != -1:
                                _new_data = _new_data[_new_data.find(bytes(self.__recive_header)):]
                    else:
                        if _new_data.startswith(bytes(self.__send_header)) or _new_data.startswith(bytes(self.__recive_header)):
                            self.__data = b""
                    self.__data += _new_data
                log.debug("self.__data: %s" % self.__data)
                while self.__data.startswith(bytes(self.__send_header)):
                    cmd_len = 0
                    slave_data = b""
                    if len(self.__data) >= 4:
                        cmd_len = self.__data[3]
                    if len(self.__data) >= (4 + cmd_len):
                        slave_data = self.__resp(4 + cmd_len)
                    if len(slave_data) == 4 + cmd_len:
                        if slave_data[4] == 0xD1:
                            self.__callback((0xD1, slave_data[5]))
                        elif slave_data[4] == 0xD2:
                            self.__callback((0xD2, None))
                        elif slave_data[4] == 0xD3:
                            self.__callback((0xD3, None))
                        elif slave_data[4] == 0xD4:
                            self.__callback((0xD4, slave_data[5]))
                        elif slave_data[4] == 0xD6:
                            if len(slave_data) >= 18:
                                channel = slave_data[5]
                                receiving_frequency = slave_data[6:10]
                                sending_frequency = slave_data[10:14]
                                receving_ctc = slave_data[14:16]
                                sending_ctc = slave_data[16:18]
                            self.__callback((0xD6, (channel, receiving_frequency, sending_frequency, receving_ctc, sending_ctc)))
                        elif slave_data[4] == 0xD7:
                            self.__callback((0xD7, slave_data[5]))
                        elif slave_data[4] == 0xD8:
                            self.__callback((0xD8, slave_data[5:]))
                        elif slave_data[4] == 0xD9:
                            self.__callback((0xD9, None))
                        elif slave_data[4] == 0xD8:
                            self.__callback((0xD8, slave_data[5:]))
                        elif slave_data[4] == 0xC0:
                            self.__callback((0xC0, None))
                        elif slave_data[4] == 0xC2:
                            self.__callback((0xC2, None))
                        elif slave_data[4] == 0xC3:
                            self.__callback((0xC3, None))
                        elif slave_data[4] == 0xC4:
                            self.__callback((0xC4, None))
                        elif slave_data[4] == 0xC5:
                            self.__callback((0xC5, None))
                while self.__data.startswith(bytes(self.__recive_header)):
                    cmd_len = 0
                    resp_data = b""
                    if len(self.__data) >= 3:
                        cmd_len = self.__data[2]
                    if len(self.__data) >= (3 + cmd_len):
                        resp_data = self.__resp(3 + cmd_len)
                    if len(resp_data) == 3 + cmd_len:
                        if len(resp_data) == 4 and resp_data[3] >= 0x01 and resp_data[3] <= 0x04:
                            if resp_data[3] in (0x03, 0x04):
                                self.__conn_state = resp_data[3]
                            if self.__conn_flag == 1 and resp_data[3] in (0x03, 0x04):
                                self.__resps.append(resp_data)
                            else:
                                self.__callback((resp_data[3], None))
                        else:
                            self.__resps.append(resp_data)

    def set_callback(self, callback):
        if callable(callback):
            self.__callback = callback
            return 0
        return -1

    @property
    def state(self):
        return self.__aw9523_u57.read(13)

    def enable(self):
        self.__aw9523_u57.pin(13, mode=0, value=1)
        return self.__uart.slave_uart_enable(1)

    def disable(self):
        self.__aw9523_u57.pin(13, mode=0, value=0)
        return self.__uart.slave_uart_disable(1)

    def running(self):
        if self.__thread_id is None:
            self.__thread_id = create_thread(self.__recive_data)

    def stop(self):
        if self.__thread_id:
            try:
                _thread.stop_thread(self.__thread_id)
            except Exception as e:
                sys.print_exception(e)
                log.error(str(e))
            finally:
                self.__thread_id = None

    def change_mode(self):
        res = -1
        cmd = bytearray([0xDB])
        self.__conn_flag = 1
        if self.__write(cmd):
            log.debug("change_mode self.__write success.")
            res = self.__response(cmd[0], ack_code=None, timeout=1000)
        self.__conn_flag = 0
        return res

    def search_match(self):
        res = -1
        cmd = bytearray([0xDD])
        self.__conn_flag = 1
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_code=3, timeout=15 * 1000)
        self.__conn_flag = 0
        return res

    def disconnect(self):
        res = -1
        cmd = bytearray([0xDC])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_code=4)
        return res

    def voice_connect(self):
        # BT audio in connected
        self.__aw9523_u57.pin(1, mode=0, value=1)
        self.__aw9523_u57.pin(4, mode=0, value=0)
        # BT audio out connected
        self.__aw9523_u57.pin(0, mode=0, value=1)
        self.__aw9523_u57.pin(5, mode=0, value=0)
        res = -1
        cmd = bytearray([0xDE])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_code=5)
        return res

    def voice_disconnect(self):
        res = -1
        cmd = bytearray([0xDF])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_code=6)
        return res

    def mic_gain(self, val):
        res = -1
        if not isinstance(val, int):
            return res
        if isinstance(val, int) and (val < 0 or val > 95):
            return res
        cmd = bytearray([0xE0, int(val)])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_cmd=False)
        return res

    def spk_gain(self, val):
        res = -1
        if not isinstance(val, int):
            return res
        if isinstance(val, int) and (val < 0 or val > 15):
            return res
        cmd = bytearray([0xE1, int(val)])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_cmd=False)
        return res

    def mute_mic(self):
        res = -1
        cmd = bytearray([0xE2])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_cmd=False)
        return res

    def mute_spk(self, mute=2):
        res = -1
        cmd = bytearray([0xE3, mute])
        if self.__write(cmd):
            res = self.__response(cmd[0], ack_cmd=False)
        return res

    def get_mac_bt_name(self):
        mac = b""
        bt_name = b""
        cmd = bytearray([0xE4])
        if self.__write(cmd):
            count = 0
            data_len = 0
            while count < 20:
                if len(self.__data) >= 3 and data_len == 0:
                    data_len = self.__data[2]
                if data_len > 0 and len(self.__data) >= (3 + data_len):
                    resp = self.__resp(3 + data_len)
                    mac = resp[3:9]
                    bt_name = resp[9:]
                utime.sleep_ms(50)
                count += 1
        if mac:
            mac = "-".join(["{:02X}"] * 6).format(*list(mac))
        if bt_name:
            bt_name = bt_name.decode()
        return (mac, bt_name)
