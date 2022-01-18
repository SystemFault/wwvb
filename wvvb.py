from machine import I2C, Pin
import usys
from ds1307 import DS1307


sleep_duration = .025
old = None
duration = 0
last_char = None
new_char = None
synced = False



class TimeSignal:
    def __init__(self, buff):
        self.dut = self.get_dut(buff)
        self.doy = self.get_day_of_year(buff)
        self.hours = self.get_hours(buff)
        self.minutes = self.get_minutes(buff)
        self.leap_year = self.get_leap_year(buff)

    def get_year(self, signal):
        """
        Year is communicated as 2 digits.  For 2018 we would receive 18.
        """
        year_tens = 10 * int("".join(signal[45:49]), 2)
        year_ones = int("".join(signal[50:54]), 2)
        return year_tens + year_ones

    def get_dut(self, signal):
        """
        Bits [36:38] (+ or -)
        Bits 40-43 (up to .9 seconds)
        DUT is the difference between UTC (Coordinated Universal Time) and UT1,
        which is the actual measurement of the Earth's rotation.
        """
        offset = .1 * int("".join(signal[40:44]), 2)
        if signal[36] == "1" and signal[38] == "1":
            pass
        elif signal[37] == "1":
            offset = offset * -1
        return offset

    def get_day_of_year(self, signal):
        """
        bits 22-23 (100, 200)
        bits 25-28 (10,20,40,80)
        bits 30-33 (1,2,4,8)
        """
        day_hundreds = 100 * int("".join(signal[22:24]), 2)
        day_tens = 10 * int("".join(signal[25:29]), 2)
        day_ones = int("".join(signal[30:34]), 2)
        return day_hundreds + day_tens + day_ones

    def get_hours(self, signal):
        hour_ten = 10 * int("".join(signal[12:14]), 2)
        hour_one = int("".join(signal[15:19]), 2)
        return hour_ten + hour_one

    def get_minutes(self, signal):
        min_ten = 10 * int('0b' + "".join(signal[1:4]), 2)
        min_one = int("".join(signal[5:9]), 2)
        return min_ten + min_one

    def get_leap_year(self, signal):
        if signal[55] == "1":
            return True
        else:
            return False

    def get_dst(self, signal):
        data = "".join(signal[57:59])
        if data == "00":
            print("\nNo DST")
        if data == "10":
            print("\nDST begins today")
        if data == "11":
            print("\nDST in effect")
        if data == "01":
            print("\nDST ends today")


def get_nmea():
    return "$GPZDA,{:02d}{:02d}{:02d}.00".format()


def calculate_date(doy, year, leap):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December"
    ]

    if leap:
        days_in_month[1] = 29

    i = 0
    while True:
        doy = doy - days_in_month[i]
        i += 1
        if doy - days_in_month[i] <= 0:
            break

    print('{} {}, 20{}'.format(months[i], doy, year))


def calculate_timestamp(signal):
    if len(signal) == 19:
        print('\n{:02d}:{:02d}:00'.format(
            get_hours(signal), get_minutes(signal)))
    if len(signal) == 34:
        print("\nDay of Year: " + str(get_day_of_year(signal)))
    if len(signal) == 44:
        print("\nDUT: " + str(get_dut(signal)))
    if len(signal) == 54:
        print("\nYear: " + str(get_year(signal)))
        calculate_date(
            get_day_of_year(signal), get_year(signal), get_dst(signal))
    if len(signal) == 60:
        get_dst(signal)


def process_time(diff, buf):
    global synced
    bit = calc_bit(diff)
    if len(buf) > 1:
        if buf[-1] == bit and bit == "M":
            # if len(buf) == 60:
            #     calculate_timestamp(buf)
            buf = [bit]
            synced = True
            print("\nSignal:\n", end="")
            sys.stdout.flush()

        else:
            buf.append(bit)
    else:
        buf.append(bit)
    if synced == True:
        calculate_timestamp(buf)
    else:
        print(".", end="")
        sys.stdout.flush()

    # print buf, len(buf)
    # print "."
    # print '{:02d}:{:02d}'.format(get_hours(buf), get_minutes(buf))
    return buf


#GPIO.add_event_detect(18, GPIO.FALLING, callback=falling, bouncetime=100)
# GPIO.add_event_detect(18, GPIO.RISING, callback=rising)
channel = 18
buf = []

print('Waiting for lock', end='')
sys.stdout.flush()

while True:
    res = GPIO.wait_for_edge(18, GPIO.RISING, timeout=5000)
    # print time.time()
    start = time.time()
    if res is None:
        print('Timeout Occured')
    else:
        # print('edge up', res)
        GPIO.wait_for_edge(channel, GPIO.FALLING)
        finish = time.time()
        buf = process_time(finish - start, buf)
