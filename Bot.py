import telebot
import sqlite3
import datetime
import time
import threading
import config
import requests
from bs4 import BeautifulSoup


def create_bd():
    try:
        conn = sqlite3.connect('mybd.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE coins (id int, name text, 
            price real(10), volume24 real(10), change24 real(10), cap real(10))''')
        conn.commit()
        conn.close()
    except:
        print('error create bd')


def start_check():
    create_bd()
    thread = threading.Thread(target=get_data, args=())
    thread.start()


def get_data():
    while True:
        print('updating bd...')
        conn = sqlite3.connect('mybd.db')
        c = conn.cursor()
        c.execute('''DELETE FROM coins''')
        for u in range(1,11):
            url = 'https://coinmarketcap.com/'
            url+=str(u)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'lxml')
            trs = soup.find('tbody')
            for i in range(100):
                tr=trs.find_all('tr')[i]
                tds = tr.find_all('td')
                id_coin = tds[0].text
                name = tds[1].text
                cap = tds[2].text[1:]
                price = tds[3].text[1:]
                price = price.replace(',','')
                volume = tds[4].text[1:]
                change = tds[6].text[:-1]
                c.execute("INSERT INTO coins VALUES (?,?,?,?,?,?)", (id_coin, name, price, volume, change, cap))
        conn.commit()
        conn.close()
        print('update finish')
        time.sleep(60*5)
        

def get_market_cap(user_id):
    answer=''
    conn = sqlite3.connect('mybd.db')
    c = conn.cursor()
    cursor = conn.execute("SELECT name, price, change24 FROM coins ORDER BY id ASC LIMIT 10")
    for row in cursor:
        data=(row[0])
        answer+='<b>{}:</b> цена ${}. изменения курса за сутки {}% \n'.format(row[0],row[1],row[2])
    bot.send_message(user_id,str(answer),parse_mode='HTML')

    conn.commit()
    conn.close()


def get_profitability(user_id):
    answer=''
    conn = sqlite3.connect('mybd.db')
    c = conn.cursor()
    cursor = conn.execute("SELECT name, price, change24 FROM coins ORDER BY change24 DESC LIMIT 10")
    for row in cursor:
        data=(row[0])
        answer+='<b>{}:</b> цена ${}. прибыльность за сутки <b>{}% </b> \n'.format(row[0],row[1],row[2])
    bot.send_message(user_id,str(answer),parse_mode='HTML')
    conn.commit()
    conn.close()


def get_lesion(user_id):
    answer=''
    conn = sqlite3.connect('mybd.db')
    c = conn.cursor()
    cursor = conn.execute("SELECT name, price, change24 FROM coins ORDER BY change24 ASC LIMIT 10")
    for row in cursor:
        data=(row[0])
        answer+='<b>{}:</b> цена ${}. убыточность за сутки <b>{}%</b> \n'.format(row[0],row[1],row[2])
    bot.send_message(user_id,str(answer),parse_mode='HTML')
    conn.commit()
    conn.close() 


def get_most_price(user_id):
    answer=' '
    conn = sqlite3.connect('mybd.db')
    c = conn.cursor()
    cursor = conn.execute("SELECT name, price FROM coins ORDER BY price DESC LIMIT 10")
    for row in cursor:
        data=(row[0])
        answer+='<b>{}:</b> цена ${}.\n'.format(row[0],row[1])
    bot.send_message(user_id,str(answer),parse_mode='HTML')
    conn.commit()
    conn.close()


bot = telebot.TeleBot(config.TOKEN)
start_check()


@bot.message_handler(commands=['start'])
def command_handler(message):
    user_markup=telebot.types.ReplyKeyboardMarkup(True,False)
    user_markup.row('Топ-10 по капитализации','10 самых дорогих монет')
    user_markup.row('Топ-10 по прибыльности за сутки', 'Топ-10 убыточности за сутки')
    bot.send_message(message.from_user.id,'Бот для мониторинга курса криптовалют',reply_markup=user_markup)


@bot.message_handler(commands=['help'])
def handle_text(message):
    bot.send_message(message.chat.id, 'В данном боте вы можете мониторить курсы криптовалют, и сортировать их по различным категориям.')


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text=='Топ-10 по капитализации':
        get_market_cap(message.chat.id)
    elif message.text=='Топ-10 по прибыльности за сутки':
        get_profitability(message.chat.id)
    elif message.text=='Топ-10 убыточности за сутки':
        get_lesion(message.chat.id)
    elif message.text=='10 самых дорогих монет':
        get_most_price(message.chat.id)


while True:
    try:
        time.sleep(1)
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(30)