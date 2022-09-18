from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from settings import *
import datetime
import ephem
from random import randint, choice
from glob import glob
import emoji


#Запись логов в файл 'bot.log'
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


def calc(update, context):
    args = context.args
    if len(args) < 3:
        update.message.reply_text("Некорректные входные данные!")
        raise ValueError

    if args[1] == "/" and args[2] == "0":
        update.message.reply_text("На ноль делить нельзя!")
        raise ZeroDivisionError




    if args[1] == "+":
        result = int(args[0]) + int(args[2])
        update.message.reply_text(result)
    elif args[1] == "-":
        result = int(args[0]) - int(args[2])
        update.message.reply_text(result)
    elif args[1] == "*":
        result = int(args[0]) * int(args[2])
        update.message.reply_text(result)
    elif args[1] == "/":
        result = int(args[0]) / int(args[2])
        update.message.reply_text(result)

    print(args)


#Функция создаёт пустой список городов, которые уже называли.
def restart_game(user_data):
    user_data['city'] = []


#Функция возвращает город, который начинается на последнюю букву предыдущего города.
def get_cityname(user_data):
    for cityname in cities_list:

        if cityname not in user_data and user_data[-1][-1].upper() == cityname[0]:
            user_data.append(cityname)
            return cityname


#Функция проверяет наличие города в общем списке и сриске уже названых городов.
def cityname_in_list(cityname, user_data):
    if cityname in cities_list and cityname not in user_data:
        if user_data == []:
            user_data.append(cityname)
            return True
        elif user_data[-1][-1] == cityname[0].lower():
            user_data.append(cityname)
            return True
    else:
        return False



#Функция впроверяет город по всем критериям и выводит подходящий, если такой есть в списке.
def cities(update, context):
    if context.user_data.get('city') == None:
        restart_game(context.user_data)
    cityname = context.args[0].capitalize()

    if cityname_in_list(cityname, context.user_data['city']):
        update.message.reply_text(f"Твой город - {cityname}")
        new_city = get_cityname(context.user_data['city'])
        update.message.reply_text(f"Мой город - {new_city}")
    else:
        update.message.reply_text("Город уже назывался или его нет в списке!")
    if len(context.user_data['city']) >= len(cities_list) - 1:
        restart_game(context.user_data)
    print(context.user_data['city'])


#Функция выводит дату следующего полнолуния.
def next_full_moon(update, context):
    try:
        date_dt = context.args[0]
        date_dt = ephem.next_full_moon(date_dt)
        update.message.reply_text(f'Ближайшее полнолуние: {date_dt}')
    except ValueError:
        update.message.reply_text("Некорректная дата!")


#Функция возвращает количество слов в фразе.
def word_counter(update, context):
    if context.args:
        words_len = len(context.args)
        update.message.reply_text(f"Количество слов: {words_len}")
    else:
        update.message.reply_text("Пустая строка!")


#Функция отправляет случайное фото кота.
def cat(update, context):
    cat_photos_list = glob('images/cat*.jp*g')
    cat_pic_filename = choice(cat_photos_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_pic_filename, 'rb'))


#Функция приветствует пользователя.
def start(update, context):
    username = update.effective_user.first_name
    update.message.reply_text(f"Привет, {username}!")


#Функция выводит созвездие, в котором находится планета в данный момент.
def planet(update, context):
    planetname = context.args[0]
    print(planetname)
    planet = getattr(ephem, planetname.capitalize())
    constellation = ephem.constellation(planet(datetime.datetime.now()))
    update.message.reply_text(constellation)


#Функция возвращает случайное число в пределах +-10 от пользовательского.
def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number + 10)
    if user_number > bot_number:
        message = f"Ваше число - {user_number}, моё - {bot_number}, вы выиграли!"
    elif user_number == bot_number:
        message = f"Ваше число - {user_number}, моё - {bot_number}, ничья!"
    else:
        message = f"Ваше число - {user_number}, моё - {bot_number}, вы проиграли!"
    return message


#Функция позволяет играть пользователю в числа.
def guess_number(update, context):
    print(context.args)
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except (TypeError, ValueError):
            message = "Введите целое число"
    update.message.reply_text(message)


def main():
    #Класс Updater постоянно слушает сервер Telegram, получает новые сообщения и передает их классу Dispatcher.

    bot = Updater(API_KEY)

    #Если создать объект Updater, то он автоматически создаст Dispatcher и свяжет их вместе с очередью.
    #Затем в объекте Dispatcher можно зарегистрировать обработчики разных типов, которые будут сортировать полученные объектом Updater сообщения.
    #Поступающие сообщения будут обрабатываться в соответствии с зарегистрированными обработчиками и передавать их в функцию обратного вызова, которую необходимо определить.

    dp = bot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("planet", planet))
    dp.add_handler(CommandHandler("guess", guess_number))
    dp.add_handler(CommandHandler("constellation", planet))
    dp.add_handler(CommandHandler("cat", cat))
    dp.add_handler(CommandHandler("wordcount", word_counter))
    dp.add_handler(CommandHandler("next_full_moon", next_full_moon))
    dp.add_handler(CommandHandler("cities", cities))
    dp.add_handler(CommandHandler("calc", calc))


    bot.start_polling()
    bot.idle()

if __name__ == "__main__":
    main()
