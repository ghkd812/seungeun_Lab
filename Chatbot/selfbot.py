##############################################################################################################################################################################################################
############################################### 2020년 3월 13일 다시 시작 전꺼 어디까지 한지 기억안나서 그냥 새로만듬#########################################################################################
##############################################################################################################################################################################################################

from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler
from NLP_custom import nlu_request, domestic_loc_list, arr_loc_list, city_list, loc_list
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, ReplyKeyboardRemove
import telegram
import pymssql as mssql
import functools
import operator
import logging
import telegramcalendar
from datetime import datetime
import datetime


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)

pre_defined_commands = ['/start', '메뉴', 'airport', '호텔','챗봇','메뉴']
updater = Updater(token='969396288:AAG7Dc4sfu_mtnsqNPlGb7w7Xs_LT6OHCPE')
dispatcher = updater.dispatcher
updater.start_polling()
## 항공을 위해 오늘날짜와 해외항공의 경우 6일 후부터 출발 가능날짜
sixdays = datetime.timedelta(days=6)
dayplussix = datetime.date.today() + sixdays
result_date = dayplussix.strftime('%Y-%m-%d')
## 국내항공의 경우 당일부터 예약가능 보통 3박 4일 일정이므로?4일로 잡겟음
rightnow = str(datetime.date.today())
fourdays = datetime.timedelta(days=3)
dayplusfour = datetime.date.today()+fourdays
domestic_result_date = dayplusfour.strftime('%Y-%m-%d')
## 해외항공 전체 리스트
Total_list = arr_loc_list+city_list+loc_list


## 달력 핸들러##
def calendar_handler(bot,update):
    update.message.reply_text("Please select a date: ",
                        reply_markup=telegramcalendar.create_calendar())

dispatcher.add_handler(CommandHandler("calendar", calendar_handler))

## 달력 콜백 핸들러 ##
def inline_handler(bot,update):
    selected,date = telegramcalendar.process_calendar_selection(bot, update)
    if selected:
        bot.send_message(chat_id=update.callback_query.from_user.id,
                        text="You selected %s" % (date.strftime("%d/%m/%Y")),
                        reply_markup=ReplyKeyboardRemove())
        save_date = date.strftime("%d/%m/%Y")

dispatcher.add_handler(CallbackQueryHandler(inline_handler))

## 튜플형태 리스트 변환 함수
def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str
## 스타트 함수
def start_command(bot, update):
    chat_id = update.message.chat_id
    custom_keyboard = [['챗봇']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id, text='안녕하세요! 여러분의 편리한 여행을 위한 챗봇 서비스입니다',reply_markup=reply_markup)

updater.dispatcher.add_handler(CommandHandler('start',start_command))

## 버튼 생성 함수
def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# 메시지 핸들링

