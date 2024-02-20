from usr.EventMesh import publish

PROFILE = {
    "language_screen": {
        "CN": ["语言设置", "中文", "英文"],
        "EN": ["Language", "Chinese", "English"],
    },
    "hotkey_screen": {
        "CN": ["快捷键"],
        "EN": ["Hot Key"]
    },
    "bluetooth_screen": {
        "CN": ["蓝牙管理", "蓝牙开关"],
        "EN": ["Bluetooth", "ON-OFF"]
    },
    "call_time_screen": {
        "CN": ["单呼设置", "30秒", "60秒", "90秒", "120秒"],
        "EN": ["Call time", "30s", "60s", "90s", "120s"],
    },
    "screen_time_screen": {
        "CN": ["息屏时间", "常亮", "30秒", "60秒", "90秒", "120秒"],
        "EN": ["Screen off time", "Always on", "30s", "60s", "90s", "120s"],
    },
    "sim_screen": {
        "CN": ["SIM卡设置", "SIM 1", "SIM 2"],
        "EN": ["SIM", "SIM 1", "SIM 2"]
    },
    "setting_screen": {
        "CN": ["设置", "音量设置", "SIM卡设置", "息屏设置", "蓝牙管理", "快捷键", "语言设置", "系统信息", "降噪设置", "送话等级", "恢复出厂"],
        "EN": ["Setting", "Voice", "SIM", "Screen", "Bluetooth", "Hot Key", "Language", "System", "Noise",
               "Call Level", "Recovery"],
    },
    "weather_screen": {
        "CN": ["天气", "白天", "风向:", "夜晚", "风向:", "白天", "风向:", "夜晚", "风向:", "白天", "风向:", "夜晚", "风向:"],
        "EN": ["Weather", "Day", "Wind:", "Night", "Wind:", "Day", "Wind:", "Night", "Wind:", "Day", "Wind:", "Night",
               "Wind:"],
    },
    "history_screen": {
        "CN": ["历史消息"],
        "EN": ["History"],
    },
    "history_dir_screen": {
        "CN": ["历史文件"],
        "EN": ["History"],
    },
    "member_screen": {
        "CN": ["成员", {1: "离线", 2: "在线", 3: "在线在组"}],
        "EN": ["Member", {1: "Offline", 2: "Online", 3: "Online & In the group"}],
    },
    "friend_screen": {
        "CN": ["好友", {1: "离线", 2: "在线", 3: "在线在组"}],
        "EN": ["Friend", {1: "Offline", 2: "Online", 3: "Online & In the group"}],
    },
    "group_screen": {
        "CN": ["群组"],
        "EN": ["Group"],
    },
    "tbk_screen": {
        "CN": ["对讲", "群组", "成员", "好友", "历史消息"],
        "EN": ["Talking", "Group", "Member", "Friends", "History"],
    },
    "menu_screen": {
        "CN": ["对讲", "位置", "天气", "设置"],
        "EN": ["Talking", "Location", "Weather", "Setting"],
    },
    "noise_screen": {
        "CN": ["降噪管理", "降噪开关"],
        "EN": ["Noise", "ON-OFF"],
    },
    "call_level_screen": {
        "CN": ["送话等级", "送话等级+3", "送话等级+2", "送话等级+1", "送话等级+0", "送话等级-1", "送话等级-2", "送话等级-3"],
        "EN": ["Call Level", "Level +3", "Level +2", "Level +1", "Level +0", "Level -1", "Level -2", "Level -3"],
    },
    "recovery_screen": {
        "CN": ["恢复出厂"],
        "EN": ["recovery"],
    },
}


def init_location_profile():
    if not publish("config_gps_enable"):
        PROFILE['menu_screen']["CN"].pop(1)
        PROFILE['menu_screen']["EN"].pop(1)


init_location_profile()
