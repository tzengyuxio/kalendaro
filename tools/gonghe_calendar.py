from jdcal import jd2gcal, jd2jcal
from skyfield.api import load

import constants

ts = load.timescale()

feature_days = [
    (constants.JD_0, 'Julian Day Origin'),
    (constants.JD_ZD0, '子輿日 Origin'),
    (constants.JD_ZD1, '子輿日, P1 Origin'),
    (constants.JD_GCal_0001_01_01, '格里曆 元年'),
    (constants.JD_JCal_0001_01_01, '儒略曆 元年'),
    (constants.JD_GCal_1978_03_04, '格里曆 生日'),
    (constants.JD_GHCal_0000_01_01, '共和曆 零年'),
    (constants.JD_GHCal_0001_01_01, '共和曆 元年')
]


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


if __name__ == "__main__":
    print_table(feature_days)
