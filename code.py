benj = '010000110100101001010101'
print(''.join(chr(int('010000110100101001010101'[i:i+8], 2)) for i in range(0, len('010000110100101001010101'), 8)))

