#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import modf, floor

tropical_year = 365.242190  # 臺北市立天文科學教育館：《天文年鑑2019》，頁 374，太陽年。
synodic_month = 29.530589  # 臺北市立天文科學教育館：《天文年鑑2019》，頁 375，朔望月。


def find_fraction(number, max_denominator, special_case = []):
    decimal_part, integer_part = modf(number)
    print('target: ', decimal_part, integer_part)
    min_e = 1
    for i in range(2, max_denominator):
        denominator = i
        numerator = denominator * decimal_part
        dp, _ = modf(numerator)
        if dp >= 0.5:
            numerator = floor(numerator) + 1
        else:
            numerator = floor(numerator)
        e = abs(numerator/denominator - decimal_part)
        if e < min_e:
            print('{0:4d}/{1:4d}, {2:0.8f}, {3:0.8f}'.format(numerator,
                                                             denominator,  numerator/denominator, e))
            min_e = e
        elif denominator in special_case:
            print('{0:4d}/{1:4d}, {2:0.8f}, {3:0.8f} [*]'.format(numerator,
                                                             denominator,  numerator/denominator, e))


if __name__ == "__main__":
    find_fraction(tropical_year, 10000, [2209]) # 365 with 752/3105
    # 2209: 天下曆
    find_fraction(synodic_month, 10000, [81,940]) # 29 with 3261/6146
    # 81: 太初曆, 940: 四分曆

    leap = tropical_year / synodic_month
    find_fraction(leap, 10000, [19])

    # LCM(3105,6146) = 19083330
    # LCM(3105,6146,60) = 38,166,660

    print(divmod(1613640,4418))  # (365, 1070)
    print(divmod(1613640,54643)) # (29, 28993)
    # 1070/4418   -> 535/2209
    # 28993/54643 -> 28993/54643

    # LCM(2209,850,60) = 11,265,900
