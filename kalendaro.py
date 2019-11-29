#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import modf, floor
from datetime import timedelta, datetime
from skyfield.api import load
from skyfield import almanac
from pytz import timezone
from jdcal import jd2gcal, jd2jcal

gan = '甲乙丙丁戊己庚辛壬癸'
zhi = '子丑寅卯辰巳午未申酉戌亥'
season_name_dict = {0: '春分', 1: '夏至', 2: '秋分', 3: '冬至'}
moon_phase_name_dict = {0: ' 朔 ', 1: '上弦', 2: ' 望 ', 3: '下弦'}

tropical_year = 365.242190  # 臺北市立天文科學教育館：《天文年鑑2019》，頁 374，太陽年。
synodic_month = 29.530589  # 臺北市立天文科學教育館：《天文年鑑2019》，頁 375，朔望月。

# http://www.jqjacobs.net/astro/astro.html
tropical_year_jacobs = 365.24219264  # Astronomical Constants Index, Code `YT`
synodic_month_jacobs = 29.5305888844  # Astronomical Constants Index, Code `S9`

ts = load.timescale()
td = ts.utc(2019, 11, 23)  # 甲子日(0), 星期六
bd = ts.utc(1978, 3, 4)  # 乙丑日(1), 星期六
tz_cst = timezone('Asia/Taipei')
tz_gmt = timezone('Europe/London')
# period 常數
period_years = 4418
period_months = 54643
period_days = 1613640
p0_orig_jd = 613270.5  # 第 0 紀首日 JD
p1_orig_jd = 2226910.5  # 第 1 紀首日 JD
gh_y0_jd = 1413879.5 # 共和零年冬至


def ganzhi_name(n):
    g = n % 10
    z = n % 12
    return gan[g]+zhi[z]


def find_winter_solstice(t0, t1, e):
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(e))
    for yi, ti in zip(y, t):
        """
        0 Vernal Equinox   / March Equinox
        1 Summer Solstice  / June Solstice
        2 Autumnal Equinox / September Equinox
        3 Winter Solstice  / December Solstice
        """
        if yi == 3:
            return ti
    return None


def find_new_moon(t0, t1, e):
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))
    for yi, ti in zip(y, t):
        """
        0 New Moon
        1 First Quarter
        2 Full Moon
        3 Last Quarter
        """
        if yi == 0:
            return ti
    return None


def find_period(solar_len, lunar_len, max_year=7000):
    """求週期

    1章 = 回歸年與朔望月之最短循環週期
    1蔀 = 1章 與 1日 之最短循環週期
    1紀 = 1蔀 與 1甲子 之最短循環週期
    1元 = 1紀 與 12歲星紀年 之最短循環週期

    1統 = 81章 = 1539 年 = 朔旦冬至復在同一天的夜半 (三統曆)

    max_year 的預設值：
        1. 西元前 約前5000年-前4000年：古埃及出現日曆。迄今約7000年。亦可倍求之。
        2. 宋祖沖之《大明曆》上元甲子，至今五萬二千一百九十算外。 元法五十九萬二千三百六十五
    """
    # 1章19歲, 1蔀76歲, 391年144閏(大明曆,祖沖之), 1紀1520歲, 1統1539年, 1元4560歲
    special_years = [19, 76, 391, 1520, 1539, 4560]
    max_time_part = 0
    print('回歸年數, 朔望月數, 太陽日數, 年循環最後一日餘時, 月循環最後一日餘時, 合甲子, 合七曜, 年循環太陽日數, 月循環太陽日數')
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
            elif time_part < 0.916667:
                continue
        days = int(solar_days) + 1
        check_jiazi = 'x' if (days % 60) == 0 else ' '
        check_week = 'x' if (days % 7) == 0 else ' '
        time_part_solar = str(timedelta(days=time_part_of_solar_days))[:-7]
        time_part_lunar = str(timedelta(days=time_part_of_lunar_days))[:-7]
        print('{0:>5}年 {1:>6}月 {2:>7}日 {3:>08}時(年) {4:>08}時(月) [{5}] [{6}] {7:>15.6f} {8:>15.6f}'.
              format(i, j, days, time_part_solar, time_part_lunar, check_jiazi, check_week, solar_days, lunar_days))


