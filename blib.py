import phpserialize
import pyotp
import time
import turbosmsua
import conf
import my_db_schema as sch
import pickle
import os

def save_dict(d, fn):
    with open(fn, 'wb') as f:
        pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)


def restore_dict(fn):
    obj = dict()
    if os.path.exists(fn):
        with open(fn, 'rb') as f:
            obj = pickle.load(f)
    return obj

class DictAutosave(dict):
    fn = ''
    def __init__(self, fn):
        self.fn = fn
        super().__init__()
        if os.path.exists(self.fn):
            with open(self.fn, 'rb') as f:
                obj = pickle.load(f)
                for i in obj:
                    print('restore:', i, obj[i])
                    super().__setitem__(i, obj[i])

    def __setitem__(self, k, v):
        print('set:', k, v)
        super().__setitem__(k, v)
        if self.fn != '':
            with open(self.fn, 'wb') as f:
                # pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self, f, 0)

    def __delitem__(self, k):
        print('del:', k)
        super().__delitem__(k)
        if self.fn != '':
            with open(self.fn, 'wb') as f:
                # pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self, f, 0)



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


