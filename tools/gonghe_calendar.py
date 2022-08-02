import datetime
from random import random

from jdcal import jd2gcal, jd2jcal
from skyfield import almanac
from skyfield.api import load
from skyfield.timelib import GREGORIAN_START

import constants

ts = load.timescale()
ts.julian_calendar_cutoff = GREGORIAN_START
ephemeris = "de422.bsp"  # Issued in 2008, -3000 to 3000, 623 MB
# ephemeris = "de441_part-1.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
# ephemeris = "de441_part-2.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
eph = load(ephemeris)

feature_days = [
    # NOTE: jd2gcal, jd2jcal 無法正確處理負數 JD
    # 12:00 Jan 1, 4713 BC (proleptic Julian calendar, via wiki)
    (constants.JDN_0, '儒略日起點', '西元前4713年（天文學記為-4712年）1月1日平午（世界時12:00）'),
    (constants.JDN_ZD0, '子輿日元點', ''),
    (constants.JDN_ZD0 - 2, '子輿日元點 歲首', ''),
    (613267, '子輿日元點 最近冬至', 'skyfield:(613266.78, -3033-01-13 06:46:14 UT1); 壽星天文曆:(613267, B3034年1月13日)'),
    (constants.JDN_ZD1, '明洪武 朔旦冬至甲子', '明太祖洪武17年11月1日, 星期二, [1]'),
    (constants.JDN_GCal_0001_01_01, '格里曆 元年', '西漢哀帝元壽2年11月20日'),
    (constants.JDN_JCal_0001_01_01, '儒略曆 元年 (公元)', '西漢哀帝元壽2年11月18日'),
    (1721415, '公元起點 附近冬至', '西漢哀帝元壽2年11月9日'),
    (constants.JDN_GCal_1978_03_04, '我的生日', ''),
    (constants.JDN_GHCal_0000_01_01, '共和曆 零年 (冬至)', '《三千五百年曆日天象表》900頁，前843年12月29日 10:48 (北京時); -842-12-21T09:14:46Z'),
    (constants.JDN_GHCal_0001_01_01, '共和曆 元年 (冬至)', '《三千五百年曆日天象表》900頁，前842年12月29日 16:37 (北京時); -841-12-21T15:05:04Z'),
    (constants.JDN_GHCal_0000_01_01 - 1, '共和曆 大除夕', ''),
    (constants.JDN_GHCal_0001_01_01 - 1, '共和曆 小除夕', ''),
    (1683429, '太初曆 天文冬至', '西漢武帝元封7年10月28日, 壬戌, GC:-104/12/20; JC:-105/12/23 [2]'),
    (1683430, '太初曆 天文朔', '西漢武帝元封7年10月29日'),
    (1683431, '太初曆 曆書朔旦冬至甲子', '西漢武帝元封7年11月01日, 甲子, GC:-104/12/22; JC:-105/12/25 [2]'),
    (1955170, '唐貞觀 天文朔冬至', '唐太宗貞觀14年閏10月30日, 癸亥, GC:640/12/21; JC:640/12/18 [2]'),
    (1955171, '唐貞觀 曆書朔旦冬至甲子', '唐太宗貞觀14年11月01日 (平朔戊寅元曆), 甲子, GC:640/12/22; JC:640/12/19 [2]'),
    (1393174, '天再旦於鄭', '前899年4月21日'),
    (1351919, '前1012年，烏加里特在5月9日出現日食', '[wiki:前1010年代]'),
    (1289081, '前1184年4月24日，傳統意義上認為的特洛伊陷落的日期', '[wiki:前1180年代]'),
    (172598, '埃及曆的開始(之一)', '19 July 4241 BC [wiki(en):5th millennium BC]'),
    (705863, '埃及曆的開始(之二)', '19 July 2781 BC [wiki(en):5th millennium BC]'),
    (259257, '地球的創造(根據Ussher年表)', '22/23 October 4004 BC [wiki(en):5th millennium BC]'),
    (1458496, '魯隱公三年二月己巳日日食', '《三千五百年曆日天象表》981頁，前720年02月22日 (BCE720-02-22)'),
    (2353712, '華盛頓生日', '(JC:1731-02-11(Old Style); GC:1732-02-22)'),
    (2000000, 'ユリウス暦763年9月14日', '[wiki(ja)]:ユリウス通日'),
    (1000000, 'ユリウス暦紀元前1976年11月7日', '[wiki(ja)]:ユリウス通日'),
    (2299160, 'ユリウス暦1582年10月4日', 'ローマ・カトリック教会におけるユリウス暦の最後の日 [wiki(ja)]:ユリウス通日'),
    (2299161, 'グレゴリオ暦1582年10月15日', 'ローマ・カトリック教会におけるグレゴリオ暦の初日 [wiki(ja)]:ユリウス通日'),
    (2450084, '1996年1月1日', '[wiki:儒略日起點] 的範例'),
    (2442404, '西元 1974 冬至 (1974-12-22)', ''),
    (2443865, '西元 1978 冬至 (1978-12-22)', ''),
    (2451545, '西元 2000 元旦 (2000-01-01)', ''),
    (2459936, '西元 2022 冬至 (2022-12-22)', ''),
    (2817143, '西元 3000 冬至 (3000-12-22)', ''),
    (3912870, '西元 6000 冬至 (6000-12-21)', ''),
    (4643353, '西元 8000 冬至 (8000-12-19)', ''),
    (5008595, '西元 9000 冬至 (9000-12-19)', ''),
    (5373471, '西元 9999 冬至 (9999-12-18)', ''),
    (5066300, '共和曆 9999年12月30日', ''),
    (5066301, '共和曆 10000年01月01日', '')
]