def find_best_leap_year_loop(solar_len, max_year=1024):
    # delta 高於這個值就不考慮
    tolerance = abs(tropical_year*4 - round(tropical_year*4))
    # delta 高於這個值就納入清單
    precision = 0  # 1 / (4418*2)
    best_leap_i = (0, 0, 0, 1)  # i, j, avg, delta
    results = []
    for i in range(1, max_year+1):
        best_leap_j = (0, 0, 1)  # j, avg, delta
        for j in range(1, i+1):  # i 年 j 閏
            avg = ((i * 365) + j) / i
            delta = abs(avg - tropical_year)
            if delta > min(best_leap_j[2], tolerance):
                continue
            best_leap_j = (j, avg, delta)
        if best_leap_j[2] > tolerance:
            continue
        if best_leap_j[2] > max(best_leap_i[3], precision) and i not in [100, 400]:
            continue
        results.append([i, *best_leap_j])
        if best_leap_j[2] < best_leap_i[3]:
            best_leap_i = (i, *best_leap_j)
    for r in results:
        print('{0:>4}年{1:>3}閏, 年均太陽日: {2:0.6f}, 誤差: {3:0.6f}, {4:>6}年差一天'.
              format(*r, round(1/r[3])))


def ganzhi_of_jd(jd):
    return (int(floor(jd + .5)) - 11) % 60


def ganzhi_of_jd_with_delta(jd, delta):
    return (int(floor(jd-delta + .5)) - 11) % 60


def is_same_day(t0, t1, timezone=tz_gmt):
    # 注意: datetime 的最小年份是 1
    dt0 = t0.astimezone(timezone)
    dt1 = t1.astimezone(timezone)
    return (dt0.year == dt1.year) and (dt0.month == dt1.month) and (dt0.day == dt1.day)


def is_jiazi(t, delta):
    return (ganzhi_of_jd_with_delta(t.tt, delta) == 0)


def delta_day_between_timezone(tz0, tz1):
    d0 = tz0.localize(datetime(2000, 1, 1))
    d1 = tz1.localize(datetime(2000, 1, 1))
    return ts.utc(d1) - ts.utc(d0)


def find_new_moon_winter_solstice_day(start_time, end_time, timezone=tz_gmt):
    e = load('de422.bsp')
    t, y = almanac.find_discrete(start_time, end_time, almanac.seasons(e))
    dd = delta_day_between_timezone(tz_gmt, timezone)
    results = []
    for yi, ti in zip(y, t):
        if yi != 3:
            continue
        ti0, ti1 = ts.tt_jd(ti.tt - 1), ts.tt_jd(ti.tt + 1)
        tnm = find_new_moon(ti0, ti1, e)  # 朔日
        if tnm is None:
            continue
        if not is_same_day(ti, tnm, timezone):
            continue
        if not is_jiazi(ti, dd):
            continue
        dt = ti.utc_datetime()
        y, m, d = dt.year, dt.month, dt.day
        jd = ts.utc(y, m, d).tt
        print(y, m, d, jd, ti.utc, tnm.utc)
        results.append(jd)
    return results


def find_period_origin():
    t0 = ts.utc(1380, 1, 1)
    t1 = ts.utc(1389, 12, 31)
    nmwsd = find_new_moon_winter_solstice_day(t0, t1)[0]
    period = round(4418 * tropical_year)
    prev_nmwsd = nmwsd - period
    print('第0紀 JD:', round(nmwsd, 1))
    print('第1紀 JD:', round(prev_nmwsd, 1))


