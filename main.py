import telebot
import requests

print("Введите токен:")
token = input()
bot = telebot.TeleBot(token)
url = "https://wbxsearch.wildberries.ru/exactmatch/v2/common?query="
url1 = "https://wbxcatalog-ru.wildberries.ru/"
url2 ="/catalog?spp=11&stores=119261,122252,122256,117673,122258,122259,121631,122466,122467,122495,122496,122498,122590,122591,122592,123816,123817,123818,123820,123821,123822,124093,124094,124095,124096,124097,124098,124099,124100,124101,124583,124584,125238,125239,125240,132318,132320,132321,125611,135243,135238,133917,132871,132870,132869,132829,133084,133618,132994,133348,133347,132709,132597,132807,132291,132012,126674,126676,127466,126679,126680,127014,126675,126670,126667,125186,116433,119400,507,3158,117501,120602,6158,121709,120762,124731,1699,130744,2737,117986,1733,686,132043&locale=ru&lang=ru&page="
spisok = []
User_Agent ={
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
}

@bot.message_handler(commands=['start'])
def privetstvie(message):
    bot.send_message(message.chat.id, "Введите запрос c помощью команды /z<запрос>:")

@bot.message_handler(commands=['z'])
def zapros(message):
    spisok.append((message.text[message.text.find(' '):]).strip())
    bot.send_message(message.chat.id, "Введите артикул с помощью команды /ar<артикул>:")

@bot.message_handler(commands=['ar'])
def articul(message):
    spisok.append((message.text[message.text.find(' '):]).strip())
    bot.send_message(message.chat.id, "Данные приняты,ожидайте...")
    osnova = url+spisok[0]
    response_get(osnova, message, osnova)

def response_get(url,message,osnova):
    response = requests.get(url, headers=User_Agent)
    if response.status_code == 200:
        bot.send_message(message.chat.id, "Ответ получен,начинаю поиск...")
        parser(response, message)
    elif response.status_code == 504:
        response_get(osnova, message, osnova)
    else:
        bot.send_message(message.chat.id, "Ошибка! Ответ от сайта не получен,попробуйте ещё раз.")

def parser(response,message):
    soup = response.json()
    zapros = spisok[0]
    shard_key = (soup['shardKey'])
    query = (soup["query"])
    url_dest = url1 + shard_key + url2
    for i in range(1, 101):
        page=i
        url_dest1 = url_dest + str(i) + "&" + query + "&search=" + zapros
        resp2 = requests.get(url_dest1, headers=User_Agent)
        soup2 = resp2.json()
        for g in range(0, 100):
            try:
                ar = ((((soup2['data'])['products'])[g])["id"])
            except IndexError:
                bot.send_message(message.chat.id, "Не удалось найти ваш товар :(")
                return None
            if spisok[1] == str(ar):
                bot.send_message(message.chat.id, "Выбранный вами товар находится на " + str(page) + " странице,на " + str(g+1) + " позиции.")
                spisok.clear()
                return None
            elif g == 99 and page == 100:
                bot.send_message(message.chat.id, "Не удалось найти ваш товар :(")
                spisok.clear()
                return None


bot.polling(none_stop = True, interval=0)
