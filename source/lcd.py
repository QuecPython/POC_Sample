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
@file      :lcd.py
@author    :Jack Sun (jack.sun@quectel.com)
@brief     :<description>
@version   :1.0.0
@date      :2023-05-19 14:29:21
@copyright :Copyright (c) 2022
"""

from machine import LCD, Pin

LCDST7701_DATA = (
    0x11, 120, 0,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x10,
    0xC0, 0, 2, 0x63, 0x00,
    0xC1, 0, 2, 0x11, 0x02,
    0xC2, 0, 2, 0x31, 0x08,
    0xCC, 0, 1, 0x10,
    0xB0, 0, 16, 0x40, 0x01, 0x46, 0x0D, 0x13, 0x09, 0x05, 0x09, 0x09, 0x1B, 0x07, 0x15, 0x12, 0x4C, 0x10, 0xC8,
    0xB1, 0, 16, 0x40, 0x02, 0x86, 0x0D, 0x13, 0x09, 0x05, 0x09, 0x09, 0x1F, 0x07, 0x15, 0x12, 0x15, 0x19, 0x08,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x11,
    0xB0, 0, 1, 0x50,
    0xB1, 0, 1, 0x68,
    0xB2, 0, 1, 0x07,
    0xB3, 0, 1, 0x80,
    0xB5, 0, 1, 0x47,
    0xB7, 0, 1, 0x85,
    0xB8, 0, 1, 0x21,
    0xB9, 0, 1, 0x10,
    0xC1, 0, 1, 0x78,
    0xC2, 0, 1, 0x78,
    0xD0, 100, 1, 0x88,
    0xE0, 0, 3, 0x00, 0x00, 0x02,
    0xE1, 0, 11, 0x08, 0x00, 0x0A, 0x00, 0x07, 0x00, 0x09, 0x00, 0x00, 0x33, 0x33,
    0xE2, 0, 13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xE3, 0, 4, 0x00, 0x00, 0x33, 0x33,
    0xE4, 0, 2, 0x44, 0x44,
    0xE5, 0, 16, 0x0E, 0x2D, 0xA0, 0xA0, 0x10, 0x2D, 0xA0, 0xA0, 0x0A, 0x2D, 0xA0, 0xA0, 0x0C, 0x2D, 0xA0, 0xA0,
    0xE6, 0, 4, 0x00, 0x00, 0x33, 0x33,
    0xE7, 0, 2, 0x44, 0x44,
    0xE8, 0, 16, 0x0D, 0x2D, 0xA0, 0xA0, 0x0F, 0x2D, 0xA0, 0xA0, 0x09, 0x2D, 0xA0, 0xA0, 0x0B, 0x2D, 0xA0, 0xA0,
    0xEB, 0, 7, 0x02, 0x01, 0xE4, 0xE4, 0x44, 0x00, 0x40,
    0xEC, 0, 2, 0x02, 0x01,
    0xED, 0, 16, 0xAB, 0x89, 0x76, 0x54, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x10, 0x45, 0x67, 0x98, 0xBA,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x00,
    0x29, 0, 0,
)

LCDST7701S_DATA = (
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x13,
    0xEF, 0, 1, 0x08,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x10,
    0xC0, 0, 2, 0x63, 0x00,
    0xC1, 0, 2, 0x0A, 0x02,
    0xC2, 0, 2, 0x01, 0x07,
    0xCC, 0, 1, 0x18,
    0xB0, 0, 16, 0x05, 0x10, 0x16, 0x0D, 0x10, 0x06, 0x07, 0x08, 0x08, 0x25, 0x06, 0x13, 0x11, 0x29, 0x31, 0x18,
    0xB1, 0, 16, 0x05, 0x0F, 0x16, 0x0D, 0x10, 0x06, 0x07, 0x09, 0x08, 0x25, 0x05, 0x14, 0x12, 0x29, 0x30, 0x18,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x11,
    0xB0, 0, 1, 0x5D,
    0xB1, 0, 1, 0x40,
    0xB2, 0, 1, 0x82,
    0xB3, 0, 1, 0x80,
    0xB5, 0, 1, 0x45,
    0xB7, 0, 1, 0x85,
    0xB8, 0, 1, 0x21,
    0xB9, 0, 2, 0x10, 0x1F,
    0xBB, 0, 1, 0x03,
    0xBC, 0, 1, 0x3E,
    0xC1, 0, 1, 0x78,
    0xC2, 0, 1, 0x78,
    0xD0, 100, 1, 0x88,
    0xE0, 0, 3, 0x00, 0x00, 0x02,
    0xE1, 0, 11, 0x04, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0x20, 0x20,
    0xE2, 0, 12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xE3, 0, 4, 0x00, 0x00, 0x33, 0x00,
    0xE4, 0, 2, 0x22, 0x00,
    0xE5, 0, 16, 0x04, 0x34, 0x9A, 0xA0, 0x06, 0x34, 0x9A, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xE6, 0, 4, 0x00, 0x00, 0x33, 0x00,
    0xE7, 0, 2, 0x22, 0x00,
    0xE8, 0, 16, 0x05, 0x34, 0x9A, 0xA0, 0x07, 0x34, 0x9A, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0xEB, 0, 7, 0x02, 0x00, 0x40, 0x40, 0x00, 0x00, 0x00,
    0xEC, 0, 2, 0x00, 0x00,
    0xED, 0, 16, 0xFA, 0x45, 0x0B, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xB0, 0x54, 0xAF,
    0xEF, 0, 6, 0x08, 0x08, 0x08, 0x45, 0x3F, 0x54,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x13,
    0xE8, 0, 2, 0x00, 0x0E,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x00,
    0x11, 120, 0,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x13,
    0xE8, 10, 2, 0x00, 0x0C,
    0xE8, 0, 2, 0x00, 0x00,
    0xFF, 0, 5, 0x77, 0x01, 0x00, 0x00, 0x00,
    0x29, 20, 0,
)


class LCDBase:

    def __init__(self, gpion, init_data, width=480, hight=800, DataLane=2, VBP=17, VFP=6):
        self.enable_gpio = Pin(gpion, Pin.OUT, Pin.PULL_PU, 1)
        self.lcd = LCD()
        self.lcd.mipi_init(initbuf=bytearray(init_data), width=width, hight=hight, DataLane=DataLane, VBP=VBP, VFP=VFP)
        self.lcd.lcd_clear(0xFFFF)

    def onoff(self, val=1):
        return True if self.enable_gpio.write(val) == 0 else False

    def state(self):
        return self.enable_gpio.read()

    def show(self, filename, start_x=200, start_y=323):
        self.lcd.lcd_show(filename, start_x, start_y)


class LCDST7701(LCDBase):
    # ST7701_480*800 LCD屏幕初始化
    def __init__(self):
        super().__init__(Pin.GPIO32, LCDST7701_DATA)


class LCDST7701S(LCDBase):

    def __init__(self):
        super().__init__(Pin.GPIO14, LCDST7701S_DATA)


from usr.settings import MEDIA_DIR
import lvgl as lv
import utime

LCD_SCREEN = LCDST7701S()


def lv_init():
    lv.init()
    # Register SDL display driver.
    disp_buf1 = lv.disp_draw_buf_t()
    buf1_1 = bytearray(480 * 800 * 2)
    disp_buf1.init(buf1_1, None, len(buf1_1))
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf1
    disp_drv.flush_cb = LCD_SCREEN.lcd.lcd_write
    disp_drv.hor_res = 480
    disp_drv.ver_res = 800
    disp_drv.sw_rotate = 1  # 因为横屏，所以需要旋转
    disp_drv.rotated = lv.DISP_ROT._90  # 旋转角度
    disp_drv.register()

    lv.tick_inc(5)
    global logo_img, logo_obj
    logo_obj = lv.obj()
    logo_obj.set_style_bg_color(lv.color_make(0xff, 0xff, 0xff), 0)
    logo_img = lv.img(logo_obj)
    logo_img.set_pos(250, 150)
    logo_img.set_size(297, 105)
    logo_img.set_src(MEDIA_DIR + 'tyt_logo.jpg')
    lv.task_handler()
    lv.scr_load(logo_obj)
    utime.sleep_ms(20)


lv_init()
