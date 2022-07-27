from datetime import timedelta
from math import modf, floor

from skyfield import almanac
from skyfield.api import load

import constants

# Ephemeris: 曆書, 星曆表。
# ref.: https://rhodesmill.org/skyfield/planets.html
# ephemeris = "de422.bsp"  # Issued in 2008, -3000 to 3000, 623 MB
# ephemeris = "de441.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
ephemeris = "de441_part-1.bsp"  # Issued in 2020, -13200 to 17191, 3.1 GB
# ephemeris = "kalendaro.bsp"  # Issued in 2020, -5000 to 3000, based on de441.bsp

eph = load(ephemeris)
ts = load.timescale()


def is_same_day(t0, t1, timezone=constants.TZ_GMT):
    y0, m0, d0, _, _, _ = t0.tt_calendar()
    y1, m1, d1, _, _, _ = t1.tt_calendar()
    return (y0 == y1) and (m0 == m1) # and (d0 == d1)


def ganzhi_of_jd(jd):
    return (int(floor(jd + .5)) - 11) % 60


def is_jiazi(t, delta):
    return True
    # return (ganzhi_of_jd_with_delta(t.tt, delta) == 0)


def find_winter_solstice(t0, t1):
    """
    尋找兩個時間點間的冬至
    :param t0:
    :param t1:
    :return:
    """
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    for yi, ti in zip(y, t):
        """
        0 春分 Vernal Equinox   / March Equinox
        1 夏至 Summer Solstice  / June Solstice
        2 秋分 Autumnal Equinox / September Equinox
        3 冬至 Winter Solstice  / December Solstice
        """
        if yi == 3:
            return ti
    return None


def find_new_moon(t0, t1):
    """
    尋找兩個時間點間的新月
    :param t0:
    :param t1:
    :return:
    """
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    for yi, ti in zip(y, t):
        """
        0 新月 New Moon
        1 上弦 First Quarter
        2 滿月 Full Moon
        3 下弦 Last Quarter
        """
        if yi == 0:
            return ti
    return None


def find_new_moon_winter_solstice(start_time, end_time, timezone=constants.TZ_GMT):
    """求朔旦冬至
    :param start_time:
    :param end_time:
    :param timezone:
    :return:
    """
    t, y = almanac.find_discrete(start_time, end_time, almanac.seasons(eph))
    for yi, ti in zip(y, t):
        if yi != 3:
            continue
        ti0, ti1 = ts.tt_jd(ti.tt - 1), ts.tt_jd(ti.tt + 1)
        tnm = find_new_moon(ti0, ti1)  # time new moon, 朔日
        if tnm is None:
            continue
        if not is_same_day(ti, tnm, timezone):
            continue
        if ganzhi_of_jd(ti.tt) != 0:
            continue
        y, m, d, _, _, _ = ti.tt_calendar()
        jd = ts.utc(y, m, d).tt
        print(y, m, d, jd, ti.utc, tnm.utc)
    #     results.append(jd)
    # return results

def find_3034(start_time, end_time):
    t, y = almanac.find_discrete(start_time, end_time, almanac.seasons(eph))
    for yi, ti in zip(y, t):
        if yi != 3:
            continue
        ti0, ti1 = ts.tt_jd(ti.tt - 3), ts.tt_jd(ti.tt + 3)
        tnm = find_new_moon(ti0, ti1)  # time new moon, 朔日
        if tnm is None:
            continue
        y, m, d, _, _, _ = ti.tt_calendar()
        jd = ts.utc(y, m, d).tt
        print(y, m, d, jd, ti.utc, tnm.utc)

