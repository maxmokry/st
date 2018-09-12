import phpserialize
import pyotp
import time
import turbosmsua
import conf
import my_db_schema as sch

def unserialize(str):
    return phpserialize.unserialize(bytes(str, 'utf-8'), decode_strings=True)


def send_pin(customer, info):
    mixed = unserialize(info.customers_mixed_info)
    res = None
    if mixed.get('2FA_way') == 'sms':
        password = str(time.time())[-4:]
        res = password
        t = turbosmsua.Turbosms(login=conf.TURBOSMS_LOGIN, password=conf.TURBOSMS_PASSWORD)
        text = 'Telegram Auth code: {}'.format(password)
        phone = customer.customers_telephone
        t.send_text(conf.TURBOSMS_SENDER, phone, text)
    elif mixed.get('2FA_way') == 'otp':
        res = mixed.get('2FAtoken')
    else:
        pass
    return res

def verify_pin(pin, saved, info):
    if info.get('2FA_way') == 'sms':
        if pin == saved:
            return True
        else:
            return False
    else:
        totp = pyotp.TOTP(saved, interval=60)
        if totp.verify(pin, valid_window=5) is True:
            return True
        else:
            return False

