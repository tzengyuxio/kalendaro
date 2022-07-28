import datetime

from jdcal import jd2gcal, jd2jcal
from skyfield.api import load

import constants

ts = load.timescale()

feature_days = [
    (constants.JD_0, 'Julian Day Origin'),
    (constants.JD_ZD0, '子輿日 Origin'),
    (constants.JD_ZD1, '子輿日, P1 Origin'),  # 明太祖洪武17年11月1日, 星期二, [1]
    (constants.JD_GCal_0001_01_01, '格里曆 元年'),
    (constants.JD_JCal_0001_01_01, '儒略曆 元年'),
    (constants.JD_GCal_1978_03_04, '格里曆 生日'),
    (constants.JD_GHCal_0000_01_01, '共和曆 零年'),
    (constants.JD_GHCal_0001_01_01, '共和曆 元年'),
    (2353711.5, '華盛頓生日 (GC:1732-02-22; JC:1731-02-11(Old Style))')
]


# [1]: https://kanasimi.github.io/CeJS/_test%20suite/era.htm#era=明太祖洪武17年11月

def day_tuple_to_str(cal_date):
    y, m, d, _ = cal_date
    return '{:>6d}-{:>02d}-{:>02d}'.format(y, m, d)


def to_row(jd):
    zd = constants.jd2zd(jd)
    ganzhi = constants.ganzhi_name(constants.ganzhi_of_jd(jd))
    gh_cal = day_tuple_to_str(constants.zd2tcal_2(zd))
    g_cal = day_tuple_to_str(jd2gcal(0, jd))
    j_cal = day_tuple_to_str(jd2jcal(0, jd))
    week = constants.weekdays[constants.weekday_of_jd(jd)]
    return [jd, zd, gh_cal, g_cal, j_cal, ganzhi, week]


def print_table(days):
    print('| 儒略日 | 子輿日 | 共和曆 | 格里曆 | 儒略曆 | 干支 | 星期 | MEMO |')
    days.sort(key=lambda x: x[0])
    for d in days:
        jd, memo = d
        row = to_row(jd) + [memo]
        print('| {:>12.1f} | {:>12.1f} | {:12} | {:12} | {:12} | {} | {} | {:20} |'.format(*row))


def validate():
    # 已驗證: zd2tcal_2 與 zd2tcal_4 相等
    for zd in range(constants.ZD_GHCal_0001_01_01 - 1, constants.ZD_GHCal_0001_01_01 + 40):
        lval = constants.zd2tcal_2(zd)
        rval = constants.zd2tcal_3(zd)
        same = lval == rval
        if not same:
            print('{} {} {} {}'.format(zd, lval, rval, ' ' if same else 'x'))


def validate2():
    start = constants.ZD_GHCal_0001_01_01 - constants.large_leap_cycle_days * 2
    end = start + constants.cycle_days
    y, m, d, _ = constants.zd2tcal_4(start-1)
    print('start: {} ({})'.format(day_tuple_to_str(constants.zd2tcal_4(start)), datetime.datetime.now()))
    for zd in range(start, end):
        cal_day = constants.zd2tcal_4(zd)
        y, m, d = next_day(y, m, d)
        same = cal_day == (y, m, d, .0)
        if not same:
            print('{} {} {} {}'.format(zd, cal_day, (y, m, d), 'x'))
    print('end:   {} ({})'.format(day_tuple_to_str(constants.zd2tcal_4(end)), datetime.datetime.now()))


def next_day(y, m, d):
    yy, mm, dd = y, m, d + 1
    if d == 31 or (d == 30 and m in [1, 3, 5, 7, 9, 11]) or (d == 30 and m == 12 and (y % 4 != 0 or y % 128 == 0)):
        dd = 1
        mm += 1
    if mm == 13:
        mm = 1
        yy += 1
    return yy, mm, dd


if __name__ == "__main__":
    # print_table(feature_days)
    # validate()
    validate2()
    # TODO:
    #   翻書確定冬至日
    #   確定一些固定日期作為 test 用資料
    #   benchmark
    #   搞懂 method 2 的邏輯