def generate_seasons_table(t0, t1):
    if t0.tt < 625648.5:
        t0 = ts.tt_jd(625649)
    e = load('de422.bsp')
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(e))
    year_no = 0
    print('年序,分至,Season,JD,年,月,日,時,分,秒,子輿紀,子輿日,年干支')
    for yi, ti in zip(y, t):
        if yi == 3:
            year_no += 1
        season_name = season_name_dict[yi]
        dt = ti.tt_calendar()
        zyp, zyd = 0, ti.tt - p0_orig_jd
        if zyd > period_days:
            zyp, zyd = 1, ti.tt - p1_orig_jd
        ganzhi_order = (year_no+56) % 60
        print('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}'.
              format(year_no, season_name, yi, ti.tt, *dt, zyp, zyd, ganzhi_name(ganzhi_order), ganzhi_order+1))


def is_in_range(t, t0, t1):
    if t0 < t1:
        return (t0 <= t) and (t <= t1)
    else:
        return (t0 <= t <= 59) or (0 <= t <= t1)


def jinhou_su_bianzhong_kao():
    t0, t1 = ts.tt(-999, 1, 1), ts.tt(-771, 12, 31)
    results = []
    e = load('de422.bsp')
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(e))
    for yi, ti in zip(y, t):
        astro_key = 'S_{0}'.format(yi)
        season_name = season_name_dict[yi]
        dt = ti.tt_calendar()
        zyd = ti.tt - p0_orig_jd
        ganzhi_order = int(zyd) % 60
        ganzhi = ganzhi_name(ganzhi_order)
        results.append([astro_key, season_name, ti.tt,
                        *dt, zyd, ganzhi, ganzhi_order+1])
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))
    for yi, ti in zip(y, t):
        astro_key = 'M_{0}'.format(yi)
        moon_phase_name = moon_phase_name_dict[yi]
        dt = ti.tt_calendar()
        zyd = ti.tt - p0_orig_jd
        ganzhi_order = int(zyd) % 60
        ganzhi = ganzhi_name(ganzhi_order)
        results.append([astro_key, moon_phase_name, ti.tt,
                        *dt, zyd, ganzhi, ganzhi_order+1])
    results.sort(key=lambda x: x[-3])
    print('天象碼,天象,JD,年,月,日,時,分,秒,子輿日,日干支,日干支序')
    for r in results:
        print('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}'.format(*r))
    print('----------------')
    first_month_found = False
    years = {}  # year_index: months
    months = []  # [month_indexes, month_indexes, month_indexes...]
    month_indexes = []
    year_index = None
    for i, r in enumerate(results):
        if r[0] == 'M_0':
            month_indexes.append(i)
        elif r[0] == 'M_1':
            month_indexes.append(i)
        elif r[0] == 'M_2':
            month_indexes.append(i)
        elif r[0] == 'M_3':
            month_indexes.append(i)
            if first_month_found:
                if len(months) >= 12:
                    years[year_index] = months
                months = [month_indexes]
                first_month_found = False
            else:
                if len(month_indexes) == 4:
                    months.append(month_indexes)
            month_indexes = []
        elif r[0] == 'S_3':
            first_month_found = True
            year_index = i
    for year_index, months in years.items():
        year_key = results[year_index][3]
        print('{0}年({1})'.format(year_key, year_index))
        for i, month in enumerate(months):
            mp = results[month[0]]
            print(
                '    {0:>2}月,{1:4d}-{2:02d}-{3:02d},{4},{5},{6}'.format(i+1, *mp[3:6], *mp[-2:], mp[2]))
    print('----------------')
    for year_index, months in years.items():
        for i in range(3):
            jan_idx, feb_idx, mar_idx, _, _, jun_idx, jul_idx = months[i:i+7]
            jan = results[jan_idx[0]]
            feb = results[feb_idx[0]]
            mar = results[mar_idx[0]]
            jun = results[jun_idx[0]]
            jul = results[jul_idx[0]]
            jan_range = ((jan[-1]+59) % 60, feb[-1])
            feb_range = ((feb[-1]+59) % 60, mar[-1])
            jun_range = ((jun[-1]+59) % 60, jul[-1])
            if year_index == 8286 and i == 2:
                print(jan_range)
                print(feb_range)
                print(jun_range)
            # check jan, 55 is one-base
            if not is_in_range(55, *jan_range):
                continue
            # check feb, 39,40 is one-base
            if not is_in_range(39, *feb_range):
                continue
            if not is_in_range(40, *feb_range):
                continue
            # check jun, 15,24,27 is one-base
            if not is_in_range(15, *jun_range):
                continue
            if not is_in_range(24, *jun_range):
                continue
            if not is_in_range(27, *jun_range):
                continue
            print('{0}年{1}月,{2},{3},JD:{4}'.format(
                results[year_index][3], i+1, *jan[-2:], jan[2]))


