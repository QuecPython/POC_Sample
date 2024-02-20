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
@file      :settings.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2023-05-11 14:49:28
@copyright :Copyright (c) 2022
"""

PROJECT_NAME = "QuecPython_Car_Intercom"
PROJECT_VERSION = "v1.0.1"

MEDIA_DIR = "U:/media/"

CONFIG = {
    # Settings config.
    "product_name": "TP68U",
    "battery_performance_level": 0,
    "single_call_time": 30,
    "lock_screen_time": -1,
    "sim_card_no": 1,
    "ptt_voice_enable": 1,
    "btn_voice_enable": 0,
    "bluetooth_onoff": 0,
    "language": "CN",
    "noise_onoff": 0,
    "call_level_no": 3,
    "vol": 10,
    "hot_key": {
        "0": {"uid": -1, "gid": -1},
        "1": {"uid": -1, "gid": -1},
        "2": {"uid": -1, "gid": -1},
        "3": {"uid": -1, "gid": -1},
        "4": {"uid": -1, "gid": -1},
        "5": {"uid": -1, "gid": -1},
        "6": {"uid": -1, "gid": -1},
        "7": {"uid": -1, "gid": -1},
        "8": {"uid": -1, "gid": -1},
        "9": {"uid": -1, "gid": -1},
    }
}

SETTING = {
    "apn_id": "",
    "apn_pwd": "",
    "poc_ip": "",
    "poc_username": "",
    "poc_password": "",
    "gps_enable": 0,
    "offline_voice_enable": 0,
    "single_call_enable": 1,
    "apn_name": "",
    "iccid_enable": 0,
    "gps_ip": "",
    "gps_port": "",
    "iccid": "",
    "admin_pwd": "27770875",
    "user_pwd": "",
}

NEW_CONFIG = {

}


def get_config():
    NEW_CONFIG.update(CONFIG)
    NEW_CONFIG.update(SETTING)
    return NEW_CONFIG
