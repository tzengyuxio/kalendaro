from math import floor, modf

from pytz import timezone

TZ_CST = timezone('Asia/Taipei')
TZ_GMT = timezone('Europe/London')

# 《天文年鑑2017》太陽年，190頁，臺北市立天文科學教育館，2017年 (2019 年鑑亦是)
tropical_year = 365.242190

# 《天文年鑑2017》朔望月，191頁，臺北市立天文科學教育館，2017年 (2019 年鑑亦是)
synodic_month = 29.530589

# 週期 cycle (未命名)
cycle_years = 4418
cycle_months = 54643
cycle_days = 1613640

# 儒略日, 儒略曆, 格里曆
JD_0 = 0
JD_GCal_0001_01_01 = 1721425.5
JD_JCal_0001_01_01 = 1721423.5
JD_GCal_1978_03_04 = 2443571.5

JDN_0 = 0
JDN_GCal_0001_01_01 = 1721426
JDN_JCal_0001_01_01 = 1721424
JDN_GCal_1978_03_04 = 2443572

# JDN = floor(JD+.5)
# JD  = ceil(JDN-.5) # 錯誤, 不能這樣反查

# 子輿日
JD_ZD0 = 613270.5  # 2226910.5 - 1613640
JD_ZD1 = 2226910.5  # 1384/12/21 (modern Gregorian calendar)
JD_ZD2 = 3840550.5  # 1384/12/21 (modern Gregorian calendar)

JDN_ZD0 = 613271  # 2226911 - 1613640
JDN_ZD1 = 2226911  # 1384/12/21 (modern Gregorian calendar)
JDN_ZD2 = 3840551  # 1384/12/21 (modern Gregorian calendar)

ZD_GHCal_0000_01_01 = 800609  # JD_GHCal_0000_01_01 - JD_ZD0
ZD_GHCal_0001_01_01 = 800974  # JD_GHCal_0001_01_01 - JD_ZD0

ZDN_GHCal_0000_01_01 = 800609  # JD_GHCal_0000_01_01 - JD_ZD0
ZDN_GHCal_0001_01_01 = 800974  # JD_GHCal_0001_01_01 - JD_ZD0

ZDN_JD0 = -613271

# 共和曆
large_leap_cycle_days = 128 * 365 + 31  # 46751
small_leap_cycle_days = 4 * 365 + 1  # 1461
days_of_months = [0, 30, 61, 91, 122, 152, 183, 213, 244, 274, 305, 335, 366]
days_of_years = [0, 365, 730, 1095, 1461]

JD_GHCal_0000_01_01 = 1413879.5
JD_GHCal_0001_01_01 = 1414244.5

JDN_GHCal_0000_01_01 = 1413880
JDN_GHCal_0001_01_01 = 1414245

# 萬年曆
# 萬年曆思路1: JD1 前後 4480年(128*35), 共和-2254至6706年, 合計 8961年
# 萬年曆思路2: 共和-1280(大約夏朝)至3840年, 合計 5121年, 2864(AD2022)往後1000年左右
JDN_WANIAN_START = 590624  # JD: 590523.5
JDN_WANIAN_END = 3863558  # JD: 3863557.5

# 干支
gan = '甲乙丙丁戊己庚辛壬癸'
zhi = '子丑寅卯辰巳午未申酉戌亥'


def ganzhi_name(n):
    return gan[n % 10] + zhi[n % 12]


def ganzhi_of_jd(jd):
    """
    0 = 甲子
    59 = 癸亥
    """
    return (int(floor(jd + .5)) - 11) % 60


# 星期
weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']


def weekday_of_jd(jd):
    """
    0 = Sunday
    1 = Monday
    6 = Saturday
    """
    return (int(floor(jd + .5)) + 1) % 7


# Converters

def jd2zd(jd):
    return jd - JD_ZD0


def zd2jd(zd):
    return zd + JD_ZD0


def jdn2zd(jd):
    return jd - JDN_ZD0


