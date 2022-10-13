import requests

data_url = 'https://script.google.com/macros/s/AKfycbwQu-PKvYhFIIrl3GOF3_8wdG0kdl-' \
           'RxXb7PbdwcVkejWGFJSzQKf0wUKRwUd9DDETq/exec'


def get_prev_kit_num(loc_id: str):
    if loc_id == 'RT':
        data_id = 'rapidlabel'
    else:
        loc_id = loc_id.zfill(3)
        data_id = 'pcrlabel_' + loc_id
    return requests.get(url=data_url, params={'id': data_id}).content.decode('ascii')


def mod10(code: str):
    n = 0
    for i in range(len(code)):
        if i % 2 == 1:
            n += int(code[i])
        else:
            if int(code[i]) * 2 < 10:
                n += int(code[i]) * 2
            else:
                n += int(str(int(code[i]) * 2)[0]) + int(str(int(code[i]) * 2)[1])
    if n % 10 == 0:
        return str(0)
    else:
        return str(10 - n % 10)


def next_kit_num(prev_kit_num):
    return str(int(prev_kit_num) + 1).zfill(6)


def make_barcode(loc_id: str, kit_num: str):
    if loc_id == 'RT':
        return loc_id + kit_num
    else:
        return loc_id + kit_num + mod10(loc_id + kit_num)


def update_db(loc_id: str, new_kit_num: str):
    if loc_id == 'RT':
        data_id = 'rapidlabel'
    else:
        data_id = 'pcrlabel_' + loc_id
    return requests.post(url=data_url, params={'id': data_id, 'value': new_kit_num})
