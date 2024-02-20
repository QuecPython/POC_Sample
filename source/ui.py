import lvgl as lv
import gc
import pm
import uos
import fota
import modem
import utime
import osTimer
import _thread
import usys as sys
from misc import Power
from queue import Queue
from usr.settings import MEDIA_DIR
from usr.common import LogAdapter, Abstract, create_thread, OSTIMER
from usr.EventMesh import subscribe, publish, publish_async
from usr.language import PROFILE as LANG_PROFILE

# LCD_SCREEN = LCDST7701()
import EventMesh

WIDTH = 800
HEIGHT = 480


def lv_style_t(radius=None, bg_color=None, bg_grad_color=None, bg_grad_dir=None, bg_opa=None, border_width=None,
               border_opa=None, pad_left=None, pad_right=None, pad_top=None, pad_bottom=None, img_recolor=None,
               img_recolor_opa=None, img_opa=None, line_color=None, line_width=None, line_rounded=None,
               shadow_color=None, shadow_opa=None, border_color=None, anim_speed=None, text_color=None, text_font=None,
               text_letter_space=None):
    _style = lv.style_t()
    _style.init()
    if radius is not None:
        _style.set_radius(radius)
    if bg_color is not None:
        _style.set_bg_color(bg_color)
    if bg_grad_color is not None:
        _style.set_bg_grad_color(bg_grad_color)
    if bg_grad_dir is not None:
        _style.set_bg_grad_dir(bg_grad_dir)
    if bg_opa is not None:
        _style.set_bg_opa(bg_opa)
    if border_width is not None:
        _style.set_border_width(border_width)
    if border_opa is not None:
        _style.set_border_opa(border_opa)
    if pad_left is not None:
        _style.set_pad_left(pad_left)
    if pad_right is not None:
        _style.set_pad_right(pad_right)
    if pad_top is not None:
        _style.set_pad_top(pad_top)
    if pad_bottom is not None:
        _style.set_pad_bottom(pad_bottom)
    if img_recolor is not None:
        _style.set_img_recolor(img_recolor)
    if img_recolor_opa is not None:
        _style.set_img_recolor_opa(img_recolor_opa)
    if img_opa is not None:
        _style.set_img_opa(img_opa)
    if line_color is not None:
        _style.set_line_color(line_color)
    if line_width is not None:
        _style.set_line_width(line_width)
    if line_rounded is not None:
        _style.set_line_rounded(line_rounded)
    if shadow_color is not None:
        _style.set_shadow_color(shadow_color)
    if shadow_opa is not None:
        _style.set_shadow_opa(shadow_opa)
    if border_color is not None:
        _style.set_border_color(border_color)
    if anim_speed is not None:
        _style.set_anim_speed(anim_speed)
    if text_color is not None:
        _style.set_text_color(text_color)
    if text_font is not None:
        _style.set_text_font(text_font)
    if text_letter_space is not None:
        _style.set_text_letter_space(text_letter_space)
    return _style


def lv_obj(parent=None, pos=None, size=None, style=None, add_flag=None, clear_flag=None,
           style_bg_opa=None, style_border_width=None, style_border_color=None):
    _obj = lv.obj() if parent is None else lv.obj(parent)
    if pos is not None:
        _obj.set_pos(*pos)
    if size is not None:
        _obj.set_size(*size)
    if style is not None:
        for i in style:
            _obj.add_style(*i)
    if add_flag is not None:
        _obj.add_flag(add_flag)
    if clear_flag is not None:
        _obj.clear_flag(clear_flag)
    if style_bg_opa is not None:
        _obj.set_style_bg_opa(*style_bg_opa)
    if style_border_width is not None:
        _obj.set_style_border_width(*style_border_width)
    if style_border_color is not None:
        _obj.set_style_border_color(*style_border_color)
    return _obj


def lv_label(parent=None, pos=None, size=None, text=None, long_mode=None, style_text_align=None, style=None):
    _label = lv.label() if parent is None else lv.label(parent)
    if pos is not None:
        _label.set_pos(*pos)
    if size is not None:
        _label.set_size(*size)
    if text is not None:
        _label.set_text(text)
    if long_mode is not None:
        _label.set_long_mode(long_mode)
    if style_text_align is not None:
        _label.set_style_text_align(*style_text_align)
    if style is not None:
        for i in style:
            _label.add_style(*i)
    return _label


def lv_img(parent=None, pos=None, size=None, src=None, style=None, zoom=None):
    _img = lv.img() if parent is None else lv.img(parent)
    if pos is not None:
        _img.set_pos(*pos)
    if size is not None:
        _img.set_size(*size)
    if src is not None:
        _img.set_src(src)
    if zoom is not None:
        _img.set_zoom(zoom)
    if style is not None:
        for i in style:
            _img.add_style(*i)
    return _img


def lv_list(parent=None, pos=None, size=None, style_pad_left=None, style_pad_top=None, style_pad_row=None, style=None):
    _list = lv.list() if parent is None else lv.list(parent)
    if pos is not None:
        _list.set_pos(*pos)
    if size is not None:
        _list.set_size(*size)
    if style_pad_left is not None:
        _list.set_style_pad_left(*style_pad_left)
    if style_pad_top is not None:
        _list.set_style_pad_top(*style_pad_top)
    if style_pad_row is not None:
        _list.set_style_pad_row(*style_pad_row)
    if style is not None:
        for i in style:
            _list.add_style(*i)
    return _list


def lv_btn(parent=None, pos=None, size=None, style=None):
    _btn = lv.btn() if parent is None else lv.btn(parent)
    if pos is not None:
        _btn.set_pos(*pos)
    if size is not None:
        _btn.set_size(*size)
    if style is not None:
        for i in style:
            _btn.add_style(*i)
    return _btn


def lv_line(parent=None, pos=None, size=None, points=None, style=None):
    _line = lv.line() if parent is None else lv.line(parent)
    if pos is not None:
        _line.set_pos(*pos)
    if size is not None:
        _line.set_size(*size)
    if points is not None:
        _line.set_points(*points)
    if style is not None:
        for i in style:
            _line.add_style(*i)
    return _line


screen_style = lv_style_t(bg_color=lv.color_make(0xff, 0xff, 0xff), bg_opa=255)
# 页眉容器样式
style_header = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x00, 0x00, 0x00),
    bg_grad_color=lv.color_make(0x00, 0x00, 0x00),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=255,
    border_width=0,
    border_opa=255,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0
)
# main页面 中间背景
main_cont_bg_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0xff, 0xff, 0xff),
    bg_grad_color=lv.color_make(0xff, 0xff, 0xff),
    # bg_grad_color=lv.color_make(0xeb, 0xea, 0xe6),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=255,
    border_width=0,
    border_opa=255,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# main页面 底部背景
main_bottom_bg_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x56, 0x9e, 0xeb),
    bg_grad_color=lv.color_make(0x56, 0x9e, 0xeb),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=255,
    border_width=0,
    border_opa=255,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# 45号黑色字体
black_45_font_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=0,
    text_color=lv.color_make(0x00, 0x00, 0x00),
    text_font=lv.font_30,
    text_letter_space=2,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# 30号白色字体
white_30_font_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=0,
    text_color=lv.color_make(0xff, 0xff, 0xff),
    text_font=lv.font_21,
    text_letter_space=2,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# 30号黑色字体
black_30_font_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=0,
    text_color=lv.color_make(0x00, 0x00, 0x00),
    text_font=lv.font_21,
    text_letter_space=2,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# 30号蓝色字体
blue_30_font_style = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_color=lv.color_make(0x21, 0x95, 0xf6),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=0,
    text_color=lv.color_make(0x2c, 0x96, 0xe8),
    text_font=lv.font_21,
    text_letter_space=2,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
)
# msgbox bgcolor
style_msgbox = lv.style_t()
style_msgbox.init()
style_msgbox.set_radius(5)  # (0xdc, 0x8f, 0x13))
style_msgbox.set_bg_color(lv.color_make(0xe6, 0x94, 0x10))
style_msgbox.set_bg_grad_color(lv.color_make(0xe6, 0x94, 0x10))
style_msgbox.set_bg_grad_dir(lv.GRAD_DIR.VER)
style_msgbox.set_border_width(0)
style_msgbox.set_bg_opa(255)

style_msgbox.set_pad_left(0)
style_msgbox.set_pad_right(0)
style_msgbox.set_pad_top(0)
style_msgbox.set_pad_bottom(0)
# 白
style_bg = lv_style_t(
    radius=0,
    img_recolor=lv.color_make(0xff, 0xff, 0xff),
    img_recolor_opa=0,
    img_opa=255,
)
# 天气页面分割线
weather_content_line_style = lv_style_t(
    line_color=lv.color_make(0xe5, 0xe1, 0xe1),
    line_width=2,
    line_rounded=255,
)
# btn 按钮样式
btn_style_blue = lv_style_t(
    radius=11,
    bg_color=lv.color_make(0xd7, 0xd4, 0xcb),
    bg_grad_color=lv.color_make(0x7f, 0x73, 0x66),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=255,
    shadow_color=lv.color_make(0xff, 0xff, 0xff),
    shadow_opa=255,
    border_color=lv.color_make(0xff, 0xff, 0xff),
    border_width=3,
    border_opa=205,
)
# 群组列表样式 黑色
style_group_black = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0xd1, 0xca, 0xb7),
    bg_grad_color=lv.color_make(0xd1, 0xca, 0xb7),
    anim_speed=10,
    bg_grad_dir=lv.GRAD_DIR.VER,
    border_width=0,
    bg_opa=255,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
    text_color=lv.color_make(0x00, 0x00, 0x00),
    text_font=lv.font_21,
)
style_group_black_1 = lv_style_t(
    radius=0,
    bg_color=lv.color_make(0xff, 0xff, 0xff),
    bg_grad_color=lv.color_make(0xff, 0xff, 0xff),
    anim_speed=10,
    bg_grad_dir=lv.GRAD_DIR.VER,
    border_width=0,
    bg_opa=255,
    pad_left=0,
    pad_right=0,
    pad_top=0,
    pad_bottom=0,
    text_color=lv.color_make(0x00, 0x00, 0x00),
    text_font=lv.font_21,
)
# list消除滚动条
style_list_scrollbar = lv_style_t(
    radius=3,
    bg_color=lv.color_make(0x00, 0x00, 0x00),
    bg_grad_color=lv.color_make(0x00, 0x00, 0x00),
    bg_grad_dir=lv.GRAD_DIR.VER,
    bg_opa=0,
)
# 群组label 样式
style_group_label_black = lv_style_t(anim_speed=20)

"""
===================================================Main 主页面 start=============================================================
"""
power_down_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
power_down_screen.set_style_bg_color(lv.color_make(0xff, 0xff, 0xff), 0)
main_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
# 顶端状态栏
main_cont_top = lv_obj(
    parent=main_screen,
    pos=(0, 0),
    size=(800, 50),
    style=[(style_header, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 顶端状态栏 运营商显示
main_top_net = lv_label(
    parent=main_cont_top,
    pos=(12, 8),
    size=(250, 32),
    text=("NULL"),
    long_mode=(lv.label.LONG.DOT),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(white_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
main_sim_img = lv_img(parent=main_cont_top, pos=(510, 5), size=(32, 32), src=(MEDIA_DIR + 'None.png'),
                      style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)], )
main_voice_img = lv_img(parent=main_cont_top, pos=(548, 5), size=(32, 32), src=(MEDIA_DIR + 'None.png'),
                        style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)], )
main_sd_img = lv_img(parent=main_cont_top, pos=(586, 5), size=(32, 32), src=(MEDIA_DIR + 'None.png'),
                     style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)], )