# 共和曆定義由零年開始（冬至時間較不靠近邊界）
# 天文計年(wiki): -n year = BC (n+1)
# [1]: https://kanasimi.github.io/CeJS/_test%20suite/era.htm#era=明太祖洪武17年11月
# [2]: 儒略日來源取自 紀年轉換工具 (連結同上)

def day_tuple_to_str(cal_date):
    y, m, d, _ = cal_date
    return '{:>6d}-{:>02d}-{:>02d}'.format(y, m, d)


def to_row(jdn):
    jd = jdn - .5
    jd = 0 if jd < 0 else jd
    zd = constants.jdn2zd(jdn)
    ganzhi = constants.ganzhi_name(constants.ganzhi_of_jd(jd))
    gh_cal = day_tuple_to_str(constants.zd2tcal_2(zd))
    j_cal = day_tuple_to_str(jd2jcal(0, jd))
    g_cal = day_tuple_to_str(jd2gcal(0, jd))
    ce_cal = ts.tt_jd(jd).tt_strftime(format='%Y-%m-%d')
    week = constants.weekdays[constants.weekday_of_jd(jd)]
    return [jdn, zd, ce_cal, gh_cal, j_cal, g_cal, ganzhi, week]


def print_table(days):
    print('| {:8} | {:8} | {:12} | {:9} | {:9} | {:9} | {} | {} | {:24} | {:24} |'.format(
        '儒略日數', '子輿日數', '西曆(公曆)', '共和曆', '儒略曆', '格里曆', '干支', '星期', '名稱', 'MEMO'
    ))
    days.sort(key=lambda x: x[0])
    for d in days:
        jdn, name, memo = d
        row = to_row(jdn) + [name, memo]
        print('| {:>10} | {:>10} | {:>15} | {:12} | {:12} | {:12} | {} | {} | {:24} | {:24} |'.format(*row))
    print()
    print('共 {} 筆曆日資料'.format(len(days)))


def validate():
    # 已驗證: zd2tcal_2 與 zd2tcal_4 相等
    for zd in range(constants.ZD_GHCal_0001_01_01 - 1, constants.ZD_GHCal_0001_01_01 + 40):
        lval = constants.zd2tcal_2(zd)
        rval = constants.zd2tcal_3(zd)
        same = lval == rval
        if not same:
            print('{} {} {} {}'.format(zd, lval, rval, ' ' if same else 'x'))


def validate2():
    # start = constants.ZD_GHCal_0001_01_01 - constants.large_leap_cycle_days * 2
    # end = start + constants.cycle_days
    start = constants.ZDN_JD0
    end = start + constants.cycle_days * 2
    y, m, d, _ = constants.zd2tcal_4(start - 1)
    start_cal = ts.tt_jd(constants.zd2jd(start)).tt_strftime(format='%Y-%m-%d')
    end_cal = ts.tt_jd(constants.zd2jd(end)).tt_strftime(format='%Y-%m-%d')
    print('start: {} | {} ({})'.format(
        start_cal, day_tuple_to_str(constants.zd2tcal_4(start)), datetime.datetime.now()))
    for zd in range(start, end):
        cal_day = constants.zd2tcal_4(zd)
        y, m, d = next_day(y, m, d)
        same = cal_day == (y, m, d, .0)
        if not same:
            print('Fail in Next(): {} {} {} {}'.format(zd, cal_day, (y, m, d), 'x'))
        rzd = constants.tcal2zd_2(y, m, d)
        if zd != rzd:
            print('Fail in Revs(): {} {} {} {}'.format(zd, cal_day, (y, m, d), 'x'))
    print('end:   {} | {} ({})'.format(
        end_cal, day_tuple_to_str(constants.zd2tcal_4(end)), datetime.datetime.now()))
    print('total days: {}'.format(end - start))


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
            fn(*zd)

    return F