if __name__ == "__main__":
    # 求紀元週期
    # find_period(tropical_year, synodic_month, 14000)
    # 以下找不到合甲子的
    # find_period(tropical_year_jacobs, synodic_month_jacobs, 14000)

    # 求最佳閏年循環
    # find_best_leap_year_loop(tropical_year)

    # 求朔旦冬至
    # t0 = ts.utc(1, 1, 1)
    # t1 = ts.utc(2999, 12, 31)
    # find_new_moon_winter_solstice_day(t0, t1)
    # print('----------------')
    # find_new_moon_winter_solstice_day(t0, t1, tz_cst)

    # 求紀元始日
    # find_period_origin()

    # 求分至表
    # t0 = ts.tt_jd(p0_orig_jd-1)
    # t1 = ts.tt(2929, 12, 31)
    # generate_seasons_table(t0, t1)

    # 晉侯酥編鐘考
    # jinhou_su_bianzhong_kao()
    print('儒略週期起點(GCal):', jd2gcal(0, 0))
    print('儒略週期起點(JCal):', jd2jcal(0, 0))
    print('子輿週期紀元(GCal):', jd2gcal(0, p0_orig_jd))
    print('子輿週期紀元(JCal):', jd2jcal(0, p0_orig_jd))
    print('共和零年冬至(GCal):', jd2gcal(0, gh_y0_jd))
    print('共和零年冬至(JCal):', jd2jcal(0, gh_y0_jd))
    print('朔旦冬至甲子(GCal):', jd2gcal(0, p1_orig_jd))
    print('朔旦冬至甲子(JCal):', jd2jcal(0, p1_orig_jd))

    # test
    # -*- ganzhi_of_jd()
    # print(ganzhi_name(ganzhi_of_jd(ts.now().tt))) # 2019-11-23, 甲子
    # print(ganzhi_name(ganzhi_of_jd(ts.utc(1910, 10, 10).tt))) # 戊申
    # print(ganzhi_name(ganzhi_of_jd(ts.utc(1912, 2, 18).tt))) # 甲子
    # -*- is_jiazi()
    # print(is_jiazi(ts.now())) # 2019-11-23, 甲子
    # print(is_jiazi(ts.utc(1910, 10, 10))) # 戊申
    # print(is_jiazi(ts.utc(1912, 2, 18))) # 甲子
    # -*- delta_day_between_timezone()
    # print(delta_day_between_timezone(tz_gmt, tz_cst))
    # print(delta_day_between_timezone(tz_gmt, tz_gmt))
    # -*- ganzhi_of_jd_with_timezone()
    # dd = delta_day_between_timezone(tz_gmt, tz_cst)
    # tt0 = ts.utc(2019, 11, 22, 21, 0, 0).tt  # UTC 21:00, CST 05:00(次日)
    # tt1 = ts.utc(2019, 11, 23, 8, 0, 0).tt  # UTC 08:00, CST 16:00
    # tt2 = ts.utc(2019, 11, 23, 17, 0, 0).tt  # UTC 17:00, CST 01:00(後一天)
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt0, 0))),  # 癸亥
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt0, dd)))  # 甲子
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt1, 0))),  # 甲子
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt1, dd)))  # 甲子
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt2, 0))),  # 甲子
    # print(ganzhi_name(ganzhi_of_jd_with_delta(tt2, dd)))  # 乙丑
