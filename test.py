import telebot
from telebot import types
import requests
import re

bot = telebot.TeleBot("")

url = "https://wbxsearch.wildberries.ru/exactmatch/v2/common?query="
url1 = "https://wbxcatalog-ru.wildberries.ru/"
url2 ="/catalog?spp=11&stores=119261,122252,122256,117673,122258,122259,121631,122466,122467,122495,122496,122498,122590,122591,122592,123816,123817,123818,123820,123821,123822,124093,124094,124095,124096,124097,124098,124099,124100,124101,124583,124584,125238,125239,125240,132318,132320,132321,125611,135243,135238,133917,132871,132870,132869,132829,133084,133618,132994,133348,133347,132709,132597,132807,132291,132012,126674,126676,127466,126679,126680,127014,126675,126670,126667,125186,116433,119400,507,3158,117501,120602,6158,121709,120762,124731,1699,130744,2737,117986,1733,686,132043&locale=ru&lang=ru&page="
spisok = []
zapros1 = []
spisok_zap = {}
mes_pol =[]
User_Agent ={
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

@bot.message_handler(commands=['start'])
def privetstvie(message):
    bot.send_message(message.chat.id, "Узнайте, на каких позициях находится ваш товар в поиске Wildberries. Введите артикул и запрос который вас интересует, например:  3577001 Конструктор LEGO")

@bot.message_handler(content_types=['text'])
def zapros(message):
    zapros1.append((message.text).strip())
    spisok_zap.update({message.chat.id:zapros1[0]})
    obrabotka(message,0)

def proverka(message,x):
    if spisok[0].isnumeric() == True:
        bot.send_message(message.chat.id, "Неверный формат!")
        spisok.clear()
        zapros1.clear()
    elif spisok[1].isnumeric() == True:
        bot.send_message(message.chat.id, "Ответ получен,начинаю поиск...")
        osnova = url + spisok[0]
        response_get(osnova, message, osnova,x)
    else:
        bot.send_message(message.chat.id, "Неверный формат!")
        spisok.clear()
        zapros1.clear()

def obrabotka(message,x):
    zapros1[0] = re.sub(r' ', " , ", zapros1[0], count=1)
    spisok.append(re.sub(r'.* , ', '', zapros1[0]))
    spisok.append(re.sub(r', .*$', "", zapros1[0]))
    spisok.append(re.sub(r' ', "", spisok[1]))
    del spisok[1]
    zapros1.clear()
    proverka(message,x)

def response_get(url,message,osnova,x):
    response = requests.get(url, headers=User_Agent)
    if response.status_code == 200:
        parser(response, message,x)
    elif response.status_code == 504:
        response_get(osnova, message, osnova,x)
    else:
        bot.send_message(message.chat.id, "Ошибка! Ответ от сайта не получен,попробуйте ещё раз.")

def parser(response,message,x):
    soup = response.json()
    zapros = spisok[0]
    shard_key = (soup['shardKey'])
    query = (soup["query"])
    url_dest = url1 + shard_key + url2
    for i in range(1, 101):
        page=i
        url_dest1 = url_dest + str(i) + "&" + query + "&search=" + str(zapros)
        resp2 = requests.get(url_dest1, headers=User_Agent)
        soup2 = resp2.json()
        for g in range(0, 100):
            try:
                ar = ((((soup2['data'])['products'])[g])["id"])
            except IndexError:
                bot.send_message(message.chat.id, "❌ Артикул " + spisok[1] + " по запросу " + spisok[0] + " на первых 100 страницах не ранжируется.")
                spisok.clear()
                mes_pol.append(message)
                return None
            if spisok[1] == str(ar):
                if x == 1:
                    bot.send_message(message.chat.id,"Ваня пидор")
                markup = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton("Обновить", callback_data="obnovka")
                markup.add(button1)
                bot.send_message(message.chat.id, " Артикул " + spisok[1] + " по запросу " + spisok[0] + " на " + str(page) + " странице,на " + str(g+1) + " позиции.", reply_markup=markup)
                spisok.clear()
                mes_pol.append(message)
                return None
            elif g == 99 and page == 100:
                bot.send_message(message.chat.id, "❌ Артикул " + spisok[1] + " по запросу " + spisok[0] + " на первых 100 страницах не ранжируется.")
                spisok.clear()
                mes_pol.append(message)
                return None

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.message:
        if call.data == "obnovka":
            zapros1.append(spisok_zap[call.message.chat.id])
            message = mes_pol[0]
            mes_pol.clear()
            obrabotka(message,1)

bot.polling(none_stop = True, interval=0)