# 顶端状态栏 时间显示（主页面不显示）
main_top_time = lv_label(
    parent=main_cont_top,
    pos=(266, 8),
    size=(135, 32),
    text=(""),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(white_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 顶端状态栏 GPS图标显示
main_top_gps_img = lv_img(
    parent=main_cont_top,
    pos=(624, 4),
    size=(32, 32),
    src=(MEDIA_DIR + 'gps.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 顶端状态栏 蓝牙状态显示
main_top_bt_img = lv_img(
    parent=main_cont_top,
    pos=(662, 5),
    size=(25, 32),
    src=(MEDIA_DIR + 'None.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 顶端状态栏 信号强度显示
main_top_csq_img = lv_img(
    parent=main_cont_top,
    pos=(698, 10),
    size=(32, 25),
    src=(MEDIA_DIR + 'signal_5.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 顶端状态栏 电量显示
main_top_battery_img = lv_img(parent=main_cont_top, pos=(736, 0), size=(48, 48), src=(MEDIA_DIR + 'battery_4.png'),
                              style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)], )
# main 功能页面
main_content = lv_obj(
    parent=main_screen,
    pos=(0, 40),
    size=(800, 400),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 功能页面 左侧日期
main_date_screen_label = lv_label(parent=main_content, pos=(22, 103), text=("2022/12/15  星期四"),
                                  long_mode=(lv.label.LONG.WRAP), style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
                                  style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )
# main 功能页面 左侧时间
main_time_screen_label = lv_label(
    parent=main_content,
    pos=(70, 40),
    # size=(150, 50),
    text=("15:36"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_45_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 功能页面 右侧实时天气图片
main_weather_screen_img_2 = lv_img(
    parent=main_content,
    pos=(450, 40),
    size=(65, 65),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 功能页面 右侧地址信息
main_weather_screen_label_2 = lv_label(
    parent=main_content,
    pos=(550, 89),
    # size=(200, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 功能页面 右侧天气
main_weather_screen_label_3 = lv_label(
    parent=main_content,
    pos=(550, 43),
    # size=(300, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 底部content
main_bottom = lv_obj(
    parent=main_screen,
    pos=(0, 440),
    size=(800, 40),
    style=[(main_bottom_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 底部群组图标
main_bottom_img = lv_img(
    parent=main_bottom,
    pos=(3, 4),
    size=(32, 32),
    src=(MEDIA_DIR + 'main_group.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# main 底部当前所在群组显示（被呼和主动呼叫状态显示）
main_bottom_label = lv_label(
    parent=main_bottom,
    pos=(50, 4),
    # size=(500, 32),
    text=("[--] (--) --"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(white_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
"""
===================================================Main 主页面 end=============================================================
"""
# lv.scr_load(main_screen)
"""
===================================================TBK 对讲功能页面 start=============================================================
"""
tbk_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
# 对讲页面导航栏页面
tbk_app_bar_screen = lv_obj(
    parent=tbk_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
tbk_app_bar_img = lv_img(
    parent=tbk_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
tbk_app_bar_label = lv_label(
    parent=tbk_app_bar_screen,
    pos=(55, 18),
    # size=(120, 25),
    text=("对讲"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 对讲页面 内容展示
tbk_content_screen = lv_obj(
    parent=tbk_screen,
    pos=(0, 100),
    size=(800, 340),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 对讲页面 群组信息
tbk_content_group_img = lv_img(
    parent=tbk_content_screen,
    pos=(57, 90),
    size=(128, 128),
    src=(MEDIA_DIR + 'group_tbk.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
tbk_content_group_check_img = lv_obj(
    parent=tbk_content_screen,
    add_flag=(lv.obj.FLAG.HIDDEN),
    pos=(52, 85),
    size=(140, 140),
    style_bg_opa=(0, 0),
    style_border_width=(1, 0),
    style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0),
)
tbk_content_group_label = lv_label(
    parent=tbk_content_screen,
    pos=(60, 235),
    size=(128, 32),
    text=("群组"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 对讲页面 成员
tbk_content_member_img = lv_img(
    parent=tbk_content_screen,
    pos=(242, 83),
    size=(128, 128),
    src=(MEDIA_DIR + 'member_tbk.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
tbk_content_member_check_img = lv_obj(
    parent=tbk_content_screen,
    add_flag=(lv.obj.FLAG.HIDDEN),
    pos=(237, 85),
    size=(140, 140),
    style_bg_opa=(0, 0),
    style_border_width=(1, 0),
    style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0),
)
tbk_content_member_label = lv_label(
    parent=tbk_content_screen,
    pos=(245, 235),
    size=(128, 32),
    text=("成员"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 对讲机好友界面
tbk_content_friend_img = lv_img(parent=tbk_content_screen, pos=(427, 86), size=(128, 128),
                                src=(MEDIA_DIR + 'Friends.png'), style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)])
tbk_content_friend_check_img = lv_obj(parent=tbk_content_screen, add_flag=(lv.obj.FLAG.HIDDEN), pos=(422, 85),
                                      size=(140, 140), style_bg_opa=(0, 0), style_border_width=(1, 0),
                                      style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0), )
tbk_content_friend_label = lv_label(parent=tbk_content_screen, pos=(430, 235), size=(128, 32), text=("Friend"),
                                    long_mode=(lv.label.LONG.WRAP), style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
                                    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )

# 对讲页面 历史消息
tbk_content_history_img = lv_img(parent=tbk_content_screen, pos=(612, 86), size=(128, 128),
                                 src=(MEDIA_DIR + 'history.png'), style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)])
tbk_content_history_check_img = lv_obj(parent=tbk_content_screen, add_flag=(lv.obj.FLAG.HIDDEN), pos=(607, 85),
                                       size=(140, 140), style_bg_opa=(0, 0), style_border_width=(1, 0),
                                       style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0), )
tbk_content_history_label = lv_label(parent=tbk_content_screen, pos=(615, 235), size=(128, 32), text=("历史消息"),
                                     long_mode=(lv.label.LONG.WRAP), style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
                                     style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )
"""
===================================================TBK 对讲功能页面 end=============================================================
"""
single_call_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
single_call_app_bar_screen = lv_obj(
    parent=single_call_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
single_call_app_bar_img = lv_img(
    parent=single_call_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
single_call_app_bar_label = lv_label(
    parent=single_call_app_bar_screen,
    pos=(55, 18),
    # size=(120, 25),
    text=("单呼"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
single_call_content_member_img = lv_img(
    parent=single_call_screen,
    pos=(336, 136),
    size=(128, 128),
    src=(MEDIA_DIR + 'member_tbk.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
single_call_member_label = lv_label(
    parent=single_call_screen,
    pos=(0, 270),
    size=(800, 32),
    text=("成员"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
"""
===================================================历史SD卡文件夹 群组页面 start=============================================================
"""
history_dir_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 对讲页面导航栏页面
history_dir_bar = lv_obj(
    parent=history_dir_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
history_dir_bar_img = lv_img(
    parent=history_dir_bar,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
history_dir_bar_label = lv_label(
    parent=history_dir_bar,
    pos=(55, 18),
    # size=(120, 25),
    text=("历史文件"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 群组list
history_dir_list = lv_list(
    parent=history_dir_screen,
    pos=(0, 100),
    size=(800, 340),
    style_pad_left=(0, 0),
    style_pad_top=(0, 0),
    style_pad_row=(4, 0),
    style=[
        (style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
    ],
)
"""
===================================================Group 群组页面 start=============================================================
"""
group_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 对讲页面导航栏页面
group_app_bar_screen = lv_obj(
    parent=group_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
group_app_bar_img = lv_img(
    parent=group_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
group_app_bar_label = lv_label(
    parent=group_app_bar_screen,
    pos=(55, 18),
    # size=(120, 25),
    text=("群组"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 群组list
group_screen_list = lv_list(
    parent=group_screen,
    pos=(0, 100),
    size=(800, 340),
    style_pad_left=(0, 0),
    style_pad_top=(0, 0),
    style_pad_row=(4, 0),
    style=[
        (style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
    ],
)
"""
===================================================Group 群组页面 end=============================================================
"""
"""
===================================================Member 成员页面 start=============================================================
"""
member_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
friend_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 群组list
"""
===================================================Member 成员页面 end=============================================================
"""
"""
===================================================History 历史消息页面 start=============================================================
"""
history_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 历史消息页面导航栏页面
history_app_bar_screen = lv_obj(
    parent=history_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
history_app_bar_img = lv_img(
    parent=history_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
history_app_bar_label = lv_label(
    parent=history_app_bar_screen,
    pos=(55, 18),
    # size=(200, 25),
    text=("历史消息"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 历史消息内容列表
history_screen_list = lv_list(
    parent=history_screen,
    pos=(0, 100),
    size=(800, 340),
    style_pad_left=(0, 0),
    style_pad_top=(0, 0),
    style_pad_row=(4, 0),
    style=[
        (style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
    ],
)

"""
===================================================History 历史消息页面 end=============================================================
"""
"""
===================================================天气页面 start=============================================================
"""
weather_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 天气页面导航栏页面
weather_app_bar_screen = lv_obj(
    parent=weather_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_app_bar_img = lv_img(
    parent=weather_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_app_bar_label = lv_label(
    parent=weather_app_bar_screen,
    pos=(55, 18),
    # size=(120, 25),
    text=("天气"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_app_city_label = lv_label(
    parent=weather_app_bar_screen,
    pos=(280, 15),
    # size=(240, 32),
    text=("--市 天气预报"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 天气内容页
weather_content_screen = lv_obj(
    parent=weather_screen,
    pos=(0, 100),
    size=(800, 340),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 分割线
line_points = [
    {"x": 0, "y": 0},
    {"x": 0, "y": 352},
]
weather_content_line1 = lv_line(
    parent=weather_content_screen,
    pos=(275, 8),
    size=(12, 332),
    points=(line_points, 3),
    style=[(weather_content_line_style, lv.PART.MAIN | lv.STATE.DEFAULT)]
)
weather_content_line2 = lv_line(
    parent=weather_content_screen,
    pos=(525, 8),
    size=(12, 332),
    points=(line_points, 3),
    style=[(weather_content_line_style, lv.PART.MAIN | lv.STATE.DEFAULT)]
)
# 天气日期
weather_date_1 = lv_label(
    parent=weather_content_screen,
    pos=(30, 20),
    # size=(200, 32),
    text=("2000-01-01"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天
weather_day_label_1 = lv_label(
    parent=weather_content_screen,
    pos=(30, 60),
    # size=(200, 32),
    text=("白天"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气图片
weather_day_img_1 = lv_img(
    parent=weather_content_screen,
    pos=(30, 90),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气与温度
weather_day_temp_info_1 = lv_label(
    parent=weather_content_screen,
    pos=(100, 106),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天风向
weather_day_wind_label_1 = lv_label(
    parent=weather_content_screen,
    pos=(30, 160),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_day_wind_info_1 = lv_label(
    parent=weather_content_screen,
    pos=(130, 160),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚
weather_night_label_1 = lv_label(
    parent=weather_content_screen,
    pos=(30, 200),
    # size=(200, 32),
    text=("夜晚"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气图片
weather_night_img_1 = lv_img(
    parent=weather_content_screen,
    pos=(30, 230),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气与温度
weather_night_temp_info_1 = lv_label(
    parent=weather_content_screen,
    pos=(100, 246),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚风向
weather_night_wind_label_1 = lv_label(
    parent=weather_content_screen,
    pos=(30, 300),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_night_wind_info_1 = lv_label(
    parent=weather_content_screen,
    pos=(130, 300),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 天气日期
weather_date_2 = lv_label(
    parent=weather_content_screen,
    pos=(300, 20),
    # size=(200, 32),
    text=("2000-01-01"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天
weather_day_label_2 = lv_label(
    parent=weather_content_screen,
    pos=(300, 60),
    # size=(200, 32),
    text=("白天"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气图片
weather_day_img_2 = lv_img(
    parent=weather_content_screen,
    pos=(300, 90),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气与温度
weather_day_temp_info_2 = lv_label(
    parent=weather_content_screen,
    pos=(370, 106),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天风向
weather_day_wind_label_2 = lv_label(
    parent=weather_content_screen,
    pos=(300, 160),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_day_wind_info_2 = lv_label(
    parent=weather_content_screen,
    pos=(400, 160),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚
weather_night_label_2 = lv_label(
    parent=weather_content_screen,
    pos=(300, 200),
    # size=(200, 32),
    text=("夜晚"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气图片
weather_night_img_2 = lv_img(
    parent=weather_content_screen,
    pos=(300, 230),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气与温度
weather_night_temp_info_2 = lv_label(
    parent=weather_content_screen,
    pos=(370, 246),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚风向
weather_night_wind_label_2 = lv_label(
    parent=weather_content_screen,
    pos=(300, 300),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_night_wind_info_2 = lv_label(
    parent=weather_content_screen,
    pos=(400, 300),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 天气日期
weather_date_3 = lv_label(
    parent=weather_content_screen,
    pos=(550, 20),
    # size=(200, 32),
    text=("2000-01-01"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天
weather_day_label_3 = lv_label(
    parent=weather_content_screen,
    pos=(550, 60),
    # size=(200, 32),
    text=("白天"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气图片
weather_day_img_3 = lv_img(
    parent=weather_content_screen,
    pos=(550, 90),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天天气与温度
weather_day_temp_info_3 = lv_label(
    parent=weather_content_screen,
    pos=(620, 106),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 白天风向
weather_day_wind_label_3 = lv_label(
    parent=weather_content_screen,
    pos=(550, 160),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_day_wind_info_3 = lv_label(
    parent=weather_content_screen,
    pos=(650, 160),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚
weather_night_label_3 = lv_label(
    parent=weather_content_screen,
    pos=(550, 200),
    # size=(200, 32),
    text=("夜晚"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气图片
weather_night_img_3 = lv_img(
    parent=weather_content_screen,
    pos=(550, 230),
    size=(64, 64),
    src=(MEDIA_DIR + 'main_weather_qing.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚天气与温度
weather_night_temp_info_3 = lv_label(
    parent=weather_content_screen,
    pos=(620, 246),
    size=(150, 32),
    text=("-- --℃"),
    long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 夜晚风向
weather_night_wind_label_3 = lv_label(
    parent=weather_content_screen,
    pos=(550, 300),
    # size=(150, 32),
    text=("风向:"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
weather_night_wind_info_3 = lv_label(
    parent=weather_content_screen,
    pos=(650, 300),
    # size=(150, 32),
    text=("--"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
"""
===================================================天气页面 end=============================================================
"""
loading_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================位置页面 start=============================================================
"""
location_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 位置内容页
location_content_screen = lv_obj(
    parent=location_screen,
    pos=(0, 40),
    size=(800, 400),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
"""
===================================================位置页面 end=============================================================
"""
"""
===================================================设置页面 start=============================================================
"""
setting_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 对讲页面导航栏页面
setting_app_bar_screen = lv_obj(
    parent=setting_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
setting_app_bar_img = lv_img(
    parent=setting_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
setting_app_bar_label = lv_label(
    parent=setting_app_bar_screen,
    pos=(55, 18),
    # size=(120, 25),
    text=("设置"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 设置内容页
setting_content_screen = lv_obj(
    parent=setting_screen,
    pos=(0, 100),
    size=(800, 340),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)

"""
===================================================设置页面 end=============================================================
"""
"""
===================================================音量页面 start=============================================================
"""
vol_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 音量设置导航栏页面
vol_app_bar_screen = lv_obj(
    parent=vol_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
vol_app_bar_img = lv_img(
    parent=vol_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
vol_app_bar_label = lv_label(
    parent=vol_app_bar_screen,
    pos=(55, 18),
    # size=(200, 25),
    text=("音量设置"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
# 音量页面内容
# 设置内容页
vol_content_screen = lv_obj(
    parent=vol_screen,
    pos=(0, 100),
    size=(800, 340),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
vol_style_bg = lv.style_t()
vol_style_indic = lv.style_t()
vol_style_bg.init()
vol_style_bg.set_border_color(lv.palette_main(lv.PALETTE.BLUE))
vol_style_bg.set_border_width(2)
vol_style_bg.set_pad_all(6)  # To make the indicator smaller
vol_style_bg.set_radius(6)
vol_style_bg.set_anim_time(1000)
vol_style_indic.init()
vol_style_indic.set_radius(3)
vol_style_indic.set_bg_opa(lv.OPA.COVER)
vol_style_indic.set_bg_color(lv.palette_main(lv.PALETTE.BLUE))
vol_label = lv_label(
    parent=vol_content_screen,
    pos=(340, 80),
    text=("音量9"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
vol_bar = lv.bar(vol_content_screen)
vol_bar.remove_style_all()
vol_bar.add_style(vol_style_bg, 0)
vol_bar.add_style(vol_style_indic, lv.PART.INDICATOR)
vol_bar.set_size(600, 40)
vol_bar.center()
vol_bar.set_value(50, lv.ANIM.OFF)
"""
===================================================音量页面 end=============================================================
"""
"""
===================================================SIM卡切换页面 start=============================================================
"""
sim_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
noise_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
call_level_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
recovery_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================SIM卡切换页面 end=============================================================
"""
"""
===================================================息屏时间页面 start=============================================================
"""
screen_time_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================息屏时间页面 end=============================================================
"""
"""
===================================================单呼退出时间页面 start=============================================================
"""
call_time_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================单呼退出时间页面 end=============================================================
"""
"""
===================================================蓝牙管理页面 start=============================================================
"""
bluetooth_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================蓝牙管理页面 end=============================================================
"""
"""
===================================================快捷键查询页面 start=============================================================
"""
hotkey_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================蓝牙管理页面 end=============================================================
"""
"""
===================================================语言切换页面 start=============================================================
"""
language_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================SIM卡切换页面 end=============================================================
"""

gps_info_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
ota_info_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
"""
===================================================系统页面 start=============================================================
"""
system_screen = lv_obj(
    style=[
        (screen_style, lv.PART.MAIN | lv.STATE.DEFAULT),
        (style_list_scrollbar, lv.PART.MAIN | lv.STATE.DEFAULT)
    ]
)
# 对讲页面导航栏页面
system_screen_app_bar_screen = lv_obj(
    parent=system_screen,
    pos=(0, 40),
    size=(800, 60),
    style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
system_screen_app_bar_img = lv_img(
    parent=system_screen_app_bar_screen,
    pos=(0, 10),
    size=(48, 48),
    src=(MEDIA_DIR + 'back.png'),
    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
system_screen_app_bar_label = lv_label(
    parent=system_screen_app_bar_screen,
    pos=(55, 18),
    # size=(200, 25),
    text=("系统信息"),
    long_mode=(lv.label.LONG.WRAP),
    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
    style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
)
"""
===================================================关机页面 start=============================================================
"""
shutdown_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
shutdown_label = lv_label(parent=shutdown_screen, pos=(0, 200), text=(""), long_mode=(lv.label.LONG.WRAP),
                          style_text_align=(lv.TEXT_ALIGN.CENTER, 0), size=(800, 50),
                          style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )

"""
===================================================关机页面 start=============================================================
"""
sos_screen = lv_obj(style=[(screen_style, lv.PART.MAIN | lv.STATE.DEFAULT)])
sos_img = lv.img(sos_screen)
sos_img.set_pos(250, 150)
sos_img.set_size(297, 105)
sos_img.set_src(MEDIA_DIR + 'sos.png')
sos_label = lv_label(parent=sos_screen, pos=(0, 300), text=("1111"), long_mode=(lv.label.LONG.WRAP),
                     style_text_align=(lv.TEXT_ALIGN.CENTER, 0), size=(800, 50),
                     style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )


class VolMsgBox(object):
    def __init__(self):
        self.vol_box = None
        self.vol_label = None
        self.bar1 = None
        self.vol_box_timer = OSTIMER("vol_box")

    def post_processor_after_instantiation(self):
        subscribe("msg_box_vol_add", self.add)
        subscribe("msg_box_vol_reduce", self.reduce)
        subscribe("msg_box_vol_show", self.show)

    def add(self, topic, screen):
        vol = publish("audio_add_volume")
        publish("msg_box_vol_show", [screen, vol])

    def reduce(self, topic, screen):
        vol = publish("audio_reduce_volume")
        publish("msg_box_vol_show", [screen, vol])

    def hide(self, *args):
        if self.vol_box:
            self.vol_box.delete()
            self.vol_box = None
        _thread.start_new_thread(self.store_vol, ())

    def store_vol(self, *args):
        publish("push_store_vol")

    def show(self, topic, data):
        if self.vol_box is None:
            self.vol_box_timer.start(2000, 0, self.hide)
            self.vol_box = lv.msgbox(data[0], "", "", [], False)
            self.vol_box.set_size(600, 200)
            modal = self.vol_box.get_parent()
            modal.set_style_bg_opa(lv.OPA.TRANSP, 0)
            self.vol_box.center()
            self.vol_label = lv_label(
                parent=self.vol_box,
                pos=(340, 80),
                text=("音量9"),
                long_mode=(lv.label.LONG.WRAP),
                style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
                style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
            )
            self.bar1 = lv.bar(self.vol_box)
            self.bar1.remove_style_all()
            self.bar1.add_style(vol_style_bg, 0)
            self.bar1.add_style(vol_style_indic, lv.PART.INDICATOR)
            self.bar1.set_size(500, 40)
            self.bar1.center()
        else:
            self.vol_box_timer.stop()
            self.vol_box_timer.start(2000, 0, self.hide)
        # self.label1.set_text( str(data[1]))#"当前音量: " +
        vol = publish("audio_volume")
        val = int(vol / 8 * 100)
        if publish("config_get", "language") == "CN":
            label = "音量 " + str(vol)
            publish("poc_tts_play", label)
        else:
            label = "Voice " + str(vol)
        if self.vol_box:
            self.vol_label.set_text(label)
            self.bar1.set_value(val, lv.ANIM.OFF)


class Screen(Abstract):
    def __init__(self):
        self.load_status = True
        self.meta = None
        self.cur = 0
        self.count = 0
        self.comp = None
        self.main_cont_top = main_cont_top
        self.main_top_net = main_top_net
        self.main_top_gps_img = main_top_gps_img
        self.main_top_csq_img = main_top_csq_img
        self.main_top_battery_img = main_top_battery_img
        self.main_top_bt_img = main_top_bt_img
        self.main_top_time = main_top_time
        self.main_voice_img = main_voice_img
        self.main_sim_img = main_sim_img
        self.main_sd_img = main_sd_img
        self.main_bottom = main_bottom
        self.main_bottom_img = main_bottom_img
        self.main_bottom_label = main_bottom_label
        self.main_date_screen_label = main_date_screen_label
        self.main_time_screen_label = main_time_screen_label
        self.top_bottom_refresh_timer = OSTIMER("top_bottom_refresh")

    def get_comp(self):
        return self.comp

    def post_processor_after_load(self, *args, **kwargs):
        self.top_bottom_refresh_fun(None)
        self.top_bottom_refresh_timer_start()

    def post_processor_after_instantiation(self):
        subscribe("call_info_refresh", self.call_info_refresh)
        subscribe("top_bottom_info_init", self.top_bottom_info_init)
        subscribe("show_volume_img", self.show_volume_img)
        subscribe("push_sd_status", self.show_sd_img)
        subscribe("push_sim_slot", self.show_sim_img)
        subscribe("push_gps_enable", self.show_gps_img)
        self.top_bottom_info_init(refresh_bottom=False)

    def post_processor_after_initialization(self):
        self.update_top_bottom_parent()

    def set_meta(self, msg):
        self.meta = msg

    def play_tts(self):
        pass

    def load_start(self):
        self.load_status = False
        self.play_tts()

    def load_end(self):
        self.load_status = True

    def success(self):
        pass

    def fail(self):
        pass

    def up_long(self):
        pass

    def back(self):
        pass

    def down_long(self):
        pass

    def btn_num_click(self, msg):
        pass

    def back_long(self):
        pass

    def sos_long(self):
        pass

    def sos(self):
        pass

    def get_load(self):
        return self.load_status

    def deactivate(self):
        self.top_bottom_refresh_timer.stop()

    @staticmethod
    def publish_ope():
        # 主动向后端请求运营商资源
        return publish("screen_get_ope")

    @staticmethod
    def publish_sig():
        # 主动向后端请求信号强度
        return publish("screen_get_sig")

    @staticmethod
    def publish_time():
        # 主动向后端请求时间
        return publish("screen_get_time")

    @staticmethod
    def publish_battery():
        # 主动向后端请求电池电量
        return publish("screen_get_battery")

    @staticmethod
    def language():
        return publish("config_get", "language")

    def update_top_bottom_parent(self):
        if self.comp:
            self.main_cont_top.set_parent(self.comp)
            self.main_bottom.set_parent(self.comp)

    def top_bottom_refresh_fun(self, args):
        publish("top_bottom_info_init")

    def top_bottom_info_init(self, event=None, msg=None, refresh_bottom=True):
        _thread.start_new_thread(self.__top_bottom_info_init, (refresh_bottom,))

    def __top_bottom_info_init(self, refresh_bottom=True):
        self.main_top_net.set_text(self.publish_ope())
        self.main_top_battery_img.set_src(self.publish_battery())
        self.show_volume_img(None, publish("audio_volume_get"))
        self.show_sim_img(None, publish("sim_slot_get"))
        self.show_sd_img(None, publish("sd_status_get"))
        if publish("get_sim_status") == 1:
            sig = self.publish_sig()
            sig_img = MEDIA_DIR + "signal_" + (str(int(sig * 5 / 31)) if 0 < sig <= 31 else "0") + ".png"
        else:
            sig_img = MEDIA_DIR + "signal_0.png"
        self.main_top_csq_img.set_src(sig_img)
        bt_state = publish("bluetooth_state")
        bt_img = MEDIA_DIR + "bluetooth_on.png"
        if bt_state == 0 or bt_state is None:
            bt_img = MEDIA_DIR + "None.png"
        elif bt_state == 3:
            bt_img = MEDIA_DIR + "bluetooth_conn.png"
        self.main_top_bt_img.set_src(bt_img)
        self.show_gps_img(msg=publish("get_gps_flag"))
        if publish("current_screen") == "menu_screen":
            self.main_top_time.set_text("")
            self.main_date_screen_label.set_text(self.publish_time()[0])
            self.main_time_screen_label.set_text(self.publish_time()[1])
        else:
            self.main_top_time.set_text(self.publish_time()[1])

    def call_info_refresh(self, event=None, msg=None):
        # print("call info refresh")
        self.main_bottom_img.set_src(MEDIA_DIR + 'main_group.png')
        self.main_bottom_label.set_text("[%s] (%s) %s" % (msg[1], msg[2], msg[3]))
        self.bg_color(self.main_bottom, msg[0])
        # print("call info refresh finished")

    def show_gps_img(self, event=None, msg=None):
        if not publish("config_gps_enable"):
            self.main_top_gps_img.set_src(MEDIA_DIR + "_")
            return
        if not msg:
            self.main_top_gps_img.set_src(MEDIA_DIR + "gps1.png")
        else:
            self.main_top_gps_img.set_src(MEDIA_DIR + "gps.png")

    def show_volume_img(self, event, msg):
        if not msg:
            self.main_voice_img.set_src(MEDIA_DIR + "voice_close.png")
        else:
            self.main_voice_img.set_src(MEDIA_DIR + "voice_close1.png")

    def show_sim_img(self, event, msg):
        # print("-----------------------{}".format(msg))
        if not msg:
            self.main_sim_img.set_src(MEDIA_DIR + "sim1.png")
        else:
            self.main_sim_img.set_src(MEDIA_DIR + "sim2.png")

    def show_sd_img(self, event, msg):
        if not msg:
            self.main_sd_img.set_src(MEDIA_DIR + "SD.png")
        else:
            self.main_sd_img.set_src(MEDIA_DIR + "SD0.png")

    @staticmethod
    def bg_color(btn, strategy):
        if not strategy:
            btn.set_style_bg_color(lv.color_make(0x56, 0x9e, 0xeb), 0)
            btn.set_style_bg_grad_color(lv.color_make(0x56, 0x9e, 0xeb), 0)
        elif strategy == 1:
            btn.set_style_bg_color(lv.color_make(0xff, 0x00, 0x00), 0)
            btn.set_style_bg_grad_color(lv.color_make(0xff, 0x00, 0x00), 0)
        elif strategy == 2:
            btn.set_style_bg_color(lv.color_make(0x00, 0xff, 0x00), 0)
            btn.set_style_bg_grad_color(lv.color_make(0x00, 0xff, 0x00), 0)

    #
    # def do_show_state(self, event=None, msg=None):
    #     self.main_bottom_img.set_src(MEDIA_DIR + 'main_group.png')
    #     self.main_bottom_label.set_text("[%s] (%s) %s" % (msg[0], msg[1], group_name))

    def top_bottom_refresh_timer_start(self, seconds=60, timer_fun=None):
        self.top_bottom_refresh_timer.stop()
        self.top_bottom_refresh_timer.start(seconds * 1000, 1,
                                            self.top_bottom_refresh_fun if timer_fun is None else timer_fun)


class PopUpMsgBox(object):
    # 设置结果弹窗

    def __init__(self):
        super().__init__()
        self.__msg_tid = None
        self.opoup_window_box = None
        self.opoup_window_label = None
        self.__hide_timer = OSTIMER("hide_timer")
        self.__init_win_box()
        self.log = LogAdapter(self.__class__.__name__)

    def __init_win_box(self):
        self.opoup_window_box = lv.msgbox(main_screen, "", "", [], False)
        self.opoup_window_box.set_size(600, 200)
        self.opoup_window_box.center()
        self.opoup_window_label = lv.label(self.opoup_window_box)
        # self.opoup_window_label.set_pos(0, 0)
        self.opoup_window_label.center()
        self.opoup_window_label.set_size(500, 100)
        self.opoup_window_label.add_style(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.opoup_window_label.set_text("")
        self.opoup_window_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.opoup_window_box.add_flag(lv.obj.FLAG.HIDDEN)

    def post_processor_after_instantiation(self):
        subscribe("msg_box_popup_show", self.show)
        subscribe("msg_box_popup_hide", self.hide)
        subscribe("msg_box_popup_reset", self.reset)

    def show(self, topic, data):
        self.__stop_show(None)
        self.__start_show(data)

    def hide(self, event=None, msg=None):
        self.__stop_show(None)

    def reset(self, event=None, msg=None):
        self.opoup_window_label.set_text(msg)

    def __start_show(self, data):
        self.__msg_tid = create_thread(self.__show_fun, args=(data,), stack_size=0x1000)

    def __stop_show(self, args):
        self.__hide_timer.stop()
        if self.__msg_tid:
            try:
                _thread.stop_thread(self.__msg_tid)
            except:
                pass
        self.__msg_tid = None
        self.opoup_window_box.add_flag(lv.obj.FLAG.HIDDEN)
        self.opoup_window_label.set_text("")

    def __show_fun(self, data):
        screen_obj = data.get("screen")
        show_msg = data.get("msg")
        # font_style = data.get("font")
        sleep_time = data.get("sleep_time", 1)
        self.log.debug("show_msg: [%s], sleep_time: [%s]" % (show_msg, sleep_time))
        self.opoup_window_label.set_text(show_msg)
        self.opoup_window_box.set_parent(screen_obj)
        self.opoup_window_box.clear_flag(lv.obj.FLAG.HIDDEN)
        self.__hide_timer.start(sleep_time * 1000, 0, self.__stop_show)


class CommonScreen(Screen):
    class CHECK:
        YES = MEDIA_DIR + "None.png"
        NO = MEDIA_DIR + "None.png"

    def __init__(self):
        super().__init__()
        self.profile = []
        self.app_bar_screem = None
        self.app_bar_img = None
        self.app_bar_label = None
        self.screen_list = None
        self.currentButton = None
        self.btn_list = []
        self.selected = 0

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.get_profile()
        self.app_bar_screen = lv_obj(
            parent=self.get_comp(),
            pos=(0, 40),
            size=(800, 60),
            style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.app_bar_img = lv_img(
            parent=self.app_bar_screen,
            pos=(0, 10),
            size=(48, 48),
            src=(MEDIA_DIR + 'back.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.app_bar_label = lv_label(
            parent=self.app_bar_screen,
            pos=(55, 18),
            # size=(300, 25),
            text=(""),
            long_mode=(lv.label.LONG.WRAP),
            style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
            style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.screen_list = lv_list(
            parent=self.get_comp(),
            pos=(0, 100),
            size=(800, 340),
            style_pad_left=(0, 0),
            style_pad_top=(0, 0),
            style_pad_row=(4, 0),
            style=[
                (style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT),
                (style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            ],
        )

    def set_btn_src_style(self, idx1, idx2, status):
        btn_info = self.btn_list[idx1]
        if len(btn_info) >= 3:
            btn_info[idx2].set_src(status)

    def do_select(self):
        self.set_btn_src_style(self.selected, -1, self.CHECK.NO)
        self.set_btn_src_style(self.cur, -1, self.CHECK.YES)
        self.selected = self.cur

    def ok_switch(self):
        self.do_select()

    def ok_radio(self):
        if self.selected != self.cur:
            self.do_select()
            return True

    def ok(self):
        return self.ok_radio()

    def down(self):
        cur = self.cur + 1
        self.__clear_state()
        if cur > self.count - 1:
            cur = 0
            self.cur = cur
        else:
            self.cur = cur
        self.__add_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_state()
        if cur < 0:
            cur = self.count - 1
            self.cur = cur
        else:
            self.cur = cur
        self.__add_state()

    def __add_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.screen_list.get_child(cur)
        self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.screen_list.get_child(cur)
        self.currentButton.set_style_bg_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.set_style_bg_grad_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
        self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def get_profile(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        if not self.profile:
            self.profile = profile
        return profile

    def init_btn_lang(self, profile):
        pass

    def __default_language(self):
        profile = self.get_profile()
        self.app_bar_label.set_text(profile[0])
        self.init_btn_lang(profile)

    def back(self):
        if self.cur > 0:
            self.__clear_state()

    def init_btn_style(self):
        for i, btn_info in enumerate(self.btn_list):
            if i == self.cur:
                self.set_btn_src_style(i, -1, self.CHECK.YES)
            else:
                self.set_btn_src_style(i, -1, self.CHECK.NO)

    def init_cur(self):
        pass

    def initialization(self):
        self.load_start()
        self.__default_language()
        if self.meta.get("init"):
            if self.cur >= 0:
                self.__clear_state()
            self.init_cur()
            self.selected = self.cur
            self.__add_state()
            self.init_btn_style()
        self.top_bottom_refresh_timer_start()
        self.load_end()


class MenuScreen(Screen):
    NAME = "menu_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.comp = main_screen
        self._flag = False
        self.menu_ui_btn_list = []
        self.main_weather_screen_img_2 = main_weather_screen_img_2
        self.main_weather_screen_label_2 = main_weather_screen_label_2
        self.main_weather_screen_label_3 = main_weather_screen_label_3
        self.timer = OSTIMER("MenuScreen")

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.menu_ui_btn_list = [
            {"load_screen": {"screen": "tbk_screen", "init": True}, "img": MEDIA_DIR + 'tbk.png', "btns": []},
            {"load_screen": {"screen": "weather_screen", "init": True}, "img": MEDIA_DIR + 'weather.png', "btns": []},
            {"load_screen": {"screen": "setting_screen", "init": True}, "img": MEDIA_DIR + 'setting.png',
             "btns": []}
        ]
        if publish("config_gps_enable"):
            self.menu_ui_btn_list.insert(1, {"load_screen": {"screen": "location_screen", "init": True},
                                             "img": MEDIA_DIR + 'location.png', "btns": []})

        # main 功能页面 对讲功能键
        raw_interval = 200
        start = int((WIDTH - len(self.menu_ui_btn_list) * 200) / 2)
        for i, btn_info in enumerate(self.menu_ui_btn_list):
            btn_info["btns"] = [
                lv_img(
                    parent=self.get_comp(),
                    pos=(start + 68 + raw_interval * i, 220),
                    size=(64, 64),
                    src=(btn_info["img"]),
                    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
                ),
                lv_obj(
                    parent=self.get_comp(),
                    add_flag=(lv.obj.FLAG.HIDDEN),
                    pos=(start + 44 + raw_interval * i, 198),
                    size=(112, 112),
                    style_bg_opa=(0, 0),
                    style_border_width=(1, 0),
                    style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0),
                ),
                lv_label(
                    parent=self.get_comp(),
                    pos=(start + raw_interval * i, 340),
                    size=(200, 27),
                    text=(""),
                    long_mode=(lv.label.LONG.WRAP),
                    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
                    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
                )]
        self.count = len(self.menu_ui_btn_list)
        subscribe("main_screen_weather_refresh", self.__main_weather_screen_refresh)

    def initialization(self):
        self.load_start()
        if self.meta.get("init"):
            self._flag = False
            if self.cur >= 0:
                self.__clear_state()
            self.cur = 0
        self.__default_language()
        publish_async("main_screen_weather_refresh")
        self.timer.start(60000, 1, self.__main_weather_screen_refresh)
        self.load_end()

    def deactivate(self):
        super(MenuScreen, self).deactivate()
        self.timer.stop()

    def ok(self):
        publish("load_screen", self.menu_ui_btn_list[self.cur]['load_screen'])

    def back(self):
        self._flag = False
        self.__clear_state()
        self.cur = 0

    def down(self):
        if not self._flag:
            self._flag = True
            self.__add_state()
            return
        cur = self.cur + 1
        self.__clear_state()
        if cur > self.count - 1:
            cur = 0
            self.cur = cur
        else:
            self.cur = cur
        self.__add_state()

    def up(self):
        self._flag = True
        cur = self.cur - 1
        self.__clear_state()
        if cur < 0:
            cur = self.count - 1
            self.cur = cur
        else:
            self.cur = cur
        self.__add_state()

    def __add_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.menu_ui_btn_list[cur]['btns'][1].clear_flag(lv.obj.FLAG.HIDDEN)

    def __clear_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.menu_ui_btn_list[cur]['btns'][1].add_flag(lv.obj.FLAG.HIDDEN)

    def __defult_weather(self):
        dw = []
        for i in range(3):
            _time = utime.localtime(utime.mktime(utime.localtime()) + (i * 24 * 60 * 60))
            day_date = "{0:02d}-{1:02d}-{2:02d}".format(_time[0], _time[1], _time[2])
            dw.append([day_date] + [""] * 6)
        return dw

    def __main_weather_screen_refresh(self, event=None, msg=None):
        weather_info = publish("poc_weather")
        self.log.debug("weather_info: %s" % str(weather_info))
        if weather_info:
            city = weather_info.get("city", "")
            day_weathers = weather_info.get("weathers", self.__defult_weather())
            today = self.publish_time()[0][:10]
            _weather = ""
            _temp = ""
            weather_temp = ""
            hour = utime.localtime()[3]
            for i in day_weathers:
                if i[0] == today:
                    _weather, _temp = (i[1], i[5]) if hour >= 6 and hour < 18 else (i[2], i[6])
                    break
            self.main_weather_screen_label_2.set_text(city)
            if "晴" in _weather:
                _weather = "晴" if publish("config_get", "language") == "CN" else "Sunny"
                pic_name = 'main_weather_qing%s.png' % ("" if hour >= 6 and hour < 18 else "_ye")
            elif "多云" in _weather:
                _weather = "多云" if publish("config_get", "language") == "CN" else "Cloudy"
                pic_name = 'main_weather_duoyun%s.png' % ("" if hour >= 6 and hour < 18 else "_ye")
            elif "阴" in _weather:
                _weather = "阴" if publish("config_get", "language") == "CN" else "Overcast"
                pic_name = "main_weather_yin.png"
            elif "雨" in _weather:
                _weather = "雨" if publish("config_get", "language") == "CN" else "Rain"
                pic_name = "main_weather_yu.png"
            elif "雪" in _weather:
                _weather = "雪" if publish("config_get", "language") == "CN" else "Snow"
                pic_name = "main_weather_xue.png"
            else:
                _weather = "晴" if publish("config_get", "language") == "CN" else "Sunny"
                pic_name = "main_weather_qing.png"

            self.main_weather_screen_img_2.set_src(MEDIA_DIR + pic_name)
            if _weather or _temp:
                weather_temp = "%s %s℃" % (_weather, _temp)
            self.main_weather_screen_label_3.set_text(weather_temp)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        for i, btn_info in enumerate(self.menu_ui_btn_list):
            self.menu_ui_btn_list[i]['btns'][2].set_text(profile[i])


class TBKScreen(Screen):
    NAME = "tbk_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.cur = 0
        self.count = 4
        self.comp = tbk_screen
        self.tbk_content_group_check_img = tbk_content_group_check_img
        self.tbk_content_member_check_img = tbk_content_member_check_img
        self.tbk_content_history_check_img = tbk_content_history_check_img
        self.tbk_content_friend_check_img = tbk_content_friend_check_img
        self.tbk_ui_btn_dict = {
            0: self.tbk_content_group_check_img,
            1: self.tbk_content_member_check_img,
            2: self.tbk_content_friend_check_img,
            3: self.tbk_content_history_check_img
        }

        self.tbk_app_bar_label = tbk_app_bar_label
        self.tbk_content_group_label = tbk_content_group_label
        self.tbk_content_member_label = tbk_content_member_label
        self.tbk_content_friend_label = tbk_content_friend_label
        self.tbk_content_history_label = tbk_content_history_label

    def play_tts(self):
        # tts_msg = "对讲" if publish("config_get", "language") == "CN" else "Intercom"
        tts_msg = "对讲" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.load_start()
        if self.meta.get("init"):
            if self.cur >= 0:
                self.__clear_tbk_state()
            self.cur = 0
            self.__add_tbk_state()
        self.__default_language()
        self.top_bottom_refresh_timer_start()
        self.load_end()

    def load(self):
        if self.cur == 0:
            return {"screen": "group_screen", "init": True}
        elif self.cur == 1:
            return {"screen": "member_screen", "init": True}
        elif self.cur == 2:
            return {"screen": "friend_screen", "init": True}
        elif self.cur == 3:
            return {"screen": "history_dir_screen", "init": True}
        return {"screen": "menu_screen", "init": True}

    def ok(self):
        publish("load_screen", self.load())

    def back(self):
        if self.cur > 0:
            self.__clear_tbk_state()
        publish("load_screen", {"screen": "menu_screen"})

    def down(self):
        cur = self.cur + 1
        self.__clear_tbk_state()
        if cur > self.count - 1:
            cur = 0
            self.cur = cur
        else:
            self.cur = cur
        self.__add_tbk_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_tbk_state()
        if cur < 0:
            cur = self.count - 1
            self.cur = cur
        else:
            self.cur = cur
        self.__add_tbk_state()

    def __add_tbk_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.tbk_ui_btn_dict.get(cur).clear_flag(lv.obj.FLAG.HIDDEN)

    def __clear_tbk_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.tbk_ui_btn_dict.get(cur).add_flag(lv.obj.FLAG.HIDDEN)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.tbk_app_bar_label.set_text(profile[0])
        self.tbk_content_group_label.set_text(profile[1])
        self.tbk_content_member_label.set_text(profile[2])
        self.tbk_content_friend_label.set_text(profile[3])
        self.tbk_content_history_label.set_text(profile[4])


class GroupScreen(Screen):
    NAME = "group_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.cur = 0
        self.count = 5
        self.page_size = 7
        self.comp = group_screen
        self.group_screen_list = group_screen_list
        self.__groups = {}
        self.__groups_btn = {}
        self.group_app_bar_label = group_app_bar_label
        self.loading = None
        self.timer = OSTIMER("GroupScreen")

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )

    def play_tts(self):
        # tts_msg = "群组" if publish("config_get", "language") == "CN" else "Group"
        tts_msg = "群组" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.__default_language()
        self.loading.clear_flag(lv.obj.FLAG.HIDDEN)
        if self.__groups_btn:
            if self.cur >= 0:
                self.__clear_group_state()
            self.cur = 0
            self.__add_group_state()

    def post_processor_after_load(self, *args, **kwargs):
        super().post_processor_after_load(*args, **kwargs)
        self.load_start()
        self.__group_screen_refresh()
        if self.cur >= 0:
            self.__clear_group_state()
        self.cur = 0
        self.__add_group_state()
        self.top_bottom_refresh_timer_start()
        self.load_end()
        self.play_group()
        self.loading.add_flag(lv.obj.FLAG.HIDDEN)
        self.group_screen_list.clear_flag(lv.obj.FLAG.HIDDEN)

    def ok(self):
        _group = self.__groups.get(self.cur)
        if _group:
            self.log.debug("Now check group info: %s" % str(_group))
            group_id = _group[0]
            res = publish("poc_joingroup", group_id)
            if res == -1:
                tts_msg = "加入群组失败" if publish("config_get", "language") == "CN" else ""
                publish("poc_tts_play", tts_msg)
            self.log.debug("poc_joingroup res: %s" % res)
        else:
            self.log.error("group info is not exists.")

    def back(self):
        publish("load_screen", {"screen": "tbk_screen"})

    def play_group(self):
        if self.count:
            data = self.__groups.get(self.cur)
            if publish("config_get", "language") == "CN":
                publish("poc_tts_play", data[1])

    def down(self):
        if self.count == 1:
            return
        cur = self.cur + 1
        self.__clear_group_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__next_group_item_create()
        self.__add_group_state()
        self.play_group()

    def up(self):
        if self.count == 1:
            return
        cur = self.cur - 1
        self.__clear_group_state()
        if cur < 0:
            self.cur = self.count - 1
            for i in range(self.count - 1, self.count - 1 - self.page_size, -1):
                self.__group_item_create(*self.__groups[i])
        else:
            self.cur = cur
            self.__next_group_item_create()
        self.__add_group_state()
        self.play_group()

    def btn_handle(self, *args):
        btn_no = args[0]
        gid = self.__groups[self.cur][0]
        hot_key = publish("config_get", "hot_key")
        hot_key[str(btn_no)]["gid"] = gid
        hot_key[str(btn_no)]["uid"] = -1
        hot_key[str(btn_no)]["mode"] = "group"
        hot_key[str(btn_no)]["name"] = self.__groups[self.cur][1]
        publish("config_store", {"hot_key": hot_key})
        param = {"screen": self.get_comp(), "msg": "群组快捷键%s设置成功" % btn_no, "sleep_time": 2}
        publish("msg_box_popup_show", param)
        # tts_msg = "群组快捷键%s设置成功" % btn_no if publish("config_get", "language") == "CN" else "Set hot key %s successfully" % btn_no
        tts_msg = "群组快捷键%s设置成功" % btn_no if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def __group_refrsh(self):
        groups = publish("poc_groups")
        # self.log.debug("poc_groups: %s" % str(groups))
        self.count = len(groups)
        if groups:
            self.__groups = {i[2]: i for i in groups}

    def __group_screen_refresh(self):
        if self.comp:
            if self.__groups_btn:
                return
            self.__group_refrsh()
            self.__group_screen_create()
            if self.__groups:
                for i in range(self.page_size if self.count >= self.page_size else self.count):
                    if self.__groups.get(i):
                        self.__group_item_create(*self.__groups[i])

    def __group_screen_create(self):
        self.group_screen_list.delete()
        self.group_screen_list = lv.list(self.comp)
        self.group_screen_list.add_flag(lv.obj.FLAG.HIDDEN)
        self.group_screen_list.set_pos(0, 100)
        self.group_screen_list.set_size(800, 340)
        self.group_screen_list.set_style_pad_left(0, 0)
        self.group_screen_list.set_style_pad_top(0, 0)
        self.group_screen_list.set_style_pad_row(4, 0)
        self.group_screen_list.add_style(style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.group_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.__groups_btn = [lv.obj(self.group_screen_list) for i in range(self.count)]

    def __group_item_create(self, *args):
        group_id, group_name, group_no = args
        if isinstance(self.__groups_btn[group_no], tuple):
            return
        # group_btn = lv.obj(self.group_screen_list)
        group_btn = self.__groups_btn[group_no]
        group_btn.set_pos(41, 0)
        group_btn.set_size(800, 53)
        group_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        group_btn_img = lv.img(group_btn)
        group_btn_img.set_pos(1, 1)
        group_btn_img.set_size(48, 48)
        group_btn_img.set_src(MEDIA_DIR + 'group_48.png')
        group_btn_label = lv.label(group_btn)
        group_btn_label.set_pos(65, 15)
        group_btn_label.set_size(300, 25)
        group_btn_label.set_text(group_name)
        group_btn_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.__groups_btn[group_no] = (group_btn, group_btn_img, group_btn_label)

    def __next_group_item_create(self):
        if self.cur >= self.page_size and self.__groups.get(self.cur):
            self.__group_item_create(*self.__groups[self.cur])

    def __add_group_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.group_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_group_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.group_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.group_app_bar_label.set_text(profile[0])


class MemberScreen(Screen):
    NAME = "member_screen"
    USER_STATE = {
        1: {"CN": "离线", "EN": "Offline"},
        2: {"CN": "在线", "EN": "Online"},
        3: {"CN": "在线在组", "EN": "Online & In the group"},
    }
    DF_USER_STATE = {"CN": "--", "EN": "--"}

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.cur = 0
        self.count = 3
        self.page_size = 7
        self.comp = member_screen
        self.currentButton = None
        self.member_screen_list = None
        self.__members = {}
        self.__members_btn = {}
        self.__usr_id_name = {}
        self.member_app_bar_label = None
        self.member_app_bar_screen = None
        self.member_app_bar_img = None
        self.member_app_bar_label = None
        self.loading = None

    def post_processor_after_instantiation(self):
        super(MemberScreen, self).post_processor_after_instantiation()
        self.member_screen_list = lv_list(
            parent=self.get_comp(),
            pos=(0, 100),
            size=(800, 340),
            style_pad_left=(0, 0),
            style_pad_top=(0, 0),
            style_pad_row=(4, 0),
            style=[
                (style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT),
                (style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
            ],
        )
        # 成员页面导航栏页面
        self.member_app_bar_screen = lv_obj(
            parent=self.get_comp(),
            pos=(0, 40),
            size=(800, 60),
            style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.member_app_bar_img = lv_img(
            parent=self.member_app_bar_screen,
            pos=(0, 10),
            size=(48, 48),
            src=(MEDIA_DIR + 'back.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.member_app_bar_label = lv_label(
            parent=self.member_app_bar_screen,
            pos=(55, 18),
            # size=(120, 25),
            text=("成员"),
            long_mode=(lv.label.LONG.WRAP),
            style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
            style=[(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.sub_init()

    def sub_init(self):
        subscribe("member_user_info", self.__member_user_info)

    def play_member(self):
        if self.count:
            data = self.__members.get(self.cur)
            if publish("config_get", "language") == "CN":
                publish("poc_tts_play", data[1])

    def play_tts(self):
        # tts_msg = "成员" if publish("config_get", "language") == "CN" else "Member"
        tts_msg = "成员" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.__default_language()
        self.member_screen_list.delete()
        self.loading.clear_flag(lv.obj.FLAG.HIDDEN)

    def post_processor_after_load(self, *args, **kwargs):
        super().post_processor_after_load()
        self.load_start()
        self.__member_screen_refresh()
        if self.cur >= 0:
            self.__clear_member_state()
        self.cur = 0
        self.__default_language()
        self.__add_member_state()
        self.top_bottom_refresh_timer_start()
        self.play_member()
        self.load_end()
        self.loading.add_flag(lv.obj.FLAG.HIDDEN)
        self.member_screen_list.clear_flag(lv.obj.FLAG.HIDDEN)

    def ok(self):
        box_show_time = 3
        if publish("signal_call_state") == 0:
            if len(self.__members) >= 1:
                # print("members", self.__members[self.cur][0], publish('poc_get_login_info')[0])
                if self.__members[self.cur][0] == publish('poc_get_login_info')[1]:
                    box_show_msg = "无法呼叫自己"
                else:
                    if self.__members[self.cur][2] != 1:
                        publish("start_signal_call", self.__members[self.cur])
                        return
                    else:
                        box_show_msg = "单呼用户%s离线" % self.__members[self.cur][1]
            else:
                box_show_msg = "无可单呼用户"
            publish("poc_tts_play", box_show_msg.replace("单呼", "单[=dan1]呼"))
        else:
            box_show_msg = "单呼用户中"
        param = {"screen": self.get_comp(), "msg": box_show_msg, "sleep_time": box_show_time}
        publish("msg_box_popup_show", param)

    def back(self):
        if publish("signal_call_state") == 0:
            publish("load_screen", {"screen": "tbk_screen"})
        else:
            publish("stop_signal_call")

    def down(self):
        if self.count == 1:
            return
        cur = self.cur + 1
        self.__clear_member_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__next_member_item_create()
        self.__add_member_state()
        self.play_member()

    def up(self):
        if self.count == 1:
            return
        cur = self.cur - 1
        self.__clear_member_state()
        if cur < 0:
            self.cur = self.count - 1
            for i in range(self.count - 1, self.count - 1 - self.page_size, -1):
                if i < 0:
                    break
                self.__member_item_create(*self.__members[i])

        else:
            self.cur = cur
            self.__next_member_item_create()
        self.__add_member_state()
        self.play_member()

    def btn_handle(self, *args):
        btn_no = args[0]
        uid = self.__members[self.cur][0]
        hot_key = publish("config_get", "hot_key")
        hot_key[str(btn_no)]["uid"] = uid
        hot_key[str(btn_no)]["gid"] = -1
        hot_key[str(btn_no)]["mode"] = "member"
        hot_key[str(btn_no)]["name"] = self.__members[self.cur][1]
        publish("config_store", {"hot_key": hot_key})
        param = {"screen": self.get_comp(), "msg": "单呼快捷键%s设置成功" % btn_no, "sleep_time": 2}
        # tts_msg = "单[=dan1]呼快捷键%s设置成功" % btn_no if publish("config_get", "language") == "CN" else "Set hot key %s successfully" % btn_no
        tts_msg = "单[=dan1]呼快捷键%s设置成功" % btn_no if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        publish("msg_box_popup_show", param)

    def create(self, members):
        self.count = len(members)
        if members:
            self.__members = {i[3]: i for i in members}
            self.__usr_id_name = {i[0]: i[1] for i in members}

    def __member_refresh(self):
        members = publish("poc_members")
        self.create(members)

    def __member_screen_refresh(self):
        if self.comp:
            self.__member_refresh()
            self.__member_screen_create()
            if self.__members:
                for i in range(self.page_size if self.count >= self.page_size else self.count):
                    if self.__members.get(i):
                        self.__member_item_create(*self.__members[i])

    def __member_screen_create(self):
        self.member_screen_list = lv.list(self.comp)
        self.member_screen_list.add_flag(lv.obj.FLAG.HIDDEN)
        self.member_screen_list.set_pos(0, 100)
        self.member_screen_list.set_size(800, 340)
        self.member_screen_list.set_style_pad_left(0, 0)
        self.member_screen_list.set_style_pad_top(0, 0)
        self.member_screen_list.set_style_pad_row(4, 0)
        self.member_screen_list.add_style(style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.member_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.__members_btn = [lv.obj(self.member_screen_list) for i in range(self.count)]

    def __member_item_create(self, *args):
        user_id, user_name, user_state, user_no = args
        if isinstance(self.__members_btn[user_no], tuple):
            return
        # member_btn = lv.obj(self.member_screen_list)
        member_btn = self.__members_btn[user_no]
        member_btn.set_pos(40, 0)
        member_btn.set_size(800, 53)
        member_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        member_btn_img = lv.img(member_btn)
        member_btn_img.set_pos(0, 0)
        member_btn_img.set_size(48, 48)
        member_btn_img.set_src(MEDIA_DIR + "member_online.png")
        member_btn_label = lv.label(member_btn)
        member_btn_label.set_pos(65, 15)
        member_btn_label.set_size(600, 25)
        login_info = publish("poc_get_login_info")
        if login_info[1] == args[0]:
            usr_info = "(%s) %s (%s)" % ("当前用户" if publish("config_get", "language") == "CN" else "Current",
                                         user_name, self.USER_STATE.get(user_state, self.DF_USER_STATE).get(
                publish("config_get", "language")))
        else:
            usr_info = "%s (%s)" % (
                user_name, self.USER_STATE.get(user_state, self.DF_USER_STATE).get(publish("config_get", "language")))
        member_btn_label.set_text(usr_info)
        member_btn_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.__members_btn[user_no] = (member_btn, member_btn_img, member_btn_label)

    def __next_member_item_create(self):
        if self.cur >= self.page_size and self.__members.get(self.cur):
            self.__member_item_create(*self.__members[self.cur])

    def __add_member_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.member_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_member_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.member_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.member_app_bar_label.set_text(profile[0])

    def __member_user_info(self, event=None, msg=None):
        if not self.__usr_id_name:
            self.__member_refresh()
        return self.__usr_id_name


class FriendScreen(MemberScreen):
    NAME = "friend_screen"

    def __init__(self):
        super(FriendScreen, self).__init__()
        self.comp = friend_screen

    def sub_init(self):
        pass

    def play_tts(self):
        # tts_msg = "成员" if publish("config_get", "language") == "CN" else "Member"
        tts_msg = "好友" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.member_app_bar_label.set_text(profile[0])

    def __member_refresh(self):
        members = publish("poc_members", 0)
        self.log.debug("poc_members: %s" % str(members))
        self.create(members)


class HistoryScreen(Screen):
    NAME = "history_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.cur = 0
        self.count = 0
        self.page_size = 7
        self.comp = history_screen
        self.history_screen_list = history_screen_list
        self.history_app_bar_label = history_app_bar_label
        self.__records = ()
        self.__history_btn = {}
        self.__record_check = 0
        self.__record_btn = 0
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )

    def play_tts(self):
        # tts_msg = "历史消息" if publish("config_get", "language") == "CN" else "History infomations."
        tts_msg = "历史消息" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def post_processor_before_initialization(self):
        self.load_start()

    def initialization(self):
        self.__default_language()
        self.history_screen_list.delete()
        self.loading.clear_flag(lv.obj.FLAG.HIDDEN)

    def post_processor_after_load(self, *args, **kwargs):
        self.__records_screen_refresh()
        if self.cur >= 0:
            self.__clear_history_state()
        self.cur = 0
        self.__default_language()
        self.__add_history_state()
        self.top_bottom_refresh_timer_start()
        # tts_msg = "进入历史消息列表" if publish("config_get", "language") == "CN" else "Enter the history message list"
        self.load_end()
        self.history_screen_list.clear_flag(lv.obj.FLAG.HIDDEN)
        self.loading.add_flag(lv.obj.FLAG.HIDDEN)

    def ok(self):
        if self.__record_check == 0:
            self.__record_check = 1
            self.__history_btn[self.cur][2].set_src(MEDIA_DIR + "record_play_check.png")
            self.__record_btn = 1
        else:
            self.__record_btn_ok()

    def back(self):
        if self.__record_check == 0:
            publish("load_screen", {"screen": "history_dir_screen", "init": False})
        else:
            self.__record_check = 0
            self.__record_btn = 0
            self.__record_btn_change()

    def down(self):
        if self.__record_check == 0:
            cur = self.cur + 1
            self.__clear_history_state()
            if cur > self.count - 1:
                self.cur = 0
            else:
                self.cur = cur
            self.__next_records_item_create()
            self.__add_history_state()
        else:
            if self.__record_btn >= 3:
                self.__record_btn = 1
            else:
                self.__record_btn += 1
            self.__record_btn_change()

    def up(self):
        if self.__record_check == 0:
            cur = self.cur - 1
            self.__clear_history_state()
            if cur < 0:
                self.cur = self.count - 1
                for i in range(self.count - 1, self.count - 1 - self.page_size, -1):
                    if i < 0:
                        break
                    self.__records_item_create(*self.__records[i])
            else:
                self.cur = cur
                self.__next_records_item_create()
            self.__add_history_state()
        else:
            if self.__record_btn <= 1:
                self.__record_btn = 3
            else:
                self.__record_btn -= 1
            self.__record_btn_change()

    def __record_btn_change(self):
        if self.__record_btn == 1:
            self.__history_btn[self.cur][2].set_src(MEDIA_DIR + "record_play_check.png")
            self.__history_btn[self.cur][3].set_src(MEDIA_DIR + "record_stop.png")
            self.__history_btn[self.cur][4].set_src(MEDIA_DIR + "record_delete.png")
        elif self.__record_btn == 2:
            self.__history_btn[self.cur][2].set_src(MEDIA_DIR + "record_play.png")
            self.__history_btn[self.cur][3].set_src(MEDIA_DIR + "record_stop_check.png")
            self.__history_btn[self.cur][4].set_src(MEDIA_DIR + "record_delete.png")
        elif self.__record_btn == 3:
            self.__history_btn[self.cur][2].set_src(MEDIA_DIR + "record_play.png")
            self.__history_btn[self.cur][3].set_src(MEDIA_DIR + "record_stop.png")
            self.__history_btn[self.cur][4].set_src(MEDIA_DIR + "record_delete_check.png")
        elif self.__record_btn == 0:
            self.__history_btn[self.cur][2].set_src(MEDIA_DIR + "record_play.png")
            self.__history_btn[self.cur][3].set_src(MEDIA_DIR + "record_stop.png")
            self.__history_btn[self.cur][4].set_src(MEDIA_DIR + "record_delete.png")

    def __record_btn_ok(self):
        if self.__record_btn == 1:
            record_name = (self.meta.get("dir")) + "/" + self.__records[self.cur][1]
            self.log.debug("play %s" % record_name)
            publish("poc_play_record", record_name)
        elif self.__record_btn == 2:
            publish("poc_stop_play_record")
        elif self.__record_btn == 3:
            record_name = (self.meta.get("dir")) + "/" + self.__records[self.cur][1]
            if publish("poc_delete_record", record_name):
                # tts_msg = "录音删除成功" if publish("config_get", "language") == "CN" else "History infomations."
                tts_msg = "录音删除成功" if publish("config_get", "language") == "CN" else ""
                publish("poc_tts_play", tts_msg)
                self.__record_check = 0
                self.__record_btn = 0
                self.initialization()
                self.post_processor_after_load()

    def __records_refresh(self):
        records = publish("poc_query_records", self.meta.get("cur"))
        # self.log.debug("poc_query_records: %s" % str(records))
        self.count = len(records)
        if records:
            self.__records = tuple(records[i] + [i] for i in range(self.count))

    def __records_screen_refresh(self):
        if self.comp:
            self.__records_refresh()
            self.__records_screen_create()
            for i in range(self.page_size if self.count >= self.page_size else self.count):
                self.__records_item_create(*self.__records[i])

    def deactivate(self):
        super(HistoryScreen, self).deactivate()
        publish("poc_stop_play_record")

    def __records_item_create(self, *args):
        folder_name, record_name, record_no = args
        if isinstance(self.__history_btn[record_no], tuple):
            return

        # history_btn = lv.obj(self.history_screen_list)
        history_btn = self.__history_btn[record_no]
        history_btn.set_pos(41, 0)
        history_btn.set_size(800, 50)
        history_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        history_btn_img = lv.img(history_btn)
        history_btn_img.set_pos(0, 1)
        history_btn_img.set_size(48, 48)
        history_btn_img.set_src(MEDIA_DIR + "record_icon.png")
        history_btn_play_img = lv.img(history_btn)
        history_btn_play_img.set_pos(630, 1)
        history_btn_play_img.set_size(48, 48)
        history_btn_play_img.set_src(MEDIA_DIR + "record_play.png")
        history_btn_stop_img = lv.img(history_btn)
        history_btn_stop_img.set_pos(690, 1)
        history_btn_stop_img.set_size(48, 48)
        history_btn_stop_img.set_src(MEDIA_DIR + "record_stop.png")
        history_btn_delete_img = lv.img(history_btn)
        history_btn_delete_img.set_pos(750, 1)
        history_btn_delete_img.set_size(48, 48)
        history_btn_delete_img.set_src(MEDIA_DIR + "record_delete.png")
        history_btn_label = lv.label(history_btn)
        history_btn_label.set_pos(65, 15)
        history_btn_label.set_size(500, 25)
        history_btn_label.set_text(folder_name + "-" + record_name)
        history_btn_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)

        self.__history_btn[record_no] = (
            history_btn, history_btn_img, history_btn_play_img, history_btn_stop_img, history_btn_delete_img,
            history_btn_label
        )

    def __next_records_item_create(self):
        if self.cur >= self.page_size and self.cur < self.count:
            self.__records_item_create(*self.__records[self.cur])

    def __records_screen_create(self):
        self.history_screen_list = lv.list(self.comp)
        self.history_screen_list.add_flag(lv.obj.FLAG.HIDDEN)
        self.history_screen_list.set_pos(0, 100)
        self.history_screen_list.set_size(800, 340)
        self.history_screen_list.set_style_pad_left(0, 0)
        self.history_screen_list.set_style_pad_top(0, 0)
        self.history_screen_list.set_style_pad_row(4, 0)
        self.history_screen_list.add_style(style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.history_screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.__history_btn = [lv.obj(self.history_screen_list) for i in range(self.count)]

    def __add_history_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.history_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_history_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.history_screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.history_app_bar_label.set_text(profile[0])


class HistoryDirScreen(Screen):
    NAME = "history_dir_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.cur = 0
        self.count = 5
        self.page_size = 7
        self.comp = history_dir_screen
        self.screen_list = history_dir_list
        self.__data = {}
        self.__data_btn = {}
        self.app_bar_label = history_dir_bar_label
        self.loading = None
        self.timer = OSTIMER("HistoryDirScreen")

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )

    def play_tts(self):
        # tts_msg = "群组" if publish("config_get", "language") == "CN" else "Group"
        tts_msg = "历史文件" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def ok(self):
        print("self.cur = ", self.cur)
        if self.__data:
            publish("load_screen", {"screen": "history_screen", "cur": self.cur, "dir": self.__data.get(self.cur)})

    def back(self):
        publish("load_screen", {"screen": "tbk_screen"})

    def initialization(self):
        if self.meta.get("init", None) == False:
            return
        self.__default_language()
        self.loading.clear_flag(lv.obj.FLAG.HIDDEN)
        if self.__data_btn:
            if self.cur >= 0:
                self.__clear_state()
            self.cur = 0
            self.__add_state()

    def post_processor_after_load(self, *args, **kwargs):
        if self.meta.get("init", None) == False:
            return
        super().post_processor_after_load(*args, **kwargs)
        self.load_start()
        self.__screen_refresh()
        if self.cur >= 0:
            self.__clear_state()
        self.cur = 0
        self.__add_state()
        self.top_bottom_refresh_timer_start()
        self.load_end()
        self.play()
        self.loading.add_flag(lv.obj.FLAG.HIDDEN)
        self.screen_list.clear_flag(lv.obj.FLAG.HIDDEN)

    def play(self):
        if self.count:
            data = self.__data.get(self.cur)
            if publish("config_get", "language") == "CN":
                publish("poc_tts_play", data)

    def down(self):
        if self.count == 1:
            return
        cur = self.cur + 1
        self.__clear_state()
        if cur > self.count - 1:
            self.cur = 0
        else:
            self.cur = cur
        self.__next_item_create()
        self.__add_state()
        self.play()

    def up(self):
        if self.count == 1:
            return
        cur = self.cur - 1
        self.__clear_state()
        if cur < 0:
            self.cur = self.count - 1
            for i in range(self.count - 1, self.count - 1 - self.page_size, -1):
                self.__item_create(i, self.__data[i])
        else:
            self.cur = cur
            self.__next_item_create()
        self.__add_state()
        self.play()

    def __refrsh(self):
        data = publish("poc_record_get_folder_list")
        # self.log.debug("poc_groups: %s" % str(groups))
        self.count = len(data)
        if data:
            self.__data = {i: item for i, item in enumerate(data)}

    def __screen_refresh(self):
        if self.comp:
            if self.__data_btn:
                return
            self.__refrsh()
            self.__screen_create()
            if self.__data:
                for i in range(self.page_size if self.count >= self.page_size else self.count):
                    if self.__data.get(i):
                        self.__item_create(i, self.__data[i])

    def __screen_create(self):
        self.screen_list.delete()
        self.screen_list = lv.list(self.comp)
        self.screen_list.add_flag(lv.obj.FLAG.HIDDEN)
        self.screen_list.set_pos(0, 100)
        self.screen_list.set_size(800, 340)
        self.screen_list.set_style_pad_left(0, 0)
        self.screen_list.set_style_pad_top(0, 0)
        self.screen_list.set_style_pad_row(4, 0)
        self.screen_list.add_style(style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)
        self.__data_btn = [lv.obj(self.screen_list) for i in range(self.count)]

    def __item_create(self, no, name):
        if isinstance(self.__data_btn[no], tuple):
            return
        # btn = lv.obj(self.screen_list)
        btn = self.__data_btn[no]
        btn.set_pos(41, 0)
        btn.set_size(800, 53)
        btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        btn_img = lv.img(btn)
        btn_img.set_pos(1, 1)
        btn_img.set_size(48, 48)
        btn_img.set_src(MEDIA_DIR + 'dir.png')
        btn_label = lv.label(btn)
        btn_label.set_pos(65, 15)
        btn_label.set_size(300, 25)
        btn_label.set_text(name)
        btn_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        # self.__data_btn[no] = (btn, btn_img, btn_label)
        self.__data_btn[no] = (btn, btn_label)

    def __next_item_create(self):
        if self.cur >= self.page_size and self.__data.get(self.cur):
            self.__item_create(self.cur, self.__data[self.cur])

    def __add_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xe6, 0x91, 0x00), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __clear_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.currentButton = self.screen_list.get_child(cur)
        if self.currentButton:
            self.currentButton.set_style_bg_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.set_style_bg_grad_color(lv.color_make(0xd1, 0xca, 0xb7), lv.PART.MAIN | lv.STATE.DEFAULT)
            self.currentButton.scroll_to_view(lv.ANIM.OFF)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.app_bar_label.set_text(profile[0])


class _LoadingScreen(Screen):
    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.loading_container = None
        self.loading = None

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.loading_container = lv_img(
            parent=self.get_comp(),
            pos=(260, 136),
            size=(250, 125),
            zoom=(820),
            src=(MEDIA_DIR + 'location_map.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )


class LocationScreen(_LoadingScreen):
    NAME = "location_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.comp = location_screen
        self.__loc_tid = None
        self.tid = 0
        self.loading_state = False
        self.loading_container = None
        self.loading = None
        self.loading_success = False

    def __init_map(self):
        try:
            self.log.debug("__init_map")
            self.loading.clear_flag(lv.obj.FLAG.HIDDEN)
            self.loading.set_src(MEDIA_DIR + "loading.png")
            self.loading_container.add_flag(lv.obj.FLAG.HIDDEN)
            # self.loading_falied_img.add_flag(lv.obj.FLAG.HIDDEN)
            res = publish("get_location_map")
            self.tid = 1
            if res == 0 and "1.png" in uos.listdir("/usr"):
                # tts_msg = "定位成功" if publish("config_get", "language") == "CN" else "Successful positioning"
                tts_msg = "定位成功" if publish("config_get", "language") == "CN" else ""
                self.loading.add_flag(lv.obj.FLAG.HIDDEN)
                self.loading_container.clear_flag(lv.obj.FLAG.HIDDEN)
                self.loading_container.set_src("U:/1.png")
            else:
                if res == -1:
                    # tts_msg = "地图加载失败" if publish("config_get", "language") == "CN" else "Positioning failed"
                    tts_msg = "地图加载失败" if publish("config_get", "language") == "CN" else ""
                else:
                    # tts_msg = "定位失败" if publish("config_get", "language") == "CN" else "Positioning failed"
                    tts_msg = "定位失败" if publish("config_get", "language") == "CN" else ""
                self.loading.set_src(MEDIA_DIR + "loading_failed.png")
            publish("poc_tts_play", tts_msg)
        except Exception as e:
            self.loading_success = False
            sys.print_exception(e)
            self.log.error(str(e))
            # tts_msg = "定位失败" if publish("config_get", "language") == "CN" else "Positioning failed"
            tts_msg = "定位失败" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
        else:
            self.loading_state = True
            self.loading_success = True
        finally:
            self.loading_state = False
            self.__loc_tid = None
            publish("record_pa_ctrl", 0)

    def play_tts(self):
        # tts_msg = "开始定位" if publish("config_get", "language") == "CN" else "1,yuanStart positioning"
        tts_msg = "开始定位" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        if self.meta.get("init"):
            self.load_start()
        self.top_bottom_refresh_timer_start()
        if self.meta.get("init"):
            self.loading.clear_flag(lv.obj.FLAG.HIDDEN)
            self.loading.set_src(MEDIA_DIR + "loading.png")
            self.__start_loc_map()
        self.load_end()

    def ok(self):
        # self.__start_loc_map()
        if self.loading_success:
            publish("load_screen", {"screen": "gps_info_screen"})
        else:
            self.__start_loc_map()

    def __start_loc_map(self):
        self.log.debug("__start_loc_map")
        if self.__loc_tid is None or (self.__loc_tid is not None and not _thread.threadIsRunning(self.__loc_tid)):
            self.loading_success = False
            self.__loc_tid = create_thread(self.__init_map, args=(), stack_size=0x2000)

    def back(self):
        if self.__loc_tid:
            try:
                _thread.stop_thread(self.__loc_tid)
            except Exception as e:
                sys.print_exception(e)
                self.log.error(str(e))
            finally:
                self.__loc_tid = None
        publish("load_screen", {"screen": "menu_screen"})

    def down(self):
        tid = self.tid
        if tid < 0:
            tid = 2
        else:
            tid -= 1
        img = str(tid) + ".png"
        self.log.info(img)
        if not self.loading_state and img in uos.listdir('usr'):
            self.tid = tid
            self.loading_container.set_src("U:/" + img)

    def up(self):
        tid = self.tid
        if tid > 2:
            tid = 0
        else:
            tid += 1
        img = str(tid) + ".png"
        self.log.info(img)
        if not self.loading_state and img in uos.listdir('usr'):
            self.tid = tid
            self.loading_container.set_src("U:/" + img)


class WeatherScreen(Screen):
    NAME = "weather_screen"

    def __init__(self):
        super().__init__()
        self.comp = weather_screen
        self.weather_app_city_label = weather_app_city_label
        self.weathers_screen_items = {
            "weather_date_1": weather_date_1,
            "weather_day_img_1": weather_day_img_1,
            "weather_day_temp_info_1": weather_day_temp_info_1,
            "weather_day_wind_info_1": weather_day_wind_info_1,
            "weather_night_img_1": weather_night_img_1,
            "weather_night_temp_info_1": weather_night_temp_info_1,
            "weather_night_wind_info_1": weather_night_wind_info_1,
            "weather_date_2": weather_date_2,
            "weather_day_img_2": weather_day_img_2,
            "weather_day_temp_info_2": weather_day_temp_info_2,
            "weather_day_wind_info_2": weather_day_wind_info_2,
            "weather_night_img_2": weather_night_img_2,
            "weather_night_temp_info_2": weather_night_temp_info_2,
            "weather_night_wind_info_2": weather_night_wind_info_2,
            "weather_date_3": weather_date_3,
            "weather_day_img_3": weather_day_img_3,
            "weather_day_temp_info_3": weather_day_temp_info_3,
            "weather_day_wind_info_3": weather_day_wind_info_3,
            "weather_night_img_3": weather_night_img_3,
            "weather_night_temp_info_3": weather_night_temp_info_3,
            "weather_night_wind_info_3": weather_night_wind_info_3,
        }
        self.weather_app_bar_label = weather_app_bar_label
        self.weather_day_label_1 = weather_day_label_1
        self.weather_day_wind_label_1 = weather_day_wind_label_1
        self.weather_night_label_1 = weather_night_label_1
        self.weather_night_wind_label_1 = weather_night_wind_label_1
        self.weather_day_label_2 = weather_day_label_2
        self.weather_day_wind_label_2 = weather_day_wind_label_2
        self.weather_night_label_2 = weather_night_label_2
        self.weather_night_wind_label_2 = weather_night_wind_label_2
        self.weather_day_label_3 = weather_day_label_3
        self.weather_day_wind_label_3 = weather_day_wind_label_3
        self.weather_night_label_3 = weather_night_label_3
        self.weather_night_wind_label_3 = weather_night_wind_label_3

    def play_tts(self):
        # tts_msg = "天气" if publish("config_get", "language") == "CN" else "Weather forecast"
        tts_msg = "天气" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.load_start()
        self.__default_language()
        _thread.start_new_thread(self.__weather_refresh, ())
        self.top_bottom_refresh_timer_start()
        self.load_end()

    def ok(self):
        pass

    def back(self):
        publish("load_screen", {"screen": "menu_screen"})

    def down(self):
        pass

    def up(self):
        pass

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        self.weather_app_bar_label.set_text(profile[0])
        self.weather_day_label_1.set_text(profile[1])
        self.weather_day_wind_label_1.set_text(profile[2])
        self.weather_night_label_1.set_text(profile[3])
        self.weather_night_wind_label_1.set_text(profile[4])
        self.weather_day_label_2.set_text(profile[5])
        self.weather_day_wind_label_2.set_text(profile[6])
        self.weather_night_label_2.set_text(profile[7])
        self.weather_night_wind_label_2.set_text(profile[8])
        self.weather_day_label_3.set_text(profile[9])
        self.weather_day_wind_label_3.set_text(profile[10])
        self.weather_night_label_3.set_text(profile[11])
        self.weather_night_wind_label_3.set_text(profile[12])

    def __weather_refresh(self):
        if publish("poc_loginstate"):
            weather_datas = publish("poc_weather")
            if weather_datas:
                self.weather_app_city_label.set_text("%s" % weather_datas.get("city", "--"))
                if weather_datas["weathers"] and len(weather_datas["weathers"]) >= 3:
                    for i in range(1, 4):
                        _day_weather = weather_datas["weathers"][i - 1]
                        if _day_weather:
                            self.weathers_screen_items["weather_date_%d" % i].set_text(_day_weather[0])
                            day_img, day_weather = self.__init_weather_img(_day_weather[1])
                            self.weathers_screen_items["weather_day_img_%d" % i].set_src(day_img)
                            day_weather_temp = "%s %s℃" % (day_weather, _day_weather[5])
                            self.weathers_screen_items["weather_day_temp_info_%d" % i].set_text(day_weather_temp)
                            self.weathers_screen_items["weather_day_wind_info_%d" % i].set_text(_day_weather[3])
                            night_img, night_weather = self.__init_weather_img(_day_weather[2])
                            self.weathers_screen_items["weather_night_img_%d" % i].set_src(night_img)
                            night_weather_temp = "%s %s℃" % (night_weather, _day_weather[6])
                            self.weathers_screen_items["weather_night_temp_info_%d" % i].set_text(night_weather_temp)
                            self.weathers_screen_items["weather_night_wind_info_%d" % i].set_text(_day_weather[4])

    def __init_weather_img(self, name):
        language = publish("config_get", "language")
        hour = utime.localtime()[3]
        if "晴" in name:
            weather = "晴" if language == "CN" else "Sunny"
            weather_img = 'main_weather_qing%s.png' % ("" if hour >= 6 and hour < 18 else "_ye")
        elif "多云" in name:
            weather = "多云" if language == "CN" else "Cloudy"
            weather_img = 'main_weather_duoyun%s.png' % ("" if hour >= 6 and hour < 18 else "_ye")
        elif "阴" in name:
            weather = "阴" if language == "CN" else "Overcast"
            weather_img = 'main_weather_yin.png'
        elif "雨" in name:
            weather = "雨" if language == "CN" else "Rain"
            weather_img = 'main_weather_yu.png'
        elif "雪" in name:
            weather = "雪" if language == "CN" else "Snow"
            weather_img = 'main_weather_xue.png'
        else:
            weather = "晴" if language == "CN" else "Sunny"
            weather_img = "main_weather_qing.png"
        return (MEDIA_DIR + weather_img, weather)


class SettingScreen(Screen):
    NAME = "setting_screen"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.comp = setting_screen
        self.setting_ui_btn_list = [
            {"load_screen": {"screen": "vol_screen", "init": True}, "img": MEDIA_DIR + 'setting_vol.png', "btns": []},
            {"load_screen": {"screen": "sim_screen", "init": True}, "img": MEDIA_DIR + 'setting_sim.png', "btns": []},
            {"load_screen": {"screen": "screen_time_screen", "init": True}, "img": MEDIA_DIR + 'setting_screed.png',
             "btns": []},
            # {"load_screen": {"screen": "call_time_screen", "init": True}, "img": MEDIA_DIR + 'setting_call.png',
            #  "btns": []},
            {"load_screen": {"screen": "bluetooth_screen", "init": True}, "img": MEDIA_DIR + 'setting_bluetooth.png',
             "btns": []},
            {"load_screen": {"screen": "hotkey_screen", "init": True}, "img": MEDIA_DIR + 'setting_hotkey.png',
             "btns": []},
            {"load_screen": {"screen": "language_screen", "init": True}, "img": MEDIA_DIR + 'setting_language.png',
             "btns": []},
            {"load_screen": {"screen": "system_screen", "init": True}, "img": MEDIA_DIR + 'setting_sys.png',
             "btns": []},
            {"load_screen": {"screen": "noise_screen", "init": True}, "img": MEDIA_DIR + 'noice_reduction.png',
             "btns": []},
            {"load_screen": {"screen": "call_level_screen", "init": True}, "img": MEDIA_DIR + 'delivery_level.png',
             "btns": []},
            {"load_screen": {"screen": "recovery_screen", "init": True}, "img": MEDIA_DIR + 'recovery_factory.png',
             "btns": []}
        ]
        self.btn_list = []

    def post_processor_after_instantiation(self):
        row_raw_pos = [[68, 35], [44, 11], [0, 135], [0, 0]]
        target_raw_pos = eval(str(row_raw_pos))
        raw_interval = 200
        high_interval = 160
        high_bg_interval = 170
        self.count = len(self.setting_ui_btn_list)
        for i, row in enumerate(self.setting_ui_btn_list):
            row["btns"] = [
                lv_img(
                    parent=setting_content_screen,
                    pos=(target_raw_pos[0][0], target_raw_pos[0][1]),
                    size=(64, 64),
                    src=(row["img"]),
                    style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
                ),
                lv_obj(
                    parent=setting_content_screen,
                    add_flag=(lv.obj.FLAG.HIDDEN),
                    pos=(target_raw_pos[1][0], target_raw_pos[1][1]),
                    size=(112, 112),
                    style_bg_opa=(0, 0),
                    style_border_width=(1, 0),
                    style_border_color=(lv.color_make(0x21, 0x95, 0xf6), 0),
                ),
                lv_label(
                    parent=setting_content_screen,
                    pos=(target_raw_pos[2][0], target_raw_pos[2][1]),
                    size=(200, 25),
                    text=(""),
                    long_mode=(lv.label.LONG.WRAP),
                    style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
                    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
                ),
                lv_obj(parent=setting_content_screen,
                       pos=(target_raw_pos[3][0], target_raw_pos[3][1]),
                       style_bg_opa=(0, 0),
                       style_border_width=(0, 0),
                       size=(200, 170))
            ]
            offset = (i + 1) % 4
            if not offset:
                for raw in row_raw_pos[:-1]:
                    raw[1] += high_interval
                row_raw_pos[-1][1] += high_bg_interval
                target_raw_pos = eval(str(row_raw_pos))
            else:
                for raw in target_raw_pos:
                    raw[0] += raw_interval

    def ok(self):
        publish("load_screen", self.setting_ui_btn_list[self.cur]['load_screen'])

    def up_long(self):
        publish("uart_switch")

    def play_tts(self):
        # tts_msg = "设置" if publish("config_get", "language") == "CN" else "Weather forecast"
        tts_msg = "设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.load_start()
        if self.meta.get("init"):
            if self.cur >= 0:
                self.__clear_setting_state()
            self.cur = 0
            self.__add_setting_state()
        self.__default_language()
        self.top_bottom_refresh_timer_start()
        self.load_end()

    def back(self):
        if self.cur > 0:
            self.__clear_setting_state()
        publish("load_screen", {"screen": "menu_screen"})

    def down(self):
        cur = self.cur + 1
        self.__clear_setting_state()
        if cur > self.count - 1:
            cur = 0
            self.cur = cur
        else:
            self.cur = cur
        self.__add_setting_state()

    def up(self):
        cur = self.cur - 1
        self.__clear_setting_state()
        if cur < 0:
            cur = self.count - 1
            self.cur = cur
        else:
            self.cur = cur
        self.__add_setting_state()

    def __add_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.setting_ui_btn_list[cur]['btns'][1].clear_flag(lv.obj.FLAG.HIDDEN)
        self.setting_ui_btn_list[cur]['btns'][-1].scroll_to_view(0)

    def __clear_setting_state(self, cur=None):
        if cur is None:
            cur = self.cur
        self.setting_ui_btn_list[cur]['btns'][1].add_flag(lv.obj.FLAG.HIDDEN)

    def __default_language(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        setting_app_bar_label.set_text(profile[0])
        for i, raw in enumerate(self.setting_ui_btn_list):
            raw["btns"][-2].set_text(profile[i + 1])


class InstantiationCreateCommonScreen(CommonScreen):
    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        data = self.profile[1:]
        self.count = len(data)
        for raw in data:
            btn = lv_obj(
                parent=self.screen_list,
                pos=(40, 0),
                size=(800, 53),
                style=[(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)],
            )
            label = lv_label(
                parent=btn,
                pos=(20, 15),
                # size=(300, 25),
                text=(raw),
                # long_mode=(lv.label.LONG.SCROLL_CIRCULAR),
                style=[(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)],
            )
            img = lv_img(
                parent=btn,
                pos=(680, 0),
                size=(48, 48),
                src=(self.CHECK.NO),
            )
            self.btn_list.append([btn, label, img])

    def init_btn_lang(self, profile):
        for i, btn_info in enumerate(self.btn_list):
            btn_info[1].set_text(profile[i + 1])


class SelScreen(InstantiationCreateCommonScreen):
    class CHECK:
        YES = MEDIA_DIR + "select.png"
        NO = MEDIA_DIR + "no_select.png"


class SwitchScreen(InstantiationCreateCommonScreen):
    class CHECK:
        YES = MEDIA_DIR + "switch_open.png"
        NO = MEDIA_DIR + "switch_close.png"

    def __init__(self):
        super().__init__()
        self.status = False

    def init_btn_style(self):
        if self.status:
            self.set_btn_src_style(self.cur, -1, self.CHECK.YES)
        else:
            self.set_btn_src_style(self.cur, -1, self.CHECK.NO)


class SettingVolScreen(Screen):
    NAME = "vol_screen"

    def __init__(self):
        super().__init__()
        self.cur = 0
        self.count = 3
        self.comp = vol_screen
        self.vol_content_screen = vol_content_screen
        self.vol_bar = vol_bar
        self.vol_app_bar_label = vol_app_bar_label

    def play_tts(self):
        # tts_msg = "音量设置" if publish("config_get", "language") == "CN" else "Set Volume"
        tts_msg = "音量设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.load_start()
        if self.meta.get("init"):
            self.__voice_init()
        self.top_bottom_refresh_timer_start()
        self.load_end()

    def deactivate(self):
        super().deactivate()
        publish("push_store_vol")

    def ok(self):
        pass

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})

    def down(self):
        publish("audio_reduce_volume")
        # tts_msg = "设置音量减" if publish("config_get", "language") == "CN" else "Reduce volume"
        # tts_msg = "设置音量减" if publish("config_get", "language") == "CN" else ""
        tts_msg = ("设置音量%s" % publish("audio_volume")) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        self.__voice_init()

    def up(self):
        publish("audio_add_volume")
        # tts_msg = "设置音量加" if publish("config_get", "language") == "CN" else "Add volume"
        # tts_msg = "设置音量加" if publish("config_get", "language") == "CN" else ""
        tts_msg = ("设置音量%s" % publish("audio_volume")) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        self.__voice_init()

    def __voice_init(self):
        language = publish("config_get", "language")
        self.vol_app_bar_label.set_text("音量设置" if language == "CN" else "Voice")
        vol = publish("audio_volume")
        val = int(vol / 8 * 100)
        label = "音量 " if publish("config_get", "language") == "CN" else "Voice"
        vol_label.set_text(label + str(vol))
        self.vol_bar.set_value(val, lv.ANIM.OFF)


class SettingSimScreen(SelScreen):
    NAME = "sim_screen"

    def __init__(self):
        super().__init__()
        self.comp = sim_screen

    def play_tts(self):
        tts_msg = "SIM卡设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        self.cur = publish("sim_slot_get")

    def ok(self):
        if publish("sim_slot_get") != self.cur:
            publish("sim_switching")
            publish("sim_slot_switch", 1 - publish("sim_slot_get"))

    def success(self):
        tts_msg = ("设置SIM卡%s" % (self.cur + 1)) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_style(self):
        if self.cur >= 0:
            self.__clear_state()
        self.init_cur()
        self.selected = self.cur
        self.__add_state()
        self.init_btn_style()

    def fail(self):
        tts_msg = ("设置SIM卡%s失败, SIM卡不存在" % (self.cur + 1)) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        self.init_style()

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingNoiseScreen(SwitchScreen):
    NAME = "noise_screen"

    def __init__(self):
        super().__init__()
        self.comp = noise_screen

    def play_tts(self):
        tts_msg = "降噪设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        noise_onoff = publish("config_get", "noise_onoff")
        self.status = bool(noise_onoff)
        self.cur = 0

    def ok(self):
        self.status = not self.status
        self.init_btn_style()
        publish("noise_switch", self.status)
        if publish("config_get", "language") == "CN":
            onoff_msg = "开" if self.status else "关"
        else:
            onoff_msg = "open" if self.status else "close"
        tts_msg = ("降噪设置%s" % onoff_msg) if publish("config_get", "language") == "CN" else ""
        publish("set_noise_mode", int(self.status))
        publish("poc_tts_play", tts_msg)
        publish("config_store", {"noise_onoff": int(self.status)})
        publish("top_bottom_info_init")

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingCallLevelScreen(SelScreen):
    NAME = "call_level_screen"

    def __init__(self):
        super().__init__()
        self.comp = call_level_screen

    def play_tts(self):
        tts_msg = "送话等级设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        mode = publish("config_get", "call_level_no")
        self.cur = mode

    def ok(self):
        if super().ok():
            publish("call_level_sel", self.cur)
            tts_msg = self.get_profile()[self.cur + 1] if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingRecoveryScreen(CommonScreen):
    NAME = "recovery_screen"

    def __init__(self):
        super().__init__()
        self.comp = recovery_screen
        self.container = None
        self.title = None
        self.label = None
        self.content = ""
        self.profile = None

    def post_processor_after_instantiation(self):
        super().post_processor_after_instantiation()
        self.container = lv_obj(
            parent=self.get_comp(),
            pos=(0, 100),
            size=(800, 340),
            style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.title = lv_label(parent=self.get_comp(), pos=(0, 100), text=(""), long_mode=(lv.label.LONG.WRAP),
                              style_text_align=(lv.TEXT_ALIGN.CENTER, 0), size=(800, 50),
                              style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )
        self.label = lv_label(parent=self.get_comp(), pos=(0, 200), text=(""), long_mode=(lv.label.LONG.WRAP),
                              style_text_align=(lv.TEXT_ALIGN.CENTER, 0), size=(800, 50),
                              style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)], )

    def get_profile(self):
        lang = publish("config_get", "language")
        profile = LANG_PROFILE[self.NAME][lang]
        if not self.profile:
            self.profile = profile
        return profile

    def __default_language(self):
        profile = self.get_profile()
        self.app_bar_label.set_text(profile[0])
        self.title.set_text(profile[0])

    def initialization(self):
        self.content = ""
        self.__default_language()

    def btn_num_click(self, args):
        self.set_content(args)

    def set_content(self, num):
        if len(self.content) < 10:
            self.content += num
            self.label.set_text("*" * len(self.content))

    def play_tts(self):
        tts_msg = "恢复出厂" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def ok(self):
        if len(self.content):
            if self.content == "27770875":
                publish("do_shutdown", 3)
            else:
                publish("poc_tts_play", "密码错误..." if publish("config_get", "language") == "CN" else "")
                param = {"screen": self.get_comp(),
                         "msg": "密码错误..." if publish("config_get", "language") == "CN" else "Upgrading",
                         "sleep_time": 2}
                publish("msg_box_popup_show", param)
        else:
            publish("do_shutdown", 2)

    def back(self):
        if len(self.content):
            self.content = self.content[:len(self.content) - 1]
            self.label.set_text("*" * len(self.content))
            return
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingScreenTimeScreen(SelScreen):
    NAME = "screen_time_screen"
    LOCK_SCREEN_TIME_KEY = {
        -1: 0,
        30: 1,
        60: 2,
        90: 3,
        120: 4,
    }
    LOCK_SCREEN_TIME_ID = {
        0: -1,
        1: 30,
        2: 60,
        3: 90,
        4: 120,
    }

    def __init__(self):
        super().__init__()
        self.comp = screen_time_screen

    def play_tts(self):
        # tts_msg = "息屏设置" if publish("config_get", "language") == "CN" else "Always on screen settings"
        tts_msg = "息屏设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        lock_screen_time = publish("config_get", "lock_screen_time")
        self.cur = self.LOCK_SCREEN_TIME_KEY.get(lock_screen_time, -1)

    def ok(self):
        if super().ok():
            lock_screen_time = self.LOCK_SCREEN_TIME_ID.get(self.selected)
            publish("config_store", {"lock_screen_time": lock_screen_time})
            publish("lcd_state_manage")
            if publish("config_get", "language") == "CN":
                sleep_mode_msg = ("%s秒" % lock_screen_time) if lock_screen_time != -1 else "常亮"
            else:
                sleep_mode_msg = (
                        "%s seconds" % lock_screen_time) if lock_screen_time != -1 else "on forever"
            tts_msg = ("设置息屏时间%s" % sleep_mode_msg) if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingCallTimeScreen(SelScreen):
    NAME = "call_time_screen"
    CALL_TIME_KEY = {
        30: 0,
        60: 1,
        90: 2,
        120: 3,
    }
    CALL_TIME_ID = {
        0: 30,
        1: 60,
        2: 90,
        3: 120,
    }

    def __init__(self):
        super().__init__()
        self.comp = call_time_screen

    def play_tts(self):
        # tts_msg = "单呼设置" if publish("config_get", "language") == "CN" else "Single call settings"
        tts_msg = "单[=dan1]呼设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        call_time = publish("config_get", "single_call_time")
        self.cur = self.CALL_TIME_KEY.get(call_time, 0)

    def ok(self):
        if super().ok():
            call_time = self.CALL_TIME_ID.get(self.selected, 30)
            publish("config_store", {"single_call_time": call_time})
            call_time_msg = ("%s秒" % call_time) if publish("config_get", "language") == "CN" else (
                    "%s seconds" % call_time)
            tts_msg = ("设置单[=dan1]呼时间%s" % call_time_msg) if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingBluetoothScreen(SwitchScreen):
    NAME = "bluetooth_screen"

    def __init__(self):
        super().__init__()
        self.comp = bluetooth_screen

    def play_tts(self):
        # tts_msg = "蓝牙管理" if publish("config_get", "language") == "CN" else "Bluetooth management"
        tts_msg = "蓝牙管理" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        bluetooth_onoff = publish("config_get", "bluetooth_onoff")
        self.status = bool(bluetooth_onoff)
        self.cur = 0

    def ok(self):
        self.status = not self.status
        self.init_btn_style()
        if not self.status:
            publish_async("bluetooth_close")
        else:
            publish_async("bluetooth_open")
        if publish("config_get", "language") == "CN":
            onoff_msg = "开" if self.status else "关"
        else:
            onoff_msg = "open" if self.status else "close"
        tts_msg = ("设置蓝牙%s" % onoff_msg) if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)
        publish("config_store", {"bluetooth_onoff": int(self.status)})
        publish("top_bottom_info_init")

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class SettingHotKeyScreen(CommonScreen):
    NAME = "hotkey_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.comp = hotkey_screen
        self.__hotkeys = {}
        self.loading = lv_img(
            parent=self.get_comp(),
            pos=(368, 168),
            size=(64, 64),
            src=(MEDIA_DIR + 'loading.png'),
            style=[(style_bg, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )

    def play_tts(self):
        # tts_msg = "快捷键" if publish("config_get", "language") == "CN" else "Hot key"
        tts_msg = "快捷键" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        self.cur = 0

    def initialization(self):
        self.btn_list.clear()
        self.screen_list.delete()
        self.loading.clear_flag(lv.obj.FLAG.HIDDEN)

    def post_processor_after_load(self):
        self.__hotkey_screen_refresh()
        super().initialization()
        self.loading.add_flag(lv.obj.FLAG.HIDDEN)
        self.screen_list.clear_flag(lv.obj.FLAG.HIDDEN)

    def ok(self):
        pass

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()

    def __hotkey_screen_refresh(self):
        self.__hotkey_screen_create()
        self.__hotkeys = publish("config_get", "hot_key")
        self.log.debug("__hotkeys: %s" % str(self.__hotkeys))
        self.count = len(self.__hotkeys)
        for key_no in range(self.count):
            self.__hotkey_item_create(key_no, self.__hotkeys[str(key_no)])

    def __hotkey_screen_create(self):
        self.screen_list = lv.list(self.comp)
        self.screen_list.add_flag(lv.obj.FLAG.HIDDEN)
        self.screen_list.set_pos(0, 100)
        self.screen_list.set_size(800, 340)
        self.screen_list.set_style_pad_left(0, 0)
        self.screen_list.set_style_pad_top(0, 0)
        self.screen_list.set_style_pad_row(4, 0)
        self.screen_list.add_style(style_group_black_1, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.screen_list.add_style(style_list_scrollbar, lv.PART.SCROLLBAR | lv.STATE.DEFAULT)

    def __hotkey_item_create(self, key_no, ids):
        language = publish("config_get", "language")
        hotkey_btn = lv.obj(self.screen_list)
        hotkey_btn.set_pos(41, 0)
        hotkey_btn.set_size(800, 53)
        hotkey_btn.add_style(style_group_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        hotkey_btn_label = lv.label(hotkey_btn)
        hotkey_btn_label.set_pos(65, 15)
        hotkey_btn_label.set_size(700, 25)
        msg = "%s %s: " % ("快捷键" if language == "CN" else "Hot Key", key_no)
        if ids["uid"] != -1:
            msg += "%s [%s]" % ("单呼用户" if language == "CN" else "Call User", ids.get('name', ""))
        elif ids["gid"] != -1:
            msg += "%s [%s]" % (
                "切换群组" if language == "CN" else "Switch Group", ids.get('name', ""))
        else:
            msg += "--"
        hotkey_btn_label.set_text(msg)
        hotkey_btn_label.add_style(style_group_label_black, lv.PART.MAIN | lv.STATE.DEFAULT)
        self.btn_list.append([hotkey_btn, hotkey_btn_label])


class SettingLanguageScreen(SelScreen):
    NAME = "language_screen"

    def __init__(self):
        super().__init__()
        self.comp = language_screen
        self.language_mode = "CN"

    def play_tts(self):
        tts_msg = "语言设置" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def init_cur(self):
        self.language_mode = publish("config_get", "language")
        self.cur = 0 if self.language_mode == "CN" else 1

    def ok(self):
        if super().ok():
            self.language_mode = "EN" if self.selected else "CN"
            if publish("config_get", "language") == "CN":
                lan_msg = "中文" if self.language_mode == "CN" else "英文"
            else:
                lan_msg = "chinese" if self.language_mode == "CN" else "english"
            tts_msg = ("切换语言%s" % lan_msg) if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            publish("language_update", self.language_mode)
            self.top_bottom_refresh_fun(None)
            self.__default_language()

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})
        super().back()


class TextScreen(Screen):
    def __init__(self):
        super().__init__()
        self.container = None
        self.screen_list = []

    def post_processor_after_instantiation(self):
        super(TextScreen, self).post_processor_after_instantiation()
        # 系统页面内容
        self.container = lv_obj(
            parent=self.get_comp(),
            pos=(0, 100),
            size=(800, 340),
            style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.init_screen(35)

    def init_screen(self, high, default=35):
        if not self.screen_list:
            for i, profile in enumerate(self.profiles):
                self.screen_list.append(lv_label(
                    parent=self.container,
                    pos=(47, default + high * i),
                    # size=(550, 32),
                    text=(""),
                    long_mode=(lv.label.LONG.WRAP),
                    style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
                    style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
                ))
        else:
            for i, label in enumerate(self.screen_list):
                label.set_pos(47, default + high * i)


class GPSInfoScreen(TextScreen):
    NAME = "gps_info_screen"

    def __init__(self):
        super().__init__()
        self.comp = gps_info_screen
        self.timer = OSTIMER("GPS")
        self.profiles = [
            {"LANG": {"CN": "经度:", "EN": "longitude: "}},
            {"LANG": {"CN": "纬度: ", "EN": "latitude: "}},
            {"LANG": {"CN": "星数: ", "EN": "stars: "}},
            {"LANG": {"CN": "GPS开关: ", "EN": "GPS ON-OFF: "}}
        ]

    def initialization(self):
        self.timer.start(1000, 1, self.get_gps_info)

    def get_gps_info(self, *args):
        info = publish("get_gps_info")
        language = publish("config_get", "language")
        self.screen_list[0].set_text(
            self.profiles[0]["LANG"][language] + str(info["longitude"] + "  " + info["lng_direct"]))
        self.screen_list[1].set_text(
            self.profiles[1]["LANG"][language] + str(info["latitude"] + "  " + info["lat_direct"]))
        self.screen_list[2].set_text(self.profiles[2]["LANG"][language] + str(info["stars"]))
        if language == "CN":
            on_off = "开" if publish("config_gps_enable") else "关"
        else:
            on_off = "ON" if publish("config_gps_enable") else "OFF"
        self.screen_list[3].set_text(self.profiles[3]["LANG"][language] + str(on_off))

    def ok(self):
        publish("load_screen", {"screen": "location_screen", "init": False})

    def back(self):
        publish("load_screen", {"screen": "menu_screen", "init": False})

    def deactivate(self):
        self.timer.stop()


class OTAWriteNumScreen(TextScreen):
    NAME = "ota_write_num_screen"

    def __init__(self):
        super().__init__()
        self.comp = ota_info_screen
        self.timer = OSTIMER("OTAWriteNum")
        self.profiles = [
            {"LANG": {"CN": "账号:", "EN": "Account: "}},
            {"LANG": {"CN": "IP: ", "EN": "IP: "}},
            {"LANG": {"CN": "状态: ", "EN": "status: "}},
            {"LANG": {"CN": "MEID: ", "EN": "MEID: "}}
        ]

    def post_processor_after_load(self, *args, **kwargs):
        pass

    def play_tts(self):
        # tts_msg = "系统信息" if publish("config_get", "language") == "CN" else "System message"
        tts_msg = "空中写号" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    # 系统页面内容
    def post_processor_after_instantiation(self):
        # 系统页面内容
        self.container = lv_obj(
            parent=self.get_comp(),
            pos=(0, 100),
            size=(800, 340),
            style=[(main_cont_bg_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.init_screen(35)

    def initialization(self, *args):
        self.play_tts()
        language = publish("config_get", "language")
        self.screen_list[0].set_text(self.profiles[0]["LANG"][language] + str(publish('config_get_account')))
        self.screen_list[1].set_text(self.profiles[1]["LANG"][language] + str(publish('config_get_ip')))
        if language == "CN":
            status = "模块就续!"
        else:
            status = "ready!"
        self.screen_list[2].set_text(self.profiles[2]["LANG"][language] + str(status))
        self.screen_list[3].set_text(self.profiles[3]["LANG"][language] + str(modem.getDevImei()[-7:]))
        _thread.start_new_thread(self.wait, ())

    def wait(self):
        import poc
        poc.get_account_info()
        language = publish("config_get", "language")
        if language == "CN":
            status = "写号成功!"
        else:
            status = "SUCCESS!"
        if language:
            self.screen_list[2].set_text(self.profiles[2]["LANG"][language] + str(status))
        publish('do_shutdown', 1)

    def ok(self):
        publish('do_shutdown', 1)


class SettingSysScreen(TextScreen):
    NAME = "system_screen"

    FOTA_ERROR_CODE = {
        1001: "FOTA_DOMAIN_NOT_EXIST",
        1002: "FOTA_DOMAIN_TIMEOUT",
        1003: "FOTA_DOMAIN_UNKNOWN",
        1004: "FOTA_SERVER_CONN_FAIL",
        1005: "FOTA_AUTH_FAILED",
        1006: "FOTA_FILE_NOT_EXIST",
        1007: "FOTA_FILE_SIZE_INVALID",
        1008: "FOTA_FILE_GET_ERR",
        1009: "FOTA_FILE_CHECK_ERR",
        1010: "FOTA_INTERNAL_ERR",
        1011: "FOTA_NOT_INPROGRESS",
        1012: "FOTA_NO_MEMORY",
        1013: "FOTA_FILE_SIZE_TOO_LARGE",
        1014: "FOTA_PARAM_SIZE_INVALID",
    }

    def __init__(self):
        super().__init__()
        self.comp = system_screen
        self.system_check_version_btn = None
        self.system_check_version_label = None
        self.system_screen_app_bar_label = system_screen_app_bar_label
        self.__btn_check = False
        self.__fota_url = "http://114.141.132.55/firmware/tyt_carinercom.pack"
        # self.__fota_url = "http://112.31.84.164:8300/QuecPython_ST/Ivy/EC600UCNLC_FOTA_0630_0703.pack"
        self.log = LogAdapter(self.__class__.__name__)
        self.__ota_timer = OSTIMER("222")
        self.__fota_queue = Queue()
        self.__ota_flag = 0
        self.__ota_res = 0
        self.profiles = [
            {"LANG": {"CN": "用户: ", "EN": "User: "}, "event": "about_get_user"},
            {"LANG": {"CN": "产品型号: ", "EN": "Product: "}, "event": "about_get_product"},
            {"LANG": {"CN": "当前版本: ", "EN": "Version: "}, "event": "about_get_sysversion"},
            {"LANG": {"CN": "IMEI: ", "EN": "IMEI: "}, "event": "about_get_imei"},
            {"LANG": {"CN": "ICCID: ", "EN": "ICCID: "}, "event": "about_get_iccid"},
            {"LANG": {"CN": "SN: ", "EN": "SN: "}, "event": "get_sn_num"},
            {"LANG": {"CN": "网络地址: ", "EN": "IPv4: "}, "event": "get_ip_addr"},
            {"LANG": {"CN": "模块型号: ", "EN": "Module "}, "event": "about_get_module"},
        ]

    def post_processor_after_instantiation(self):
        super(SettingSysScreen, self).post_processor_after_instantiation()
        # 检查更新
        self.system_check_version_btn = lv_btn(
            parent=self.container,
            pos=(600, 30),
            size=(180, 50),
            style=[(btn_style_blue, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )
        self.system_check_version_label = lv_label(
            parent=self.system_check_version_btn,
            pos=(0, 0),
            size=(180, 50),
            text=("检查更新"),
            long_mode=(lv.label.LONG.WRAP),
            # style_text_align=(lv.TEXT_ALIGN.CENTER, 0),
            style_text_align=(lv.TEXT_ALIGN.LEFT, 0),
            style=[(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)],
        )

    def play_tts(self):
        # tts_msg = "系统信息" if publish("config_get", "language") == "CN" else "System message"
        tts_msg = "系统信息" if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def initialization(self):
        self.load_start()
        self.__system_info_refresh()
        self.top_bottom_refresh_timer_start()
        self.load_end()

    def ok(self):
        if not self.__btn_check:
            self.__upgrade_btn_check()
            return
        if self.__btn_check:
            # tts_msg = "开始升级检测" if publish("config_get", "language") == "CN" else "Start upgrade detection"
            tts_msg = "开始升级检测" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            param = {"screen": self.get_comp(),
                     "msg": "正在升级..." if publish("config_get", "language") == "CN" else "Upgrading", "sleep_time": 15}
            publish("msg_box_popup_show", param)
            if self.__ota_flag == 0:
                create_thread(self.__device_upgrade, stack_size=0x2000)

    def back(self):
        publish("load_screen", {"screen": "setting_screen"})

    def down(self):
        self.__upgrade_btn_check()

    def up_long(self):
        publish("load_screen", {"screen": "ota_write_num_screen"})

    def up(self):
        self.__upgrade_btn_check()

    def __system_info_refresh(self):
        language = publish("config_get", "language")
        self.system_screen_app_bar_label.set_text("系统信息" if language == "CN" else "System")
        for i, label in enumerate(self.screen_list):
            label.set_text(self.profiles[i]["LANG"][language] + str(publish(self.profiles[i]["event"])))
        self.system_check_version_label.set_text("检查更新" if language == "CN" else "Upgrade")
        self.__btn_check = True
        self.__upgrade_btn_check()

    def __upgrade_btn_check(self):
        if self.__btn_check:
            self.__btn_check = False
            self.system_check_version_btn.set_style_border_color(lv.color_make(0xff, 0xff, 0xff),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
            self.system_check_version_label.add_style(black_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)
        else:
            self.__btn_check = True
            self.system_check_version_btn.set_style_border_color(lv.color_make(0x18, 0x95, 0xe2),
                                                                 lv.PART.MAIN | lv.STATE.DEFAULT)
            self.system_check_version_label.add_style(blue_30_font_style, lv.PART.MAIN | lv.STATE.DEFAULT)

    def __upgrade_process(self, args):
        language = publish("config_get", "language")
        self.log.debug("__upgrade_process args %s" % str(args))
        down_status = args[0]
        down_process = args[1]
        self.log.debug("upgrade status: %s, upgrade process: %s" % (down_status, down_process))
        if language == "CN":
            msg = ("正在升级中, 升级包下载进度 {} %".format(down_process))
        else:
            msg = ("Upgrading, and download progress {} %".format(down_process))
        if self.__ota_res == 0:
            tts_msg = ""
            param = {}
            if down_status in (0, 1):
                if down_process < 100:
                    param = {"screen": self.get_comp(), "msg": msg, "sleep_time": 10}
                else:

                    param = {"screen": self.get_comp(), "msg": msg,
                             "sleep_time": 10}
                    # tts_msg = "升级完成, 准备重启设备" if publish("config_get", "language") == "CN" else "The upgrade is complete, ready to restart the device"
                    tts_msg = "升级包下载完成" if publish("config_get", "language") == "CN" else ""
                    self.__fota_queue.put(True)
            elif down_status == 2:
                param = {"screen": self.get_comp(), "msg": msg, "sleep_time": 5}
                # tts_msg = "升级完成, 准备重启设备" if publish("config_get", "language") == "CN" else "The upgrade is complete, ready to restart the device"
                tts_msg = "升级包下载完成" if publish("config_get", "language") == "CN" else ""
                self.__fota_queue.put(True)
            else:
                if language == "CN":
                    err_msg = ("升级失败, 失败原因: %s" % self.FOTA_ERROR_CODE.get(down_process))
                else:
                    err_msg = ("upgrade status: %s, upgrade process: %s" % self.FOTA_ERROR_CODE.get(down_process))
                param = {"screen": self.get_comp(), "msg": err_msg, "sleep_time": 5}
                # tts_msg = "升级失败" if publish("config_get", "language") == "CN" else "Upgrade failed"
                tts_msg = "升级失败" if publish("config_get", "language") == "CN" else ""
                self.__fota_queue.put(False)
            publish("poc_tts_play", tts_msg)
            publish("msg_box_popup_show", param)

    def __device_upgrade(self):
        self.__ota_flag = 1
        self.__ota_res = 0
        _fota = fota()
        self.__ota_res = _fota.httpDownload(url1=self.__fota_url, callback=self.__upgrade_process)
        self.log.debug("_fota.httpDownload %s" % self.__ota_res)
        if self.__ota_res == 0:
            self.__ota_timer.start(600 * 1000, 0, self.__ota_timer_callback)
            fota_res = self.__fota_queue.get()
            self.__ota_timer.stop()
            if fota_res:
                utime.sleep(5)
                Power.powerRestart()
        else:
            param = {"screen": self.get_comp(),
                     "msg": "升级失败或当前设备已是最新版本无需升级" if publish("config_get", "language") == "CN" else "Upgrading Failed",
                     "sleep_time": 5}
            tts_msg = "升级失败或当前设备已是最新版本无需升级" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            publish("msg_box_popup_show", param)

            self.log.debug("gc.mem_alloc(): %s" % gc.mem_alloc())
            self.log.debug("gc.collect(): %s" % gc.collect())
            self.log.debug("gc.mem_alloc(): %s" % gc.mem_alloc())
        self.__ota_flag = 0

    def __ota_timer_callback(self, args):
        self.__fota_queue.put(False)


class SingleCallScreen(Screen):
    NAME = "SingleCallScreen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.comp = single_call_screen

    def post_processor_after_load(self, *args, **kwargs):
        pass

    def initialization(self):
        single_call_member_label.set_text(self.meta.get("info")[1])

    def back(self):
        publish("poc_calluser", 0)
        publish("load_screen", {"screen": "menu_screen"})

    def deactivate(self):
        publish("push_state_info")


class SOSScreen(Screen):
    NAME = "sos_screen"

    def __init__(self):
        super().__init__()
        self.log = LogAdapter(self.__class__.__name__)
        self.comp = sos_screen

    def initialization(self):
        sos_label.set_text(self.meta.get("info"))

    def back(self, *args, **kwargs):
        publish("start_sos")
        publish("load_screen", {"screen": "menu_screen"})


class Poc_Ui(object):

    def __init__(self, lcd):
        self.lv = lv
        self.lcd = lcd
        self.screen = None
        self.timer = OSTIMER("Poc_Ui")
        self.screens = {}
        self.msg_box_list = []
        self.__lcd_sleep_timer = OSTIMER("lcd_sleep")
        self.__speak_timer = OSTIMER("speak")
        self.__signal_call = 0
        self.__signal_call_time = 0
        self.loading_finish = False
        self.__signal_call_user = {}
        self.check_net_timer = OSTIMER("111")
        self.load_timer = OSTIMER("333")
        self.log = LogAdapter(self.__class__.__name__)

    def add_screen(self, screen):
        self.screens[screen.NAME] = screen
        return self

    def add_msg_box(self, msg_box):
        self.msg_box_list.append(msg_box)

    def post_processor_after_instantiation(self):
        subscribe("btn_ok", self.btn_manage)
        subscribe("btn_group", self.btn_manage)
        subscribe("btn_back", self.btn_manage)
        subscribe("btn_up", self.btn_manage)
        subscribe("btn_down", self.btn_manage)
        subscribe("btn_handle", self.btn_manage)
        subscribe("btn_ptt", self.btn_manage)
        subscribe("btn_opt", self.btn_manage)
        subscribe("btn_num_click", self.btn_manage)
        subscribe("btn_up_long", self.btn_manage)
        subscribe("group_btn_long", self.btn_manage)
        subscribe("load_screen", self.lv_load)
        subscribe("btn_sos_long", self.btn_manage)
        subscribe("poc_reduce_vol_event", self.btn_manage)
        subscribe("poc_add_vol_event", self.btn_manage)
        subscribe("screen_switch", self.screen_switch)
        subscribe("current_screen", self.current_screen)
        subscribe("lcd_state_manage", self.__lcd_state_manage)
        subscribe("start_signal_call", self.__start_signal_call)
        subscribe("stop_signal_call", self.__stop_signal_call)
        subscribe("signal_call_state", self.__signal_call_state)
        subscribe("do_shutdown", self.do_shutdown)
        subscribe("sim_switch_show", self.sim_switch_show)
        subscribe("sim_switching", self.sim_switching)
        subscribe("single_call_notify", self.single_call_notify)
        subscribe("sos_notify", self.sos_notify)
        subscribe("record_pa_ctrl", self.record_pa_ctrl)
        subscribe("speak_notify", self.speak_notify)

        # subscribe("poc_join_group", self.poc_join_group)
        for box in self.msg_box_list:
            box.post_processor_after_instantiation()
        for scr_name in self.screens.keys():
            self.screens[scr_name].post_processor_after_instantiation()

    def speak_notify(self, event, msg):
        if self.screen and self.screen.NAME == "sos_screen":
            self.screen.back()

    def record_pa_ctrl(self, event, msg):
        if self.screen and (self.screen == "history_screen" or self.screen == "location_screen"):
            if msg:
                self.timer.stop()
            else:
                self.start_timeout_redirect()

    def sos_notify(self, event, msg):
        if msg:
            publish("load_screen", {"screen": "sos_screen", "info": msg})
        else:
            publish("load_screen", {"screen": "menu_screen"})

    def poc_join_group(self, *args, **kwargs):
        if not self.screen:
            publish("load_screen", {"screen": "menu_screen"})

    def btn_manage(self, topic, msg):
        if not self.screen:
            return
        if topic == "btn_ptt" or topic == "btn_sos_long":
            self.__lcd_state_manage()
        else:
            if not self.__lcd_state_manage():
                return
        if topic == "btn_ok":
            self.__btn_ok_on()
        elif topic == "btn_back":
            publish("poc_stop_sos")
            self.__btn_back()
        elif topic == "btn_up_long":
            self.__btn_up_long()
        elif topic == "btn_num_click":
            self.__btn_num_click(topic, msg)
        elif topic == "btn_up":
            self.__btn_up()
        elif topic == "btn_down":
            self.__btn_down()
        elif topic == "btn_handle":
            self.__btn_handle(topic, msg)
        elif topic == "btn_ptt":
            publish("poc_stop_sos")
            self.__btn_ptt(mode=msg)
        elif topic == "btn_group":
            self.__btn_group(msg=msg)
        elif topic == "btn_sos_long":
            self.__btn_sos_long()
        elif topic == "group_btn_long":
            self.group_btn_long()
        elif topic == "poc_add_vol_event":
            self.poc_add_vol_event()
        elif topic == "poc_reduce_vol_event":
            self.poc_reduce_vol_event()
        self.filter_redirect()

    def filter_redirect(self, topic=""):
        if self.screen.NAME != "menu_screen" and self.loading_finish and (
                self.screen != "SingleCallScreen" and topic != "btn_ptt") and self.screen.NAME != "ota_write_num_screen" \
                and self.screen.NAME != "sos_screen" and self.screen.NAME != "location_screen":
            self.start_timeout_redirect()

    def __btn_group(self, topic=None, msg=None):
        if self.screen:
            publish("load_screen", {"screen": "group_screen", "init": True})

    def poc_add_vol_event(self, topic=None, msg=None):
        publish("msg_box_vol_add", self.screen)

    def poc_reduce_vol_event(self, topic=None, msg=None):
        publish("msg_box_vol_reduce", self.screen)

    def group_btn_long(self):
        publish("sim_slot_switch")
        tts_msg = "正在切卡中..." if publish("config_get", "language") == "CN" else ""
        publish("poc_tts_play", tts_msg)

    def __btn_sos_long(self, topic=None, msg=None):
        publish("start_sos")

    def __btn_num_click(self, topic, msg):
        if self.screen:
            self.screen.btn_num_click(msg)

    def start_timeout_redirect(self):
        self.timer.stop()
        self.timer.start(30000, 0, self.redirect)

    def single_call_notify(self, event, state):
        if self.screen:
            if self.screen.NAME == "SingleCallScreen":
                if state:
                    self.timer.stop()
                else:
                    self.start_timeout_redirect()

    def redirect(self, args):
        if self.screen.NAME != "menu_screen" and self.screen.NAME != "ota_write_num_screen":
            publish("load_screen", {"screen": "menu_screen"})

    def start(self):
        self.post_processor_after_instantiation()
        publish("poc_tts_ready")

    def finish(self):
        lcd_sleep_time = publish("config_get", "lock_screen_time")
        if lcd_sleep_time != -1:
            self.__lcd_sleep_timer_start()
        self.loading_finish = True
        self.poc_join_group()
        publish("push_state_info")
        publish("tts_play_group")

    def screen_switch(self, event, msg):
        if self.screen is not None and self.screen.NAME not in msg["filters"]:
            self.log.debug("screen_switch screen.NAME = {} filters = {}".format(self.screen.NAME, msg["filters"]))
            publish("load_screen", msg)

    def lv_load(self, event=None, msg=None):
        # 1. 找到跳转界面
        # 2. 传递上级信息
        # 3. 初始化界面  initialization
        if self.screens.get(msg["screen"]):
            if self.screen:
                if self.screen.NAME == "ota_write_num_screen":
                    return
            scr = self.screens.get(msg["screen"])
            if scr == self.screen:
                return
            self.load_timer.stop()
            scr.set_meta(msg)
            scr.post_processor_before_initialization()
            init_result = scr.initialization()
            if init_result is False:
                return
            if self.screen:
                self.screen.deactivate()
            self.screen = scr
            self.screen.post_processor_after_initialization()
            self.lv.img.cache_invalidate_src(None)
            self.lv.img.cache_set_size(8)
            self.lv.scr_load(self.screen.get_comp())
            self.load_timer.start(20, 0, self.screen_load)
            self.filter_redirect()

    def screen_load(self, *args):
        _thread.start_new_thread(self.screen.post_processor_after_load, ())

    def current_screen(self, event=None, msg=None):
        return self.screen.NAME if self.screen else ""

    def __btn_ok_on(self):
        # """ok 按下"""
        if self.screen.get_load():
            self.screen.ok()

    def __btn_back(self):
        if hasattr(self.screen, "back"):
            self.screen.back()

    def __btn_down(self):
        if self.screen.get_load():
            self.screen.down()

    def __btn_up(self):
        if self.screen.get_load():
            self.screen.up()

    def __btn_up_long(self):
        # print("btn_up_long...")
        if self.screen.get_load():
            self.screen.up_long()

    def __btn_handle(self, event=None, mode=None):
        if self.screen.get_load():
            if hasattr(self.screen, "btn_handle"):
                self.screen.btn_handle(mode)
            else:
                self.__execute_hot_key(mode)

    def __btn_ptt(self, event=None, mode=None):
        if publish("bluetooth_state") == 3:
            tts_msg = "已切换蓝牙模式" if publish("config_get", "language") == "CN" else ""
            publish("poc_tts_play", tts_msg)
            param = {"screen": self.screen.get_comp(), "msg": tts_msg, "sleep_time": 3}
            publish("msg_box_popup_show", param)
            return
        if self.screen.get_load():
            publish("hand_mic_ptt_callback", mode)

    def __execute_hot_key(self, args):
        hot_key_data = publish("config_get", "hot_key")
        hot_key_item = hot_key_data.get(str(args))
        mode = hot_key_item.get("mode")
        if mode:
            if mode == "load_screen":
                publish("load_screen", hot_key_item["value"])
            else:
                if hot_key_item["uid"] != -1:
                    self.__start_signal_call(usr_info=[hot_key_item["uid"], hot_key_item['name']])
                elif hot_key_item["gid"] != -1:
                    publish("poc_joingroup", hot_key_item["gid"])

    def __speak_timeout(self, args):
        self.__signal_call_time -= 1
        if self.__signal_call_time > 0:
            box_show_msg = "单呼用户%s中, 剩余时间 %s 秒" % (self.__signal_call_user["usr_name"], self.__signal_call_time)
            publish("msg_box_popup_reset", box_show_msg)
        else:
            self.__signal_call_time = 0
            self.__speak_timer.stop()
            publish("poc_speak", 0)
            self.__signal_call = 0
            box_show_msg = "单呼用户%s结束" % self.__signal_call_user["usr_name"]
            param = {"screen": self.screen.get_comp(), "msg": box_show_msg, "sleep_time": 3}
            publish("msg_box_popup_show", param)
            self.__signal_call_user = {}

    def __start_signal_call(self, event=None, usr_info=None):
        if not publish("config_single_call_enable"):
            box_show_msg = "无单呼权限"
            publish("poc_tts_play", box_show_msg.replace("单呼", "单[=dan1]呼"))
            return
        publish("poc_calluser", usr_info)
        if usr_info[0] != publish("poc_get_login_info")[1]:
            # publish("load_screen", {"screen": "SingleCallScreen", "info": usr_info})
            pass
        else:
            box_show_time = 2
            box_show_msg = "禁止单呼当前用户"
            param = {"screen": self.screen.get_comp(), "msg": box_show_msg, "sleep_time": box_show_time}
            publish("msg_box_popup_show", param)
            publish("poc_tts_play", box_show_msg.replace("单呼", "单[=dan1]呼"))

    def __stop_signal_call(self, event=None, msg=None):
        if self.__signal_call == 1:
            self.__signal_call_time = 0
            self.__speak_timeout(None)

    def __signal_call_state(self, event=None, msg=None):
        return self.__signal_call

    def __lcd_on(self):
        self.lcd.onoff(1)

    def __lcd_off(self):
        self.lcd.onoff(0)

    def __lcd_state(self):
        return self.lcd.state()

    def __auto_lcd_switch(self, *args):
        if self.__lcd_state():  # 未息屏状态，熄灭屏幕
            self.__lcd_off()

    def __lcd_sleep_timer_start(self, event=None, mode=None):
        # 开启息屏定时器
        lcd_sleep_time = publish("config_get", "lock_screen_time")
        if lcd_sleep_time == -1:
            self.__lcd_sleep_timer.stop()
            return
        self.__lcd_sleep_timer.start(lcd_sleep_time * 1000, 1, self.__auto_lcd_switch)

    def __lcd_sleep_timer_stop(self, event=None, mode=None):
        # """息屏"""
        self.__lcd_sleep_timer.stop()

    def __lcd_sleep_timer_restart(self, event=None, mode=None):
        # """重置息屏Timer"""
        self.__lcd_sleep_timer_stop()
        self.__lcd_sleep_timer_start()

    def __lcd_state_manage(self, event=None, mode=None):
        # """LCD 状态管理"""
        if self.__lcd_state():
            if publish("config_get", "lock_screen_time") == -1:
                self.__lcd_sleep_timer_stop()
                return True
            self.__lcd_sleep_timer_restart()
            return True
        else:
            self.__lcd_on()
            return False

    def sim_switching(self, event, msg):
        cn_info = "正在切卡中, 请稍后..."
        en_info = "Switch Sim Card...."
        if publish("config_get", "language") == "CN":
            box_show_msg = cn_info
            publish("poc_tts_play", cn_info)
        else:
            box_show_msg = en_info
        param = {"screen": self.screen.get_comp(), "msg": box_show_msg, "sleep_time": 15}
        publish("msg_box_popup_show", param)

    def sim_switch_show(self, event, msg):
        if self.screen:
            if msg:
                cn_info = "sim卡切卡成功"
                en_info = "SIM Switch Success"
                self.screen.success()
            else:
                cn_info = "sim卡切卡失败"
                en_info = "SIM Switch Failure"
                self.screen.fail()
            box_show_msg = cn_info if publish("config_get", "language") == "CN" else en_info
            param = {"screen": self.screen.get_comp(), "msg": box_show_msg, "sleep_time": 1}
            publish("msg_box_popup_show", param)
            if self.screen.NAME == "sim_screen" and msg:
                tts_msg = ("sim卡切卡成功") if publish("config_get", "language") == "CN" else ""
                publish("poc_tts_play", tts_msg)
            if self.screen.NAME == "sim_screen":
                self.screen.ok_radio()

    def do_shutdown(self, event, msg=None):
        lv.scr_load(shutdown_screen)
        if msg is None:
            if publish("config_get", "language") == "CN":
                text = "正在关机..."
                publish("poc_tts_play", text)
            else:
                text = "shutdown ..."
            shutdown_label.set_text(text)
        elif msg == 2:
            if publish("config_get", "language") == "CN":
                text = "正在恢复配置..."
                publish("poc_tts_play", text)
            else:
                text = "recovery config ..."
            shutdown_label.set_text(text)
        elif msg == 3:
            if publish("config_get", "language") == "CN":
                text = "正在恢复出厂..."
                publish("poc_tts_play", text)
            else:
                text = "recovery ..."
            shutdown_label.set_text(text)

        elif msg == 1:
            if publish("config_get", "language") == "CN":
                text = "即将重启..."
                publish("poc_tts_play", text)
            else:
                text = "restart ..."
            shutdown_label.set_text(text)

        _thread.start_new_thread(self.shutdown, (event, msg))

    def shutdown(self, event=None, msg=None):
        if msg is None:
            publish("store_config")
            utime.sleep(3)
            Power.powerDown()
        elif msg == 2:
            publish("do_restore_config")
            utime.sleep(3)
            Power.powerRestart()
        elif msg == 3:
            publish("do_recovery")
            utime.sleep(3)
            Power.powerRestart()
        elif msg == 1:
            publish("store_config")
            utime.sleep(3)
            Power.powerRestart()
