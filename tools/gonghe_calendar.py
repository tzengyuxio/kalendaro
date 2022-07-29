import datetime
from random import random

from jdcal import jd2gcal, jd2jcal
from skyfield import almanac
from skyfield.api import load

import constants

ts = load.timescale()
ephemeris = "de441_part-1.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
# ephemeris = "de441_part-2.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
eph = load(ephemeris)

feature_days = [
    (constants.JD_0, 'Julian Day Origin'),  # 12:00 Jan 1, 4713 BC (proleptic Julian calendar, via wiki)
    (constants.JD_ZD0, '子輿日 Origin'),
    (constants.JD_ZD0 - 3, '最靠近子輿日紀元的冬至 (-3034-12-20)'),
    (constants.JD_ZD1, '明洪武 朔旦冬至甲子'),  # 明太祖洪武17年11月1日, 星期二, [1]
    (constants.JD_GCal_0001_01_01, '格里曆 元年'),
    (constants.JD_JCal_0001_01_01, '儒略曆 元年'),
    (constants.JD_GCal_1978_03_04, '格里曆 生日'),
    (constants.JD_GHCal_0000_01_01, '共和曆 零年'),  # 《三千五百年曆日天象表》900頁，前843年12月29日 10:48 (北京時); -842-12-21T09:14:46Z
    (constants.JD_GHCal_0001_01_01, '共和曆 元年'),  # 《三千五百年曆日天象表》900頁，前842年12月29日 16:37 (北京時); -841-12-21T15:05:04Z
    (2353711.5, '華盛頓生日 (JC:1731-02-11(Old Style); GC:1732-02-22)'),
    (1458495.5, '魯隱公三年二月己巳日日食 (BCE720-02-22)'),  # 《三千五百年曆日天象表》981頁，前720年02月22日
    (2442403.5, '1974 冬至 (1974-12-22)'),
    (2443864.5, '1978 冬至 (1978-12-22)'),
    (2451544.5, '2000 元旦 (2000-01-01)'),
    (2459935.5, '2022 冬至 (2022-12-22)'),
    (2817142.5, '3000 冬至 (3000-12-22)'),
    (3912869.5, '6000 冬至 (6000-12-21)'),
    (4643352.5, '8000 冬至 (8000-12-19)'),
    (5008594.5, '9000 冬至 (9000-12-19)'),
    (5373470.5, '9999 冬至 (9999-12-18)')
]


# 共和曆定義由零年開始（冬至時間較不靠近邊界）
# 天文計年(wiki): -n year = BC (n+1)
# [1]: https://kanasimi.github.io/CeJS/_test%20suite/era.htm#era=明太祖洪武17年11月

def day_tuple_to_str(cal_date):
    y, m, d, _ = cal_date
    return '{:>6d}-{:>02d}-{:>02d}'.format(y, m, d)


def to_row(jd):
    zd = constants.jd2zd(jd)
    ganzhi = constants.ganzhi_name(constants.ganzhi_of_jd(jd))
    gh_cal = day_tuple_to_str(constants.zd2tcal_2(zd))
    j_cal = day_tuple_to_str(jd2jcal(0, jd))
    g_cal = day_tuple_to_str(jd2gcal(0, jd))
    week = constants.weekdays[constants.weekday_of_jd(jd)]
    return [jd, zd, gh_cal, j_cal, g_cal, ganzhi, week]


def print_table(days):
    print('| 儒略日 | 子輿日 | 共和曆 | 儒略曆 | 格里曆 | 干支 | 星期 | MEMO |')
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
    y, m, d, _ = constants.zd2tcal_4(start - 1)
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


def run_test(fn, zdlist):
    def F():
        for zd in zdlist:
            fn(zd)

    return F


def _time_analyze_(func):
    from time import process_time
    start = process_time()
    func()
    finish = process_time()
    print("{:<20}:{:10.6} s".format(func.__name__, finish - start))


def benchmark():
    zds = []
    for i in range(100000):
        zds.append(random() * 1000000 - 500000)
    # setup = 'import constants'
    # t1 = timeit.timeit(stmt='for i in zds: constants.zd2tcal_2(i)'.format(zds), setup=setup)
    # t2 = timeit.timeit(stmt='constants.zd2tcal_4({})'.format(zds), setup=setup)
    # print(t1)
    # print(t2)
    _time_analyze_(run_test(constants.zd2tcal_2, zds))
    _time_analyze_(run_test(constants.zd2tcal_4, zds))


def year_to_ganzhi(year):
    return constants.ganzhi_name((year - 4) % 60)


def find_gonghe_origin():
    # start_time = ts.utc(-843, 1, 1)
    # end_time = ts.utc(-839, 12, 31)
    start_time = ts.utc(-3035, 1, 1)
    end_time = ts.utc(-3033, 12, 31)
    t, y = almanac.find_discrete(start_time, end_time, almanac.seasons(eph))
    for yi, ti in zip(y, t):
        if yi != 3:
            continue
        yy, _, _, _, _, _ = ti.tt_calendar()
        print(ti.utc_iso(), year_to_ganzhi(yy))


def check_convert(days):
    for d in days:
        jd, memo = d
        expected = constants.jd2zd(jd)
        yy, mm, dd, tt = constants.zd2tcal_4(expected)
        date_str = day_tuple_to_str((yy, mm, dd, tt))
        actual1 = constants.tcal2zd_1(yy, mm, dd, tt)
        actual2 = constants.tcal2zd_1(yy, mm, dd, tt)
        match1 = ' ' if actual1 == expected else 'x'
        match2 = ' ' if actual2 == expected else 'x'
        print('|{:>10} | {} | [{}]{:>10} | [{}]{:>10} |'.format(expected, date_str, match1, actual1, match2, actual2))


if __name__ == "__main__":
    print_table(feature_days)
    # validate()
    # validate2()
    # TODO:
    #   [x] 翻書確定冬至日
    #   [x] 確定一些固定日期作為 test 用資料
    #   [x] benchmark
    #   [x] 搞懂 method 2 的邏輯
    #   [x] tcal2zd
    #   [x] tcal2zd 對小數(時間)的處理
    #   [ ] 增加 tcal2zd 在負數 ZD 的 test case
    #   [ ] benchmark tcal2zd
    # MEMO:
    #   歲首問題：冬至, 春分, 立春, 月首首日
    # benchmark()
    # find_gonghe_origin()
    print('\n----------------------------------------\n')
    check_convert(feature_days)
