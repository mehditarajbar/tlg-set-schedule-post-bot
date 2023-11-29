import telebot
from telebot import apihelper
from datetime import datetime
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler


bot = telebot.TeleBot("TOKEN")
proxy_url = 'PROXY_URL'
proxy_port = 2080  # PROXY_PORT
apihelper.proxy = {'https': f'socks5://{proxy_url}:{proxy_port}'}
data = {}


@bot.message_handler(commands=['add-post'])
def send_post(message):
    try:
        bot.reply_to(message, 'عنوان پست را وارد نمایید :')
        bot.register_next_step_handler(message, get_title)
    except Exception as e:
        bot.reply_to(message, 'ارتباط قطع شد دوباره تلاش کنید!')


def get_title(message):
    try:
        bot.reply_to(message, 'متن پست را وارد کنید :')
        data['title'] = message.text
        bot.register_next_step_handler(message, get_content)
    except Exception as e:
        bot.reply_to(message, 'ارتباط قطع شد دوباره تلاش کنید!')


def get_content(message):
    try:
        bot.reply_to(message, 'تاریخ را ارسال کنید  (Y-M-D H:M):')
        data['content'] = message.text
        bot.register_next_step_handler(message, set_schedule)
    except Exception as e:
        bot.reply_to(message, 'ارتباط قطع شد دوباره تلاش کنید!')


def set_schedule(message, time_checker=True):
    try:
        if time_checker:
            given_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
            if given_date < datetime.now():
                raise Exception("زمان انتخاب شده گذشته است!")
            else:
                data['set_schedule'] = given_date
        bot.reply_to(message, 'یوزرنیم کانال را وارد کنید:')
        bot.register_next_step_handler(message, set_chat_id)
    except Exception as e:
        bot.reply_to(message, e)
        get_content(message)


def set_chat_id(message):
    try:
        channel_username = message.text
        if 'https://t.me/' in channel_username:
            channel_username = message.text.replace('https://t.me/', '')
        channel_info = bot.get_chat(f'@{channel_username}')
        if channel_info:
            data['chat_id'] = channel_info.id
            data['setter'] = message
            bot.reply_to(message, 'پست تنظیم شد')
            save_data()
    except Exception as e:
        bot.reply_to(message, 'کانال یافت نشد!')
        set_schedule(message, False)


def save_data():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_scheduled_post, 'date', run_date=str(data['set_schedule']), args=[data])
        scheduler.start()
    except Exception as e:
        bot.reply_to(data['setter'], e)


def send_scheduled_post(data):
    try:
        bot.send_message(data['chat_id'], f'{data["title"]}\n\n {data["content"]}')
    except Exception as e:
        print(e)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('/add-post')
    itembtn2 = types.KeyboardButton('/remove-post')
    itembtn3 = types.KeyboardButton('/edit-post')
    itembtn4 = types.KeyboardButton('/publish-now')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    bot.reply_to(message, "Howdy, how are you doing?", reply_markup=markup)


bot.infinity_polling()