def _time_analyze_(func):
    from time import process_time
    start = process_time()
    func()
    finish = process_time()
    print("{:<20}:{:10.6} s".format(func.__name__, finish - start))


def benchmark():
    zds = []
    tcals = []
    for i in range(100000):
        zd = random() * 1000000 - 500000
        zds.append(zd)
        tcals.append(constants.zd2tcal_4(zd))
    # setup = 'import constants'
    # t1 = timeit.timeit(stmt='for i in zds: constants.zd2tcal_2(i)'.format(zds), setup=setup)
    # t2 = timeit.timeit(stmt='constants.zd2tcal_4({})'.format(zds), setup=setup)
    # print(t1)
    # print(t2)
    _time_analyze_(run_test(constants.tcal2zd_1, tcals))
    _time_analyze_(run_test(constants.tcal2zd_2, tcals))
    # _time_analyze_(run_test(constants.zd2tcal_2, zds))
    # _time_analyze_(run_test(constants.zd2tcal_4, zds))


def year_to_ganzhi(year):
    return constants.ganzhi_name((year - 4) % 60)


def find_gonghe_origin():
    # start_time = ts.utc(-843, 1, 1)
    # end_time = ts.utc(-839, 12, 31)
    start_time = ts.utc(-3035, 1, 1)
    end_time = ts.utc(-3033, 12, 31)
    t, y = almanac.find_discrete(start_time, end_time, almanac.seasons(eph))
    # t, y = almanac.find_discrete(start_time, end_time, almanac.moon_phases(eph))
    for yi, ti in zip(y, t):
        if yi != 3:
            continue
        yy, _, _, _, _, _ = ti.tt_calendar()
        # print(ti.ut1, ti.utc_iso(), year_to_ganzhi(yy))
        print(ti.ut1, ti.ut1_strftime())


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
        print('|{:>16.4f} | {} | [{}]{:>16.4f} | [{}]{:>16.4f} |'.format(
            expected, date_str, match1, actual1, match2, actual2))


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
    #   [v] 思考 zd 的整數、小數位與日期關係
    #   [v] 搞清楚[紀年轉換工具]的[公元],[英國],[儒略曆],[格里曆]等欄位資訊
    #   [x] 增加 tcal2zd 在負數 ZD 的 test case
    #   [x] benchmark tcal2zd
    # MEMO:
    #   歲首問題：冬至, 春分, 立春, 月首首日
    # benchmark()
    # find_gonghe_origin()
    print('\n----------------------------------------\n')
    # check_convert(feature_days)

    # BUG:
    # 738-03-00? -> 修正後差一天
    # |    1683489.2 |    1070218.7 |    738-03-00 |   -103-02-21 |   -103-02-18 | 壬戌 | Thu | 西漢太初1年1月1日           |
    # |    1683489.2 |    1070218.7 |    738-02-31 |   -103-02-21 |   -103-02-18 | 壬戌 | Thu | 西漢太初1年1月1日           |
    #
    # 本表的儒略曆日, 年數與[紀年轉換工具]的[英國]年數相同，與[紀年轉換工具]的[儒略曆]年數相比多一。另外還要注意其[公元]欄位

    # ## 修 bug
    # zd1 = 1410000.0
    # zd2 = 1410000.3
    # zd3 = 1410000.99999999
    # print('zd1: {}'.format(day_tuple_to_str(constants.zd2tcal_4(zd1))))
    # print('zd2: {}'.format(day_tuple_to_str(constants.zd2tcal_4(zd2))))
    # print('zd3: {}'.format(day_tuple_to_str(constants.zd2tcal_4(zd3))))

    # ## JD, JDN 轉換測試
    # JDN = floor(JD+.5)
    # JD  = ceil(JDN-.5)
    # jd_list = [-1.5, -1.25, -1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1]
    # jdn_list = [-1, -1, -1, -1, 0, 0, 0, 0, 1, 1, 1]
    # int_list = [int(x-.5) for x in jdn_list]
    # floor_list = [floor(x-.5) for x in jdn_list]
    # ceil_list = [ceil(x-.5) for x in jdn_list]
    # print(jdn_list)
    # print(int_list)
    # print(floor_list)
    # print(ceil_list)

    # print(jd2jcal(0, 0))
    # print(jd2jcal(0, -0.7))
    # print(jd2gcal(0, 0))
    # print(-2.3 // 1, -2.3 % 1)

    # constants.find_fraction(constants.tropical_year, 1, 1000)
    # constants.find_fraction(constants.synodic_month, 1, 1000)
