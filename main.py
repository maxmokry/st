# Настройки
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm.exc import *

import my_db_schema as sch
from blib import unserialize, verify_pin, send_pin









updater = Updater(token='616238756:AAF50TX6cvvjEwoX7WWXzJxfZOPkGcxfXz8') # Токен API к Telegram
dispatcher = updater.dispatcher

chats = dict()
#
# Обработка команд
def startCommand(bot, update):
    chats[update.message.chat_id] = {}
    text = '''Вас приветствует Seller-Online!
        
        Для того, чтобы начать работу введите имя пользователя.
        
        Вам не нужно вводить тут пароль. 
        Авторизация осуществляется через дополнительный метод, который вы выбрали на сайте. 
        Если дополнительная авторизация на сайте не включена, то услуши бота будут недоступны! 
    '''
    bot.send_message(chat_id=update.message.chat_id, text=text)


def textMessage(bot, update):
    chat_id = update.message.chat_id
    if chat_id not in chats:
        startCommand(bot, update)
        return
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
            response = 'Введите код подтверждения'
            bot.send_message(chat_id=chat_id, text=response)
        except NoResultFound:
            bot.send_message(chat_id=chat_id, text='Ошибка в логине пользователя')
    elif 'auth' not in chats[chat_id]:
        res = verify_pin(update.message.text,
                         chats[chat_id]['pin'],
                         chats[chat_id]['mixed'])
        if res is True:
            chats[chat_id]['auth'] = True
            bot.send_message(chat_id=chat_id, text='Вы успешно авторизованы')
        else:
            del chats[chat_id]
            bot.send_message(chat_id=chat_id, text='неверный пароль')
    command = update.message.text.lower()
    if command == 'баланс':
        pass
    elif command == 'выход' or command == 'exit':
        del chats[chat_id]
        bot.send_message(chat_id=chat_id, text='Вы успешно вышли из системы')
        return
    else:
        help_text = '''*Неизвестная команда*
        
        _Команды бота:_
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
