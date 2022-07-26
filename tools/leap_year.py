import constants


# 求最佳閏年循環
def find_best_leap_year_loop(max_year=1000):
    # delta 高於這個值就不考慮
    tolerance = abs(constants.tropical_year * 4 - round(constants.tropical_year * 4))
    # delta 高於這個值就納入清單
    precision = 0  # 1 / (4418*2)

    best_leap_i = (0, 0, 0, 1)  # i, j, avg, delta
    results = []
    for i in range(1, max_year + 1):
        best_leap_j = (0, 0, 1)  # j, avg, delta
        for j in range(1, i + 1):  # i 年 j 閏
            avg = ((i * 365) + j) / i
            delta = abs(avg - constants.tropical_year)
            if delta > min(best_leap_j[2], tolerance):
                continue
            best_leap_j = (j, avg, delta)

        avg, min_avg = best_leap_j[2], best_leap_i[3]
        if avg > tolerance:
            continue
        if avg > max(min_avg, precision) and i not in [100, 400, 900]:
            continue
        results.append([i, *best_leap_j])
        if avg < min_avg:
            best_leap_i = (i, *best_leap_j)
    for r in results:
        seconds = round(r[3] * 86400, 3)
        print('{0:>4}年{1:>3}閏, 年均太陽日: {2:0.6f}, 誤差: {3:0.6f} ({4:>7.3f}秒), {5:>6}年差一天'.
              format(*r, seconds, round(1 / r[3])))


if __name__ == "__main__":
    find_best_leap_year_loop()
