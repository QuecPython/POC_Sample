import math
import utime
from usr.common import LogAdapter
from sensor import GNSS

log = LogAdapter(__name__)

CRLF = "\r\n"


class CoordinateSystemConvert:
    EE = 0.00669342162296594323
    EARTH_RADIUS = 6378.137  # Approximate Earth Radius(km)

    def _transformLat(self, x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def _transformLon(self, x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(math.fabs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    def wgs84_to_gcj02(self, lon, lat):
        dLat = self._transformLat(lon - 105.0, lat - 35.0)
        dLon = self._transformLon(lon - 105.0, lat - 35.0)
        radLat = lat / 180.0 * math.pi
        utime.sleep_ms(20)
        magic = math.sin(radLat)
        magic = 1 - magic * magic * self.EE
        utime.sleep_ms(20)
        sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((self.EARTH_RADIUS * 1000 * (1 - self.EE)) / (magic * sqrtMagic) * math.pi)
        dLon = (dLon * 180.0) / (self.EARTH_RADIUS * 1000 / sqrtMagic * math.cos(radLat) * math.pi)
        utime.sleep_ms(20)
        lon02 = lon + dLon
        lat02 = lat + dLat

        return lon02, lat02


class NMEAParse:
    """This class is match and parse gps NEMA 0183"""

    def __init__(self):
        self.__gga_data = ""

    def set_gps_data(self, gps_data):
        self.__gga_data = gps_data

    @property
    def GxGGAData(self):
        return self.__gga_data

    @property
    def Stars(self):
        stars = ""
        _rmc = self.GxGGAData
        if _rmc:
            stars = _rmc[7]
        return stars

    @property
    def Latitude(self):
        lat = ""
        _rmc = self.GxGGAData
        if _rmc:
            lat = _rmc[2]
            lat = str(float(lat[:2]) + float(lat[2:]) / 60)
            lat = ("" if _rmc[3] == "N" else "-") + lat
        return lat, _rmc[3]

    @property
    def Longitude(self):
        lng = ""
        _rmc = self.GxGGAData
        if _rmc:
            lng = _rmc[4]
            lng = str(float(lng[:3]) + float(lng[3:]) / 60)
            lng = ("" if _rmc[5] == "E" else "-") + lng
        return lng, _rmc[5]

    @property
    def Altitude(self):
        _gga = self.GxGGAData
        alt = _gga[9] if _gga else ""
        return alt


class GNSSUtil:
    __RMC = 0
    __GGA = 1
    __GSV = 2
    __GSA = 3
    __VTG = 4
    __GLL = 5

    def __init__(self, wk2114, nmea=None, PowerPin=None, StandbyPin=None, BackupPin=None):
        self.__uart = wk2114
        # self.__uart.set_callback(2, self.__uart_retrieve_cb)
        self.__uart.slave_uart_init(2, 9600)
        self.__uart.slave_uart_disable(2)
        self.__gnss = GNSS()
        self.__nmea_parse = NMEAParse()

    def __uart_open(self):
        self.__uart.slave_uart_enable(2)

    def __uart_close(self):
        self.__uart.slave_uart_disable(2)


    def read(self, retry=30):
        # log.debug("GNSS read start")
        self.__uart_open()
        gga_data = None
        while True:
            count = 0
            while True:
                to_read = self.__uart.any(2)
                # log.debug("uart any: %s" % to_read)
                if to_read > 0:
                    break
                count += 1
                if count >= 6:
                    break
                utime.sleep_ms(500)
            if to_read > 0:
                self.__gnss.parse(self.__uart.read(2, to_read).decode())
                gga_data = self.__gnss.getGGA()
                # print("GGA...", gga_data)
                # print("RMC...", self.__gnss.getRMC())
                if gga_data != -1:
                    break
                utime.sleep_ms(30)
            else:
                break
        self.__uart_close()
        return gga_data

    def data(self, retry=30):
        res = {}
        gps_data = self.read(retry)
        # print("--------read_gps_data", gps_data)
        if gps_data:
            self.__nmea_parse.set_gps_data(gps_data)
            try:
                res = {
                    "Latitude": self.__nmea_parse.Latitude[0],
                    "lat_direct": self.__nmea_parse.Latitude[1],
                    "Longitude": self.__nmea_parse.Longitude[0],
                    "lng_direct": self.__nmea_parse.Longitude[1],
                    "stars": self.__nmea_parse.Stars,
                }
            except Exception as e:
                # print("e ~~~", e, gps_data, self.__nmea_parse.GxGGAData)
                pass
        return res
