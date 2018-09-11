import phpserialize
import pyotp
import time
import turbosmsua
import conf
import my_db_schema as sch

def unserialize(str):
    return phpserialize.unserialize(bytes(str, 'utf-8'), decode_strings=True)


def get_otp_key(token):
    totp = pyotp.TOTP(token, interval=60)
    return totp.now()

def get_customer_info():
    pass


def send_pin(customer, info):
    mixed = unserialize(info.customers_mixed_info)
    res = None
    print(1)
    if mixed.get('2FA_way') == 'sms':
        print(2)
        password = str(time.time())[-4:]
        res = password
        print(password)
        t = turbosmsua.Turbosms(login=conf.TURBOSMS_LOGIN, password=conf.TURBOSMS_PASSWORD)
        print(conf.TURBOSMS_LOGIN, conf.TURBOSMS_PASSWORD)
        # t = turbosmsua.Turbosms(login="selleronline", password="Deptij2OdfarbEi")
        print(3)
        text = 'Telegram Auth code: {}'.format(password)
        phone = customer.customers_telephone
        t.send_text(conf.TURBOSMS_SENDER, phone, text)
        print(4)
    elif mixed.get('2FA_way') == 'otp':
        res = mixed.get('2FAtoken')
    else:
        pass
    print(5)
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

