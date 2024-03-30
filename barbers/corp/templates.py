from datetime import date, time, datetime, timedelta


def phonenumber_to_show(value):
    if isinstance(value, int):
        value = str(value)
    if value.startswith('8') and len(value) == 11:
        phone = f'+7 ({value[1:4]}) {value[4:7]}-{value[7:9]}-{value[9:]}'
    elif value.startswith('+7') and len(value) == 12:
        phone = f'+7 ({value[2:5]}) {value[5:8]}-{value[8:10]}-{value[10:]}'
    elif len(value) == 10:
        phone = f'+7 ({value[:3]}) {value[3:6]}-{value[6:8]}-{value[8:]}'
    else:
        phone = ''
    return phone

def phonenumber_to_db(value):
    if isinstance(value, int):
        value = str(value)
    phone = value.replace(" ", "")

    if len(phone) < 10 or len(phone) > 12:
        return None

    if phone.startswith('+7') and len(phone) == 12:
        phone = phone[2:]
    elif phone.startswith('8') and len(phone) == 11:
        phone = phone[1:]

    if len(phone) == 10:
        return phone

    return None


value = 9610845144
phonenumber = phonenumber_to_show(value)
print(phonenumber)