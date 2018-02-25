signal = list("M01100111M000100100M000000101M010100101M001000001M100000000MM")

#print signal

min_ten = 10 * int('0b' + "".join(signal[1:4]), 2)
#print min_ten
min_one = int("".join(signal[5:9]), 2)
hour_ten = 10 * int("".join(signal[12:14]), 2)
hour_one = int("".join(signal[15:19]), 2)

day_hundreds = 100 * int("".join(signal[22:24]), 2)
day_tens = 10 * int("".join(signal[25:29]), 2)
day_ones = int("".join(signal[30:34]), 2)
print day_hundreds + day_tens + day_ones

print str(hour_ten + hour_one) + ":" + str(min_ten + min_one)
# for i, val in enumerate(signal):
#     minutes = 0
#     if i > 1 or i < 10:
