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

# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file      :running.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2023-02-01 10:40:03
@copyright :Copyright (c) 2022
"""
from usr.lcd import *
import pm
import misc
import utime
import WK2114
import usys as sys
from machine import Pin, UART, I2C
from usr.EventMesh import subscribe
from usr.common import Abstract
from usr.mgr import BatteryManager, MapManager, ConfigStoreManager, DeviceInfoManager, NetManager, BluetoothManager, \
    PocManager, HandMicManager, AW9523Manager, LedManager


class App(object):
    def __init__(self):
        self.managers = []

    def append_manager(self, manager):
        if isinstance(manager, Abstract):
            manager.post_processor_after_instantiation()
            self.managers.append(manager)
        return self

    def start(self):
        for manager in self.managers:
            manager.post_processor_before_initialization()
            manager.initialization()
            manager.post_processor_after_initialization()


class PocApp(App):
    def __init__(self):
        super(PocApp, self).__init__()
        self.__ui = None
        self.__finish = False
        subscribe("poc_app_finish", self.get_state)

    def get_state(self, event, msg):
        return self.__finish

    def set_ui(self, ui):
        self.__ui = ui

    def start(self):
        if self.__ui is not None:
            self.__ui.start()
        super().start()
        if self.__ui is not None:
            self.__ui.finish()
        self.__finish = True


def net_light_check():
    if hasattr(misc, "net_light"):
        try:
            if misc.net_light() != 0:
                misc.net_light(0)
                return 0
        except Exception as e:
            sys.print_exception(e)
    return 1


def time_sync_check():
    if hasattr(utime, "nitzSwitch"):
        try:
            if utime.nitzSwitch() != 0:
                utime.nitzSwitch(0)
                return 0
        except Exception as e:
            sys.print_exception(e)
    return 1


res1 = net_light_check()
res2 = time_sync_check()
if 0 in (res1, res2):
    misc.Power.powerRestart()
utime.setTimeZone(0)

config = ConfigStoreManager()
config.post_processor_after_instantiation()

from usr.at_cmd import *

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
r.add_order_cmd(AT11)
r.add_order_cmd(AT13)
r.add_order_cmd(AT17)
r.add_order_cmd(AT18)
r.add_order_cmd(AT19)
r.add_order_cmd(AT20)
um = UartManager()
um.set_resolver(r)
um.start()
# UartManager.start()

# Must first init poc, because poc will reset some gpio.
poc_manager = PocManager(noise_reduction_gpion=Pin.GPIO46)
poc_manager.poc_init()
aw9523 = AW9523Manager(Pin.GPIO17, Pin.GPIO43, I2C.I2C1)
wk2114 = WK2114(Pin.GPIO39, Pin.GPIO40, Pin.GPIO37, UART.UART2, 115200, 8, 0, 1)

battery = BatteryManager()
locmap = MapManager(wk2114)
device_info = DeviceInfoManager(horn_gpion=Pin.GPIO3)
net_manager = NetManager()
bluetooth = BluetoothManager(aw9523.u57, wk2114)
hand_mic = HandMicManager()
led_mgr = LedManager()
led_mgr.post_processor_after_instantiation()
publish("reset_led_timer", 1)
from usr.ui import Poc_Ui, MenuScreen, TBKScreen, GroupScreen, MemberScreen, HistoryScreen, LocationScreen, \
    WeatherScreen, \
    SettingScreen, SettingVolScreen, SettingSimScreen, SettingScreenTimeScreen, SettingCallTimeScreen, SettingSysScreen, \
    SettingBluetoothScreen, PopUpMsgBox, SettingHotKeyScreen, SettingLanguageScreen, FriendScreen, \
    SettingRecoveryScreen, SettingCallLevelScreen, SettingNoiseScreen, GPSInfoScreen, SingleCallScreen, \
    OTAWriteNumScreen, VolMsgBox, SOSScreen, HistoryDirScreen

poc_ui = Poc_Ui(LCD_SCREEN)
poc_ui.add_screen(MenuScreen()) \
    .add_screen(TBKScreen()) \
    .add_screen(FriendScreen()) \
    .add_screen(GroupScreen()) \
    .add_screen(MemberScreen()) \
    .add_screen(HistoryScreen()) \
    .add_screen(LocationScreen()) \
    .add_screen(WeatherScreen()) \
    .add_screen(SettingScreen()) \
    .add_screen(SettingVolScreen()) \
    .add_screen(SettingSimScreen()) \
    .add_screen(SettingScreenTimeScreen()) \
    .add_screen(SettingCallTimeScreen()) \
    .add_screen(SettingSysScreen()) \
    .add_screen(SettingBluetoothScreen()) \
    .add_screen(SettingHotKeyScreen()) \
    .add_screen(SettingLanguageScreen()) \
    .add_screen(SettingRecoveryScreen()) \
    .add_screen(SettingCallLevelScreen()) \
    .add_screen(SettingNoiseScreen()) \
    .add_screen(GPSInfoScreen()) \
    .add_screen(SingleCallScreen()) \
    .add_screen(OTAWriteNumScreen()) \
    .add_screen(SOSScreen()) \
    .add_screen(HistoryDirScreen())


poc_ui.add_msg_box(PopUpMsgBox())
poc_ui.add_msg_box(VolMsgBox())
poc_app = PocApp()
poc_app.append_manager(config)
poc_app.append_manager(led_mgr)
poc_app.append_manager(battery)
poc_app.append_manager(aw9523)
poc_app.append_manager(bluetooth)
poc_app.append_manager(locmap)
poc_app.append_manager(device_info)
poc_app.append_manager(net_manager)
poc_app.append_manager(poc_manager)
poc_app.append_manager(hand_mic)
poc_app.set_ui(poc_ui)

poc_app.start()
pm.autosleep(0)
publish("check_net")