def find_cycle(solar_len, lunar_len, max_year=7000):
    """求週期

    1歲 = 365¼日 (回歸年)
    1章 = 回歸年 與 朔望月 的最短循環週期
    1蔀 = 回歸年 與 朔望月 與 平太陽日 的最短循環週期
    1紀 = 1蔀 與 1甲子 之最短循環週期
    1元 = 1紀 與 12歲星紀年 之最短循環週期

    1統 = 81章 = 1539 年 = 朔旦冬至復在同一天的夜半 (三統曆)

    後漢書
    日月時歲章蔀紀元。1元3紀4560歲, 1紀20蔀1520歲, 1蔀4章76歲, 1章19歲

    max_year 的預設值：
        1. 西元前 約前5000年-前4000年：古埃及出現日曆。迄今約7000年。亦可倍求之。(倍求之, 合適的有 4418,8836,13254, 最合適還是 4418)
        2. 宋祖沖之《大明曆》上元甲子，至今五萬二千一百九十算外。 元法五十九萬二千三百六十五
        3. 西元前 3200年 左右：蘇美人發明楔形文字
    """
    # 1章19歲, 1蔀76歲, 391年144閏(大明曆,祖沖之), 1紀1520歲, 1統1539年, 1元4560歲
    special_years = [19, 76, 391, 1520, 1539, 4560]
    max_time_part = 0.5  # 最後一天至少要過半天
    print('回歸年數, 朔望月數, 太陽日數, 年循環最後一日餘時, 月循環最後一日餘時, 合甲子, 合七曜, 年循環太陽日數, 月循環太陽日數, 年循環月循環同日')
    for i in range(max_year):
        j = round(i * solar_len / lunar_len)
        solar_days, lunar_days = i * solar_len, j * lunar_len
        time_part_of_solar_days, day_part_of_solar_days = modf(solar_days)
        time_part_of_lunar_days, day_part_of_lunar_days = modf(lunar_days)
        if i not in special_years:
            if day_part_of_solar_days != day_part_of_lunar_days:
                continue
            time_part = min(time_part_of_solar_days, time_part_of_lunar_days)
            if time_part > max_time_part:
                max_time_part = time_part
            elif time_part < 0.916667:  # 22 小時之後
                continue
        days = int(solar_days) + 1
        check_jiazi = 'x' if (days % 60) == 0 else ' '
        check_week = 'x' if (days % 7) == 0 else ' '
        check_same_day = 'x' if day_part_of_solar_days == day_part_of_lunar_days else ' '
        time_part_solar = str(timedelta(days=time_part_of_solar_days))[:-7]
        time_part_lunar = str(timedelta(days=time_part_of_lunar_days))[:-7]
        print('{0:>5}年 {1:>6}月 {2:>7}日 {3:>08}時(年) {4:>08}時(月) [{5}] [{6}] {7:>15.6f} {8:>15.6f} [{9}]'.format(
            i, j, days, time_part_solar, time_part_lunar, check_jiazi, check_week, solar_days, lunar_days,
            check_same_day))


if __name__ == "__main__":
    # find_new_moon_winter_solstice()
    find_cycle(constants.tropical_year, constants.synodic_month, 20000)
    # 以下找不到合甲子的
    # find_period(tropical_year_jacobs, synodic_month_jacobs, 14000)

    print('\n\n----------------------------------------\n\n')

    t0 = ts.utc(-3200, 1, 1)
    t1 = ts.utc(1800, 12, 31)
    # t1 = ts.utc(2999, 12, 31)
    find_new_moon_winter_solstice(t0, t1)




    # find_3034(ts.utc(-3040, 1, 1), ts.utc(-3030, 1, 1))
    # -3039 12 19 611440.5004882407 CalendarTuple(year=-3039, month=12, day=19, hour=22, minute=59, second=19.840786174296227) CalendarTuple(year=-3039, month=12, day=19, hour=3, minute=9, second=13.946844205616799)
    # -3031 12 19 614362.5004882407 CalendarTuple(year=-3031, month=12, day=19, hour=21, minute=34, second=9.670948177932587) CalendarTuple(year=-3031, month=12, day=20, hour=10, minute=44, second=36.86352962291858)