#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from math import modf

from skyfield import api
from skyfield.api import load

ts = load.timescale()
e = api.load('de422.bsp')
td = ts.utc(2019, 6, 26)  # 甲午日(30), 星期三
bd = ts.utc(1978, 3, 4)  # 乙丑日(1), 星期六


# tropical_year = 365.24219264  # Jacobs
# synodic_month = 29.5305888844  # Jacobs


def find_dzsd(t, cnt):
    t1 = t
    t0 = ts.tt_jd(t1.tt - 360)
    i = 0
    head = ['冬至JD', '冬至日', '新月JD', '新月日', '干支', '星期']
    print(','.join(head))
    while i < cnt:
        tws = find_winter_solstice(t0, t1)
        if tws != None:
            i += 1
            ganzhi = ganzhi_of_jd(tws.tt)
            id = 2019 - i
            if ganzhi in (59, 0) or id in [-3033, -3034, -3035]:
                tws0, tws1 = ts.tt_jd(tws.tt - 1), ts.tt_jd(tws.tt + 1)
                tnm = find_new_moon(tws0, tws1)
                if tnm != None:
                    # print(i, almanac.SEASON_EVENTS[3], tws.utc_iso(' '),)
                    # print(i, almanac.MOON_PHASES[0], tnm.utc_iso(' '),)
                    weekday = weekday_of_jd(tws.tt)
                    name_gz, name_wd = ganzhi_name(ganzhi), weekday_name(weekday)
                    delta = abs(tws.tt - tnm.tt)
                    dzsd = [tws.tt, tws.utc_iso(' '), tnm.tt, tnm.utc_iso(), name_gz, name_wd, delta]
                    print('[{7:4d}] {0:>6.9f},{1:>22s},{2:>6.9f},{3:>22s},{4},{5},{6:0.5f}'.format(*dzsd, id))
        t1 = t0
        t0 = ts.tt_jd(t1.tt - 360)


# 19年7閏, 391年144閏(大明曆)
special_year = [19, 76, 391, 4560]


def find_zhang(ylen, mlen, max_year=99999):
    min_err = 1
    max_err = 0
    min_err_with_ganzhi = 1
    max_err_with_ganzhi = 0
    for i in range(1, max_year):
        j = round(i * ylen / mlen)
        days_in_i_year = i * ylen
        days_in_j_month = j * mlen
        time_part_in_i_year, day_part_in_i_year = modf(days_in_i_year)
        time_part_in_j_month, day_part_in_j_month = modf(days_in_j_month)
        if int(day_part_in_i_year) != int(days_in_j_month) and i not in special_year:
            continue
        leap = j - i * 12
        days = int(day_part_in_i_year)
        err = min(time_part_in_i_year, time_part_in_j_month)
        meet_ganzhi = ((days + 1) % 60) == 0
        meet_week = ((days + 1) % 7) == 0
        if err > 0.916667 and not meet_ganzhi and i not in special_year:
            continue
        # if err >=  min_err and i not in special_year:
        #     continue
        if meet_ganzhi:
            if err < min(0.916667, max_err_with_ganzhi):
                continue
            max_err_with_ganzhi = err
        x1 = 'x' if meet_ganzhi else ' '
        x2 = 'x' if meet_week else ' '
        if not meet_ganzhi and i not in special_year:
            continue
        terr_year = str(datetime.timedelta(days=time_part_in_i_year))[:-7]
        terr_month = str(datetime.timedelta(days=time_part_in_j_month))[:-7]
        # print('{0:>5}年 {1:>7}月 {2:>5}閏 {3:>8}日 {4:>.6f}時 {7} [{5}], {6}'.format(i, j, leap, days, err, x, i % 128,
        #                                                                         terr))
        # min_err = err
        print('{0:>5}年 {1:>7}月 {2:>8}日 {3:>08}時(年) {4:>08}時(月) [{5}] [{6}]'.
              format(i, j, days + 1, terr_year, terr_month, x1, x2))


if __name__ == '__main__':
    find_dzsd(td, 6000)

    # t0 = ts.utc(2018,9,1)
    # t1 = ts.utc(2018,9,30)
    # t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))
    # for yi, ti in zip(y, t):
    #     print(yi, almanac.MOON_PHASES[yi], ti.utc_iso(' '))

    # ganzhi, weekday = ganzhi_of_jd(td.tt), weekday_of_jd(td.tt)
    # print(td.utc_iso(), ganzhi, weekday)
    # ganzhi, weekday = ganzhi_of_jd(bd.tt), weekday_of_jd(bd.tt)
    # print(bd.utc_iso(), ganzhi, weekday)

    # find_fraction(3.1415926, 1, 1000)
    # find_zhang(tropical_year, synodic_month)