def jd2zd_parted(jd):
    zd = jd - JD_ZD0
    p, d = int(zd // cycle_days), zd % cycle_days
    return p, d


def tcal2zd_1(y, m, d, t=.0):
    days = (y - 1) * 365 + floor((y - 1) // 4) - floor((y - 1) // 128)
    days += days_of_months[m - 1]
    days += d
    days += (ZD_GHCal_0001_01_01 - 1)
    return days + t


def tcal2zd_2(y, m, d, t=0):
    # 以 (-2191, 1, 1, ZD=364) 為參考起始點 (-2191 為閏年)
    # 並利用 -2303年 來作為計算 128 年循環 (-2304 為不閏年)
    """ step by step 逼近法
    method 2: 0.079415 s (100,000 次)
    method 4: 0.054687 s, 68.86%
    """
    days = floor((y + 2191) * 365.25) - floor((y + 2303) / 128.0) + \
           floor((m - 1) * 30.5001) + d + 363
    return days + t


def zd2tcal_1(zd):  # method 1
    num_padding_cycle = 0
    ed = zd - (ZD_GHCal_0001_01_01 - 1)  # ed = (p * period_days + d) - (gh_y1_zd - 1)
    while ed < 0:
        ed += large_leap_cycle_days
        num_padding_cycle += 1
    q1, r1 = ed // large_leap_cycle_days, ed % large_leap_cycle_days
    if r1 == 0:
        q1, r1 = q1 - 1, large_leap_cycle_days
    q2, r2 = r1 // small_leap_cycle_days, r1 % small_leap_cycle_days
    if r2 == 0:
        q2, r2 = q2 - 1, small_leap_cycle_days
    yy = 1 + 128 * q1 + 4 * q2 + (r2 // 365) - (128 * num_padding_cycle)
    diny = r2 % 365  # days in year
    mm, dt = 0, 0
    for i in range(13):
        if diny <= days_of_months[i]:
            dt = diny - days_of_months[i - 1]
            break
        mm += 1
    dd, tt = int(dt // 1), dt % 1
    return int(yy), mm, dd, tt


def zd2tcal_2(zd):  # method 2 [ok]
    padding_cycles = 0
    ed = zd - (ZD_GHCal_0001_01_01 - 1)  # ed = (p * period_days + d) - (gh_y1_zd - 1)
    yy, mm, dd, tt = 0, 0, 0, 0.0
    while ed <= 0:
        ed += large_leap_cycle_days
        padding_cycles += 1
    while ed > large_leap_cycle_days:
        ed -= large_leap_cycle_days
        yy += 128
    while ed > small_leap_cycle_days:
        ed -= small_leap_cycle_days
        yy += 4
    for i in range(5):
        if ed <= days_of_years[i]:
            yy += i
            ed = ed - days_of_years[i - 1]
            break
    yy -= 128 * padding_cycles
    for i in range(13):
        if ed <= days_of_months[i]:
            mm = i
            ed = ed - days_of_months[i - 1]
            break
    dd, tt = int(ed // 1), (ed % 1)
    return yy, mm, dd, float(tt)


def zd2tcal_3(zd):  # method 3
    # padding_cycles = 0
    # ed = (p * cycle_days + d) - (gh_y1_zd)
    ed = zd - ZD_GHCal_0001_01_01
    ed, tt = int(ed // 1), (ed % 1)
    # while ed <= 0:
    #     ed += large_leap_cycle_days
    #     padding_cycles += 1
    alpha = floor(ed / 46751.0)  # 大週期數
    A = ed + 1 + alpha - floor(alpha / 4.0)  # 日數加上週期數調整
    C = floor(A / 365.25)
    ed = ed - floor(A * 365.25)
    B = floor(ed / 30.6001)
    dd = ed - floor(B * 30.6001) - 1
    # yy = A - (padding_cycles*128) + 1
    yy = A + 1
    mm = B + 1
    return yy, mm, int(dd), tt


def zd2tcal_4(zd):  # method 4, base on method 2
    """ step by step 逼近法
    method 2: 0.513753 s (100,000 次)
    method 4: 0.491170 s, 95.6%
    """
    ed = zd - (ZD_GHCal_0001_01_01 - 1)  # ed = (p * period_days + d) - (gh_y1_zd - 1)
    yy, mm, dd, tt = 1, 1, 1, 0.0
    while ed <= 0:
        ed += large_leap_cycle_days
        yy -= 128
    while ed > large_leap_cycle_days:
        ed -= large_leap_cycle_days
        yy += 128
    while ed > small_leap_cycle_days:
        ed -= small_leap_cycle_days
        yy += 4
    for year_days in [365, 365, 365, 366]:
        if ed > year_days:
            ed -= year_days
            yy += 1
        else:
            break
    for month_days in [30, 31, 30, 31, 30, 31, 30, 31, 30, 31, 30, 31]:
        if ed > month_days:
            ed -= month_days
            mm += 1
        else:
            break
    tt, dd = modf(ed)
    return yy, mm, int(dd), tt


def find_fraction(num_float, min_denominator, max_denominator):
    """
    尋找分數表示式
    :param num_float: 實際數值
    :param min_denominator: 最小分母
    :param max_denominator: 最大分母
    :return:
    """
    results = [(1, 1, num_float)]  # (分子, 分母, [誤差*分母])
    for denominator in range(min_denominator, max_denominator):
        top = num_float * denominator
        left_int = floor(top)
        right_int = left_int + 1
        left_delta, right_delta = top - left_int, right_int - top
        numerator, delta = (left_int, left_delta) if left_delta < right_delta else (right_int, right_delta)
        if delta < results[-1][2]:
            results.append((int(numerator), int(denominator), delta))
    print('target: {} ({} - {})'.format(num_float, min_denominator, max_denominator))
    for r in results:
        if r[0] == 0:
            continue
        v = r[0] / r[1]
        d = v - num_float
        op = '+' if d > 0 else '-'
        print('{0:>4d} /{1:>4d} | value: {2:.9f}, delta: {4:} {3:0.9f}'.format(r[0], r[1], v, abs(d), op))
