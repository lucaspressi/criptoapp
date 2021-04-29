import logging
import urllib.request
import json
import pandas as pd
import time
import schedule
import requests

logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

def get_data(symbol:str):
  url = "https://api.lunarcrush.com/v2?data=assets&key=5suihgh9hmho3a8tlk728&symbol={}".format(symbol)
  json_load = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
  actual = json_load['data'][0]
  del actual['timeSeries']
  df = pd.json_normalize(actual)
  return df

def data_generate(symbols):
  data = pd.DataFrame()
  for symbol in symbols:
    df = get_data(symbol)
    data = data.append(df)
  return data.sort_values(by='percent_change_24h', ascending=True)

def main():
    logging.info("Starting the main function...")
    cripto_info = data_generate(symbols=["BTC", "ETH", "DOGE","XRP", "BNB", "LTC", "LINK"])
    cripto_info.reset_index(level=0, inplace=True)

    message_list = ['Percentage Change 24h']
    cripto_info_pc24 = cripto_info.sort_values(by='percent_change_24h', ascending=True)
    cripto_info_pc24.reset_index(level=0, inplace=True)
    for i in range(len(cripto_info)):
      name = str(cripto_info_pc24['name'][i])
      percent_change_24h = str(cripto_info_pc24['percent_change_24h'][i])
      message_list.append('{}: {}%'.format(name, percent_change_24h))
    bot_message = '\n'.join(message_list)

    cripto_info_price = cripto_info.sort_values(by='price', ascending=False)
    cripto_info_price.reset_index(level=0, inplace=True)
    message_list.append('\nPrice')
    for i in range(len(cripto_info)):
      name = str(cripto_info_price['name'][i])
      price = str(cripto_info_price['price'][i])
      message_list.append('{}: {}USD'.format(name, price))
    bot_message = '\n'.join(message_list)

    if cripto_info_pc24['percent_change_24h'][0] < -4.0:
      bot_chatID = '1387270054'
      bot_token = '1755240951:AAHcC-WMs8IPOOYN4NlPoE2J90l8gws0PUQ'
      send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

      logging.info("Sending the message...")
      response = requests.get(send_text)
      return response.json()

    else:
      logging.info("Nothing interesting to send...")
      pass

schedule.every(90).minutes.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