def handler(bot, update):
    text = update.message.text
    chat_id = update.message.chat_id
    message_id = update.message.message_id

    if text not in pre_defined_commands:
        request = {
            "chat_id": chat_id,
            "message_id": message_id,
            "intent_id": "",
            "input_data": text,
            "request_type": "text",
            "story_slot_entity": {},
            "output_data": "",
        }
        json.loads.response = nlu_request(request) ## 항공 자연어처리
        # logger.info(json.loads.response)
        # bot.send_message(chat_id=chat_id, text=str(json.loads.response.get('intent_id')))
        # bot.send_message(chat_id=chat_id, text=str(json.loads.response.get('input_data')))
        # bot.send_message(chat_id=chat_id, text=str(json.loads.response.get('story_slot_entity')))
        # bot.send_message(chat_id=chat_id, text=str(json.loads.response.get('output_data')))
        #json.loads.response_pkg = nlu_request_pkg(request) ##패키지 자연어처리
        # bot.send_message(chat_id=chat_id, text=str(json.loads.response_pkg.get('output_data')))
    # 메뉴는 그냥 무조건 텍스트 안에 있으면 불러오기
    ## 없어도 될거같은 부분 닫힌 대화형식의 챗봇이 아닌 열린 대화형식의 챗봇으로 갈 예정이면 필요없음 간단하게 안내정도? 어떤 형식으로 질문해달라고
    ## 아니면 패키지를 받아왔을때 단순히 안내가 아닌 패키지 의도를 대화를 저장하고 그것을 기억하곡 난뒤 그다음 장소를 받아 하나하나 얻어가는 형식 구현
    ## 방법을 몰라서 좀 더 알아봐야될것 같음 (메뉴, 패키지, 호텔, 항공 등 다 없어도 될듯 버튼이 있으면 버튼만 사용하게됨)
    if text in ['메뉴', '메뉴리스트','리스트','하이','뭐야','안내','알려줘','챗봇','안녕','안뇽']:
        bot.send_message(chat_id=chat_id, text= '안녕하세요 ***여행 챗봇입니다.\n\n'\
                         '○○○ 패키지,해외항공,국내항공,항공권,자유여행,라르고,프리미엄\n\n'\
                         '○○○ 패키지 인천출발,대구출발,부산출발 \n\n'\
                         '형태로 질문해주세요')

    # elif text in ['항공권','항공편','비행기','항공티켓','항공'] :
    #     custom_keyboard = [['해외항공','국내항공']]
    #     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    #     bot.send_message(chat_id=chat_id,
    #                          text= '하단에 해외항공, 국내항공 중 선택해주세요',reply_markup=reply_markup)
        # bot.send_message(chat_id=chat_id, text='고객님께서 원하시는 항공메뉴를 불러옵니다')
        # show_list = []
        # show_list.append(InlineKeyboardButton('해외항공', callback_data='해외항공',url='http://www.verygoodtour.com/Product/Air2/AirMain'))
        # show_list.append(InlineKeyboardButton('국내항공', callback_data='국내항공',url='http://www.verygoodtour.com/Air/Domestic/Main'))
        # show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)- 1))
        # update.message.reply_text('해외항공, 국내항공을 선택해주세요',reply_markup=show_markup)

    elif '해외항공' in str(json.loads.response.get('output_data')):
        bot.send_message(chat_id=chat_id, text= '해외항공을 선택하셨습니다')
        show_list = []
        show_list.append(InlineKeyboardButton('홍콩', callback_data='홍콩',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen=true&OpenDay=300'
                                                  '&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&DepartureAirportCode=SEL'
                                                  '&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&ArrivalAirportCode=HKG'
                                                  '&ArrivalAirportName=%ED%99%8D%EC%BD%A9%5BHKG%5D&DepartureAirportCode2=&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('방콕', callback_data='방콕',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=BKK&ArrivalAirportName=%EB%B0%A9%EC%BD%95%5BBKK%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('타이페이', callback_data='타이페이',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=TPE&ArrivalAirportName=타이페이%5BTPE%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('싱가폴', callback_data='싱가폴',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=SIN&ArrivalAirportName=싱가폴%5BSIN%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('클락', callback_data='클락',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=CRK&ArrivalAirportName=클락%5BCRK%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('도쿄(나리타)', callback_data='도쿄(나리타)',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=NRT&ArrivalAirportName=도쿄%28나리타%29%5BNRT&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('도쿄(하네다)', callback_data='도쿄(하네다)',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=HND&ArrivalAirportName=도쿄%28하네다%29%5BHND&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('오사카', callback_data='오사카)',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=OSA&ArrivalAirportName=오사카%5BOSA%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('나고야', callback_data='나고야',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=NGO&ArrivalAirportName=나고야%5BNGO%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('후쿠오카', callback_data='후쿠오카',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=FUK&ArrivalAirportName=후쿠오카%5BFUK%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('북경', callback_data='북경',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=BJS&ArrivalAirportName=북경%5BBJS%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('상해(푸동)', callback_data='상해(푸동)',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=PVG&ArrivalAirportName=상해%28푸동%5BPVG%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('상해(홍챠오)', callback_data='상해(홍챠오)',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=SHA&ArrivalAirportName=상해%28홍챠오%5BSHA%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('청도', callback_data='청도',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=TAO&ArrivalAirportName=청도%5BTAO%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('광주', callback_data='광주',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=CAN&ArrivalAirportName=광주%5BCAN%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('런던', callback_data='런던',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=LON&ArrivalAirportName=런던%5BLON%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('파리', callback_data='파리',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=PAR&ArrivalAirportName=파리%5BPAR%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('로마', callback_data='로마',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=ROM&ArrivalAirportName=로마%5BROM%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('이스탄불', callback_data='이스탄불',
                                              url='http:/www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=IST&ArrivalAirportName=이스탄불%5BIST%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('프랑크푸르트', callback_data='프랑크푸르트',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=FRA&ArrivalAirportName=프랑크푸르트%5BFRA%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('LA', callback_data='LA',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=LAX&ArrivalAirportName=LA%5BLAX%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('뉴욕', callback_data='뉴욕',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=NYC&ArrivalAirportName=뉴욕%5BNYC%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('샌프란시스코', callback_data='샌프란시스코',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=SFO&ArrivalAirportName=샌프란시스코%5BSFO%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('보스턴', callback_data='보스턴',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=BOS&ArrivalAirportName=보스턴%5BBOS%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('벤쿠버', callback_data='벤쿠버',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=YVR&ArrivalAirportName=벤쿠버%5BYVR%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('시드니', callback_data='시드니',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=SYD&ArrivalAirportName=시드니%5BSYD%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('멜버른', callback_data='멜버른',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=MEL&ArrivalAirportName=멜버른%5BMEL%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('브리즈번', callback_data='브리즈번',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=BNE&ArrivalAirportName=브리즈번%5BBNE%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('오클랜드', callback_data='오클랜드',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=AKL&ArrivalAirportName=오클랜드%5BAKL%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_list.append(InlineKeyboardButton('괌', callback_data='괌',
                                              url='http://www.verygoodtour.com/Product/Air2/Schedule?AirType=2&IsOpen='
                                                  'true&OpenDay=300&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                  'DepartureAirportCode=SEL&DepartureAirportName=%EC%9D%B8%EC%B2%9C%2F%EA%B9%80%ED%8F%AC%5BSEL%5D&'
                                                  'ArrivalAirportCode=GUM&ArrivalAirportName=괌%5BGUM%5D&DepartureAirportCode2='
                                                  '&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate='+result_date+'&close'))
        show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)- 1))
        update.message.reply_text("찾으시는 지역이 없을 경우 <지역명>을 입력해주세요\n\n"\
                                  "국내항공권을 원하시는 고객님의 경우\n\n"\
                                  "예시) <지역명>+국내항공권 또는 국내항공권을 검색해주세요",reply_markup=show_markup)

    elif '국내항공' in str(json.loads.response.get('output_data')):
        bot.send_message(chat_id=chat_id, text= '국내항공을 선택하셨습니다')
        show_list = []
        show_list.append(InlineKeyboardButton('제주', callback_data='제주',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=CJU'
                                                  '&ArrivalAirportName=제주&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('청주', callback_data='청주',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=CJJ'
                                                  '&ArrivalAirportName=청주&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('진주', callback_data='진주',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=HIN'
                                                  '&ArrivalAirportName=진주&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('포항', callback_data='포항',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=KPO'
                                                  '&ArrivalAirportName=포항&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('군산', callback_data='군산',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=KUV'
                                                  '&ArrivalAirportName=군산&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('광주', callback_data='광주',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=KWJ'
                                                  '&ArrivalAirportName=광주&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('무안', callback_data='무안',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=MWX'
                                                  '&ArrivalAirportName=무안&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('부산', callback_data='부산',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=PUS'
                                                  '&ArrivalAirportName=부산&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('여수', callback_data='여수',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=RSU'
                                                  '&ArrivalAirportName=여수&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('대구', callback_data='대구',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=TAE'
                                                  '&ArrivalAirportName=대구&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('울산', callback_data='울산',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=USN'
                                                  '&ArrivalAirportName=울산&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_list.append(InlineKeyboardButton('원주', callback_data='원주',
                                              url='http://www.verygoodtour.com/Air/Domestic/Avail/Schedule?AirType=2&Airline=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                  '&DepartureAirportCode=GMP&DepartureAirportName=%EA%B9%80%ED%8F%AC&ArrivalAirportCode=WJU'
                                                  '&ArrivalAirportName=청주&DepartureDate='+rightnow+'&ArrivalDate='+domestic_result_date+'&AvailNo=&AirlineCode='))
        show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)- 1))
        update.message.reply_text("찾으시는 지역이 없을 경우 <지역명>을 입력해주세요\n\n"\
                                  "해외항공권을 원하시는 고객님의 경우\n\n"\
                                  "예시) <지역명>+해외항공권 또는 해외항공권을 검색해주세요",reply_markup=show_markup)

    elif '의도' in str(json.loads.response.get('output_data')):
        custom_keyboard = [['패키지','라르고','프리미엄','항공','국내항공','자유']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id,
                         text= '패키지, 라르고, 프리미엄, 항공권, 자유 중 원하시는 서비스를 입력해주세요\n\n'\
                                '지방출발상품을 확인하고 싶은 고객님께서는\n\n'\
                                '예시) 패키지 부산출발, 라르고 인천출발, 패키지 무안출발',reply_markup=reply_markup)

    elif '패키지' in str(json.loads.response.get('output_data')):
        custom_keyboard = [['미국','중국','일본','유럽','동남아','대양주','미주']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id,
                         text="여행지명을 함께 입력해주세요.\n\n"\
                         "예시) 오사카, 방콕, 중국\n\n"\
                         "지방출발상품을 확인하고 싶은 고객님께서는\n\n"\
                         " 예시) 오사카 인천출발, 방콕 청주출발",
                         reply_markup=reply_markup)

    elif '항공' in str(json.loads.response.get('output_data')):
        bot.send_message(chat_id=chat_id,
                         text="도착지를 입력해주세요.\n\n"\
                         "예시) 오사카, 뉴욕, 홍콩")

    elif '자유' in str(json.loads.response.get('output_data')):
        custom_keyboard = [['미국 자유','중국 자유','일본 자유','유럽 자유','동남아 자유','대양주 자유','미주 자유']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id,
                         text="여행지명을 함께 입력해주세요.\n\n"\
                         "예시) 오사카, 방콕, 중국\n\n" \
                         "지방출발상품을 확인하고 싶은 고객님께서는\n\n" \
                         "예시) 오사카 무안출발, 방콕 청주출발",
                         reply_markup=reply_markup)

    elif '라르고' in str(json.loads.response.get('output_data')):
        custom_keyboard = [['미국','중국','일본','유럽','동남아','대양주','미주']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id,
                         text="여행지명을 함께 입력해주세요.\n\n"\
                         "예시) 오사카, 방콕, 중국\n\n"\
                         "지방출발상품을 확인하고 싶은 고객님께서는\n\n"\
                         "예시) 라르고 무안출발, 라르고 청주출발",
                         reply_markup=reply_markup)

    elif '프리미엄' in str(json.loads.response.get('output_data')):
        custom_keyboard = [['미국','중국','일본','유럽','동남아','대양주','미주']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        bot.send_message(chat_id=chat_id,
                         text="여행지명을 함께 입력해주세요.\n\n"\
                         "예시) 오사카, 방콕, 중국\n\n"\
                         "지방출발상품을 확인하고 싶은 고객님께서는\n\n"\
                         "예시) 프리미엄 무안출발, 프리미엄 청주출발",
                         reply_markup=reply_markup)

    # elif '항공' in str(json.loads.response.get('output_data')):
    #     custom_keyboard = [['해외항공','국내항공']]
    #     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    #     bot.send_message(chat_id=chat_id,
    #                      text= '해외항공, 국내항공 중 선택해주세요',reply_markup=reply_markup)

    ## 추후 장소를 받아와서 파라미터를 전송하여 장소와 날짜를 채울 예정
    ## 항공과 장소항목이 동시에 들어왔을떄 불러오는 항목
    # elif '항공장소' in str(json.loads.response.get('intent_id')):
    #     bot.send_message(chat_id=chat_id, text='고객님께서 원하시는 항공메뉴를 불러옵니다')
    #     show_list = []
    #     show_list.append(InlineKeyboardButton('해외항공', callback_data='해외항공',url='http://www.verygoodtour.com/Product/Air2/AirMain'))
    #     show_list.append(InlineKeyboardButton('국내항공', callback_data='국내항공',url='http://www.verygoodtour.com/Air/Domestic/Main'))
    #     show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)- 1))
    #     update.message.reply_text('해외항공, 국내항공을 선택해주세요',reply_markup=show_markup)

    elif '항공장소' in str(json.loads.response.get('intent_id')):
        ## 장소를 먼저 불러온다 어떤 도시를 찾는지!!!
        take_city = str(json.loads.response.get('output_data'))
        ## 고객이 원하는 도시를 SQL 디비에서 조회를 실시
        conn = mssql.connect(server="*********", user="*********", password="@!***********", database="*********",
                             ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                             charset="utf8")
        cursor = conn.cursor()
        if take_city != []:
            sql = " SELECT CITY_CODE" \
                  " FROM PUB_CITY" \
                  " WHERE IS_USE_AIR = 1 AND KOR_NAME = '%s'" %(take_city)
            cursor.execute(sql)
            match_city = cursor.fetchall()
            ## 튜플형태라서 잘못된 데이터 형태를 리스트 형태로 변환
            if match_city != []:
                match_city = convertTuple(match_city)
                match_city = list(match_city)
            matching_city = []
            for i in match_city:
                matching_city.append(i)
            if matching_city == []:
                bot.send_message(chat_id=chat_id, text="검색하신 지역상품을 찾을 수가 없습니다\n\n"
                                                       "국가이름이 아닌 공항 지역명을 입력해주세요")

            if matching_city != []:
                bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
                show_list = []
                if take_city in domestic_loc_list:
                    show_list.append(InlineKeyboardButton(take_city, callback_data=take_city,
                                                      url='http://m.verygoodtour.com/Air/AirDom/AirSchedule?AirType=2&IsOpen=false&OpenDay=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                          '&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&DepartureAirportCode=GMP&DepartureAirportName=김포&'
                                                          'ArrivalAirportCode='+ match_city[0]+'&ArrivalAirportName='+ take_city + '&DepartureAirportCode2=&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2='
                                                          '&DepartureDate='+ rightnow + '&ArrivalDate=' + domestic_result_date))
                    show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
                    ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
                    update.message.reply_text("%s 지역 상품입니다\n\n" \
                                              "원하는 검색이 나오지 않으시는 경우\n\n" \
                                              "예시) 지역명+항공권 알려줘 입력" % (take_city), reply_markup=show_markup)

                elif take_city in Total_list:
                    show_list.append(InlineKeyboardButton(take_city, callback_data=take_city,
                                                          url = 'http://m.verygoodtour.com/Air/AirSea/AirSchedule?AirType=2&IsOpen='
                                                                'false&OpenDay=&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                                'DepartureAirportCode=ICN&DepartureAirportName=%EC%9D%B8%EC%B2%9C&'
                                                                'ArrivalAirportCode='+ match_city[0] + '&ArrivalAirportName='+ take_city +
                                                                '&DepartureAirportCode2=&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate=' +rightnow + '&ArrivalDate=' + result_date))
                    show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
                    ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
                    update.message.reply_text("%s 지역 상품입니다\n\n" \
                                              "원하시는 결과가 안나오는 경우\n\n" \
                                              "예시) 일본 항공권 -> 오사카. 도쿄 등 상세 지역명 입력" % (take_city), reply_markup=show_markup)


    elif '의도장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        menu_value = str(json.loads.response['story_slot_entity'].get('메뉴'))
        ## 의도가 분석이 안됫을시 다시한번 여기서 의도를 메뉴 슬롯에 채워진걸로 분류 후 브랜드 타입도 한번에 여기서 다 진행할수 있게금 brand_type도 함께 설정
        if menu_value in ['패키지', '패키지관광', '패키지여행', '패키지상품', '해외여행','패키지상품']:
            menu_select = "='p'"
            brand_type =  'brand_type is null'
        elif menu_value in ['자유여행', '자유', '개별', '개별여행', '자유일정', '자유관광','자유상품','자유여행상품']:
            menu_select = "='f'"
            brand_type = 'brand_type is null'
        elif menu_value in ['라르고','Largo','LARGO','largo']:
            menu_select = "='p' or pm.att_code = 'f'"
            brand_type = 'brand_type = 2'
        elif menu_value in ['프리미엄','plus','PLUS','Plus','라르고플러스','플러스']:
            menu_select = "='p' or pm.att_code = 'f'"
            brand_type = 'brand_type = 1'
        elif menu_value in ['국내항공', '국내항공권','국내항공편','국내비행기', '국내','해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외','항공권','항공']:
            ## 장소를 먼저 불러온다 어떤 도시를 찾는지!!!
            take_city = str(json.loads.response.get('output_data'))
            ## 고객이 원하는 도시를 SQL 디비에서 조회를 실시
            conn = mssql.connect(server="**************", user="**", password="*******",
                               database="*****",
                                 ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                                 charset="utf8")
            cursor = conn.cursor()
            if take_city != []:
                sql = " SELECT CITY_CODE" \
                      " FROM PUB_CITY" \
                      " WHERE IS_USE_AIR = 1 AND KOR_NAME = '%s'" % (take_city)
                cursor.execute(sql)
                match_city = cursor.fetchall()
                ## 튜플형태라서 잘못된 데이터 형태를 리스트 형태로 변환
                if match_city != []:
                    match_city = convertTuple(match_city)
                    match_city = list(match_city)
                matching_city = []
                for i in match_city:
                    matching_city.append(i)
                    matching_city = str(matching_city)
                if matching_city == []:
                    bot.send_message(chat_id=chat_id, text="검색하신 지역상품을 찾을 수가 없습니다\n\n"
                                                           "국가이름이 아닌 공항 지역명을 입력해주세요")

                if matching_city != []:
                    bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
                    show_list = []
                    if take_city in domestic_loc_list:
                        show_list.append(InlineKeyboardButton(take_city, callback_data=take_city,
                                                              url='http://m.verygoodtour.com/Air/AirDom/AirSchedule?AirType=2&IsOpen=false&OpenDay=&AdultCount=1&ChildCount=0&InfantCount=0'
                                                                  '&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&DepartureAirportCode=GMP&DepartureAirportName=김포&'
                                                                  'ArrivalAirportCode=' + match_city[0] + '&ArrivalAirportName=' + take_city +
                                                                  '&DepartureAirportCode2=&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2='
                                                                  '&DepartureDate=' + rightnow + '&ArrivalDate=' + domestic_result_date))
                    elif take_city in Total_list:
                        show_list.append(InlineKeyboardButton(take_city, callback_data=take_city,
                                                              url='http://m.verygoodtour.com/Air/AirSea/AirSchedule?AirType=2&IsOpen='
                                                                  'false&OpenDay=&AdultCount=1&ChildCount=0&InfantCount=0&FareSeatType=%EC%9D%BC%EB%B0%98%EC%84%9D&'
                                                                  'DepartureAirportCode=ICN&DepartureAirportName=%EC%9D%B8%EC%B2%9C&'
                                                                  'ArrivalAirportCode=' + match_city[0] + '&ArrivalAirportName=' + take_city +
                                                                  '&DepartureAirportCode2=&DepartureAirportName2=&ArrivalAirportCode2=&ArrivalAirportName2=&DepartureDate=' + rightnow + '&ArrivalDate=' + result_date))
                show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
                ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
                update.message.reply_text('%s 지역 상품입니다' % (take_city), reply_markup=show_markup)

        ## 출발지 추가
        if dep_location in ['인천', '김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)

        conn = mssql.connect(server="1************0", user="**", password="**************", database="*****",
                             ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                             charset="utf8")
        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and (pm.att_code %s) and %s" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (menu_select, brand_type ,cvt_dep_loc, nation_value, nation_value, nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and (pm.att_code %s) and %s" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (menu_select, brand_type,cvt_dep_loc, '%' + nation_value + '%', '%' + nation_value + '%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text='검색하신 지역상품을 찾을 수가 없습니다')

        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (
                  matching_list[0], matching_list[1], matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (
                  matching_list[0], matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 1:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s'"% (matching_list[0])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        if len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)
        if len(image_info_1) == 2:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2 or len(matching_list) == 1:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                      callback_data=matching_list[0],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                      callback_data=matching_list[1],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                      callback_data=matching_list[2],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                      callback_data=matching_list[0],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                      callback_data=matching_list[1],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[1])))
            elif len(matching_list) == 1:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                      callback_data=matching_list[0],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[0])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다' % (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)

    elif '자유장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        logger.info(dep_location)
        ## 출발지 추가
        if dep_location in ['인천', '김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)


        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code <> 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc, nation_value, nation_value, nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code <> 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc, '%' + nation_value + '%', '%' + nation_value + '%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text='검색하신 지역상품을 찾을 수가 없습니다')

        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0], matching_list[1], matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()
            conn = mssql.connect(server="*************", user="**********", password="***************",
                                 database="*********",
                                 ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                                 charset="utf8")
            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (
                  matching_list[0], matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        if len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                      callback_data=matching_list[0],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                      callback_data=matching_list[1],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                      callback_data=matching_list[2],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                      callback_data=matching_list[0],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                      callback_data=matching_list[1],
                                                      url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (
                                                      matching_list[1])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다' % (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)



    # 의도를 패키지로 분류하고 장소까지 받아왓을떄 나오는 항목
    elif '패키지장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        logger.info(dep_location)
        ## 출발지 추가
        if dep_location in ['인천','김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)

        conn = mssql.connect(server="*********", user="*********", password="@!***********", database="*********", ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                             charset="utf8")
        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code = 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,nation_value,nation_value,nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code = 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,'%'+nation_value+'%','%'+nation_value+'%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text= '검색하신 지역상품을 찾을 수가 없습니다')

        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()
            conn = mssql.connect(server="*********", user="*********", password="*********",
                                 database="*********",
                                 ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                                 charset="utf8")
            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)
            logger.info(master_name_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()
            conn = mssql.connect(server="*********", user="*********", password="@!***********",
                                 database="*********",
                                 ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                                 charset="utf8")
            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

         ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        if len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0], caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2], caption='['+'1'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                  callback_data=matching_list[2],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다'% (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)

    elif '자유장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        logger.info(dep_location)
        ## 출발지 추가
        if dep_location in ['인천','김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)

        conn = mssql.connect(server="*********", user="*********", password="@!***********", database="*********", ## elif intent_id == '패키지': nation_value = 'output_data' sql = 'select master_code from pkg_master where show_yn = 'y'#
                             charset="utf8")
        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code <> 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,nation_value,nation_value,nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.att_code <> 'p'" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,'%'+nation_value+'%','%'+nation_value+'%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text= '검색하신 지역상품을 찾을 수가 없습니다')

        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

         ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        if len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                  callback_data=matching_list[2],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list) - 1))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다'% (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)

    elif '라르고장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        logger.info(dep_location)
        ## 출발지 추가
        if dep_location in ['인천','김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)


        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.brand_type = 1" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,nation_value,nation_value,nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.brand_type = 1" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,'%'+nation_value+'%','%'+nation_value+'%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text= '검색하신 지역상품을 찾을 수가 없습니다\n\n'\
                                                           '다른 지역명으로 검색해주세요')
        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 1:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s'"% (matching_list[0])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

         ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        elif len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)
        elif len(image_info_1) == 2:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2 or len(matching_list) == 1:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                  callback_data=matching_list[2],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))

            elif len(matching_list) == 1:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다'% (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)

    elif '프리미엄장소' in str(json.loads.response.get('intent_id')):
        nation_value = str(json.loads.response.get('output_data'))
        dep_location = str(json.loads.response['story_slot_entity'].get('출발'))
        logger.info(dep_location)
        ## 출발지 추가
        if dep_location in ['인천','김포']:
            cvt_dep_loc = '0'
        elif dep_location in ['부산']:
            cvt_dep_loc = '1'
        elif dep_location in ['대구']:
            cvt_dep_loc = '2'
        elif dep_location in ['청주']:
            cvt_dep_loc = '3'
        elif dep_location in ['무안']:
            cvt_dep_loc = '4'
        else:
            cvt_dep_loc = '0'

        logger.info(cvt_dep_loc)


        cursor = conn.cursor()
        ## 쿼리문 작성 장소를 불러와서 쿼리에 format을 사용하여 nation_value에 담긴 장소이름을 like문에 삽입하여 리스트 출력
        if cvt_dep_loc != []:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.brand_type = 2" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (vc.region_name = '%s' or vc.nation_name = '%s' or vc.city_name = '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,nation_value,nation_value,nation_value)
            cursor.execute(sql)
            matching = cursor.fetchall()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
        ## 만약 REION NAME , NATION_NAME, CITY_NAME에서 상품이 추출이 안되면 MASTER_NAME 과 PKG_COMMENT에서 LIKE문으로 추출
        if matching == [] or len(matching) == 1:
            sql = " select top 3 pm.master_code" \
                  " from pkg_master pm with(nolock)" \
                  " inner join pkg_detail pd with(nolock)" \
                  " on pm.master_code = pd.master_code" \
                  " inner join pro_trans_seat ts with(nolock)" \
                  " on pd.seat_code = ts.seat_code" \
                  " left join pub_airport pa with(nolock)" \
                  " on ts.dep_arr_airport_code = pa.airport_code" \
                  " left join view_city vc with(nolock)" \
                  " on pa.city_code = vc.city_code" \
                  " where pd.show_yn= 'y' and pm.brand_type = 2" \
                  " and pd.dep_date > getdate() and pm.branch_code = '%s' and (pm.master_name like '%s' or pm.master_name like '%s')" \
                  " group by pm.master_code" \
                  " order by newid()" % (cvt_dep_loc,'%'+nation_value+'%','%'+nation_value+'%')
            cursor.execute(sql)
            matching = cursor.fetchall()
            # conn.close()
            if matching != []:
                matching = convertTuple(matching)
                matching = list(matching)
            matching_list = []
            for i in matching:
                matching_list.append(i)
            if matching_list == []:
                bot.send_message(chat_id=chat_id, text= '검색하신 지역상품을 찾을 수가 없습니다\n\n'\
                                                          '※프리미엄 상품 지역※\n\n'\
                                                          '서유럽,동유럽,발칸,스페인,북유럽,지중해,동남아,중국,국내')

        ## 디버그 로깅
        logger.info(matching_list)
        ## sql 자체에서 정보를 매칭하여 이미지 url까지 완성해서 파이썬에 저장하여 불러와서 사용하는 형식
        if len(matching_list) == 3:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s' or MASTER_CODE = '%s' ) SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s' or MASTER_CODE = '%s' "% (matching_list[0],matching_list[1],matching_list[2])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 2:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s' or MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0],matching_list[1])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s' or Master_code = '%s'"% (matching_list[0],matching_list[1])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

        if len(matching_list) == 1:
            cursor = conn.cursor()
            sql = " WITH LIST AS ( SELECT (CASE WHEN IFM.FILE_NAME_S = '' THEN '' WHEN IFM.FILE_NAME_M = '' THEN ('http://contents.verygoodtour.com/content/'" \
                  " + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_S)" \
                  " ELSE ('http://contents.verygoodtour.com/content/' + IFM.REGION_CODE + '/' + IFM.NATION_CODE + '/' + IFM.STATE_CODE + '/' + IFM.CITY_CODE + '/image/' + IFM.FILE_NAME_M)" \
                  " END) AS [PKG_IMG_URL], ROW_NUMBER() OVER(PARTITION BY MASTER_CODE ORDER BY MASTER_CODE ) AS RANK" \
                  " FROM PKG_FILE_MANAGER PFM WITH(NOLOCK)" \
                  " INNER JOIN INF_FILE_MASTER IFM WITH(NOLOCK)" \
                  " ON PFM.FILE_CODE = IFM.FILE_CODE" \
                  " WHERE IFM.FILE_TYPE =1 AND IFM.SHOW_YN = 'Y' AND MASTER_CODE = '%s') SELECT * FROM LIST WHERE RANK = 1" % (matching_list[0])
            cursor.execute(sql)
            image_info = cursor.fetchall()
            image_info_1 = convertTuple(image_info)
            image_info_1 = list(image_info_1)
            conn.close()

            cursor = conn.cursor()
            sql = " SELECT MASTER_NAME" \
                  " FROM PKG_MASTER " \
                  " WHERE MASTER_CODE = '%s'"% (matching_list[0])
            cursor.execute(sql)
            master_name = cursor.fetchall()
            master_name_1 = convertTuple(master_name)
            master_name_1 = list(master_name_1)
            conn.close()
            ##디버깅
            logger.info(image_info_1)

         ##상품 메뉴버튼 마스터코드
        if len(image_info_1) == 6:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[4],  caption='['+'3'+'.'+matching_list[2]+']'+master_name_1[2])
            ##디버그
            logger.info(len(image_info_1))
        if len(image_info_1) == 4:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            bot.send_photo(chat_id=chat_id, photo=image_info_1[2],  caption='['+'2'+'.'+matching_list[1]+']'+master_name_1[1])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        if len(image_info_1) == 2:
            bot.send_photo(chat_id=chat_id, photo=image_info_1[0],  caption='['+'1'+'.'+matching_list[0]+']'+master_name_1[0])
            logger.info(len(image_info_1))
            logger.info(bot.send_photo)

        ## 사진은 보낼수 없지만 버튼에 url 삽입 가능
        if len(matching_list) == 3 or len(matching_list) == 2 or len(matching_list) == 1:
            bot.send_message(chat_id=chat_id, text='잠시만 기다려주세요 로딩중...')
            if len(matching_list) == 3:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))
                show_list.append(InlineKeyboardButton(matching_list[2],
                                                  callback_data=matching_list[2],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' % (matching_list[2])))
            elif len(matching_list) == 2:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
                show_list.append(InlineKeyboardButton(matching_list[1],
                                                  callback_data=matching_list[1],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[1])))

            elif len(matching_list) == 1:
                show_list = []
                show_list.append(InlineKeyboardButton(matching_list[0],
                                                  callback_data=matching_list[0],
                                                  url='http://www.verygoodtour.com/Product/Package/PackageMaster?MasterCode=%s#n' %(matching_list[0])))
            show_markup = InlineKeyboardMarkup(build_menu(show_list, len(show_list)))
            ## 불러온 상품 기준의 땡땡 지역 상품입니다 멘트
            update.message.reply_text('%s 지역 상품입니다'% (nation_value), reply_markup=show_markup)
        ##디버깅
        logger.info(len(matching_list))
        logger.info(show_list)
        logger.info(InlineKeyboardButton)



echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)