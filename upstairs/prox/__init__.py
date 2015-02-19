def check_parity(code):
    if len(code) is not 35:
        return False
    bool_code = [int(x) for x in list(code)]
    return full_parity(bool_code) and odd_parity(bool_code) and even_parity(bool_code)

def full_parity(code):
    a = 0
    for b in code:
        a += b
    return bool(a % 2)

def even_parity(code):
    a = 0
    for bit in [x-1 for x in [2,3,4,6,7,9,10,12,13,15,16,18,19,21,22,24,25,27,28,30,31,33,34]]:
        a += code[bit]
    return not bool(a % 2)

def odd_parity(code):
    a = 0
    for bit in [x-1 for x in [2,3,5,6,8,9,11,12,14,15,17,18,20,21,23,24,26,27,29,30,32,33,35]]:
        a += code[bit]
    return bool(a % 2)
