# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm.exc import *
from sqlalchemy.sql import text

import my_db_schema as sch
from blib import unserialize, verify_pin, send_pin, restore_dict, save_dict
import conf


import logging

# add filemode="w" to overwrite
logging.basicConfig(level=logging.INFO)

# chats = DictAutosave('chats.pkl')
chats = restore_dict('chats.pkl')






updater = Updater(token=conf.TELEGRAM_TOKEN) # Токен API к Telegram
dispatcher = updater.dispatcher

#
# Обработка команд
def startCommand(bot, update):
    chats[update.message.chat_id] = {}
    text = '''Вас приветствует Seller-Online!
        
Для того, чтобы начать работу введите имя пользователя.
        
Вам не нужно вводить тут пароль. 
Авторизация осуществляется через дополнительный метод, который вы выбрали на сайте. 
Если дополнительная авторизация на сайте не включена, то услуги бота будут недоступны! 
'''
    bot.send_message(chat_id=update.message.chat_id, text=text)


def textMessage(bot, update):
    print(update)
    chat_id = update.message.chat_id
    if chat_id not in chats:
        startCommand(bot, update)
        return
    command = update.message.text.lower()
    if 'login' not in chats[chat_id]:
        print(chat_id)
        print(update)
        s = sch.session()
        login = str(update.message.text).lower()
        try:
            customer = s.query(sch.Customers).filter(sch.Customers.customers_login.ilike(login)).one()
            info = s.query(sch.CustomersInfo).filter(
                sch.CustomersInfo.customers_info_id == customer.customers_id).one()
            mixed = unserialize(info.customers_mixed_info)
            pin = send_pin(customer, info)
            print(111, pin)
            if pin is None:
                del chats[chat_id]
                bot.send_message(chat_id=chat_id, text='У вас не включена дополнительная авторизация.')
                return
            chats[chat_id]['login'] = login
            chats[chat_id]['pin'] = pin
            chats[chat_id]['customerid'] = customer.customers_id
            chats[chat_id]['mixed'] = mixed
            save_dict(chats, 'chats.pkl')
            response = 'Введите код подтверждения'
            bot.send_message(chat_id=chat_id, text=response)
            return
        except NoResultFound:
            bot.send_message(chat_id=chat_id, text='Ошибка в логине пользователя')
            return
    elif 'auth' not in chats[chat_id]:
        res = verify_pin(update.message.text,
                         chats[chat_id]['pin'],
                         chats[chat_id]['mixed'])
        if res is True:
            chats[chat_id]['auth'] = True
            save_dict(chats, 'chats.pkl')
            bot.send_message(chat_id=chat_id, text='Вы успешно авторизованы')
            return
        else:
            del chats[chat_id]
            save_dict(chats, 'chats.pkl')
            bot.send_message(chat_id=chat_id, text='неверный пароль')
            return

    if command == 'баланс':
        s = text('select customers_account, get_blocked_money(customers_id) from tbl_customers where customers_id = {}'
                 .format(chats[chat_id]['customerid']))
        print(sch.conn)
        print(s)
        b = sch.conn.execute(s)
        print(sch.conn)
        bal = b.first()
        print(bal)
        bb = float(bal.customers_account) - float(bal.get_blocked_money)
        print(bb)
        bot.send_message(chat_id=chat_id, text='Ваш баланс: {:.2f} USD'.format(bb))
        return
    elif command == 'выход' or command == 'exit':
        del chats[chat_id]
        save_dict(chats, 'chats.pkl')
        bot.send_message(chat_id=chat_id, text='Вы успешно вышли из системы')
        return
    else:
        help_text = '''**Неизвестная команда**
        
        __Команды бота:__
        Баланс - получить баланс
        Выход - выйти из системы
        '''
        bot.send_message(chat_id=chat_id, text=help_text)


    # response = 'Получил Ваше сообщение: ' + update.message.text
    # bot.send_message(chat_id=update.message.chat_id, text=response)


# Хендлеры
# start_command_handler = CommandHandler('start', startCommand)
text_message_handler = MessageHandler(Filters.text | Filters.command, textMessage)
# Добавляем хендлеры в диспетчер
# dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)
# Начинаем поиск обновлений
updater.start_polling(clean=True)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
