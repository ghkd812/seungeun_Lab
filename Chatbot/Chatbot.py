import telegram
import dateutil.parser as dparser
import datetime
import re

api_key = '969396288:AAG7Dc4sfu_mtnsqNPlGb7w7Xs_LT6OHCPE'

my_token = '969396288:AAG7Dc4sfu_mtnsqNPlGb7w7Xs_LT6OHCPE'

bot = telegram.Bot(token=api_key)

# chat_id = bot.get_updates()[-1].message.chat_id
# chat_id = 949061779
#
# bot.sendMessage(chat_id=chat_id, text='안녕하세요 스몰이 여행사입니다.')

# telegram.base.TelegramObject
#
# telegram.inlineKeyboardButton

# dparser.parse
#
# match = re.search(r'\d{4}-\d{2}-\d{2}', '2019-01-01')
# date = datetime.strptime(match.group(), '%Y-%m-%d').date()
#
# import datefinder
#
# input_string = "monkey 2010-07-10 love banana"
# # a generator will be returned by the datefinder module. I'm typecasting it to a list. Please read the note of caution provided at the bottom.
# matches = list(datefinder.find_dates(input_string))
#
# if len(matches) > 0:
#     # date returned will be a datetime.datetime object. here we are only using the first match.
#     date = matches[0]
#     print(date)
# else:
#     print ('No dates found')
#
# from pygrok import Grok
#
# input_string = 'monkey 2010-07-10 love banana'
# date_pattern = '%{YEAR:년}-%{MONTHNUM:월}-%{MONTHDAY:day}'
#
# grok = Grok(date_pattern)
# print(grok.match(input_string))
#
# matchObj = re.match(
#     r'(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d) (?P=year)\.(?P=month)\.(?P=day)',
#     '2018-07-28 2018.07.28', '2019년 1월 25일')
#
# print(matchObj.group())
# print(matchObj.groups())
# print(matchObj.group(1))