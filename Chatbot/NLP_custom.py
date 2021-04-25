##################################################################################################################################################################
##버젼 9  2020년 3월 다시 진행 항공합치기 버젼 기억안나서 다시 해보기#############################################################################################
##################################################################################################################################################################
from konlpy.corpus import kolaw
from konlpy.tag import Kkma
from konlpy import init_jvm
import pymssql as mssql
import json
import functools
import operator
import logging
import re
from pymongo import MongoClient
import requests
import datetime
from bson.objectid import ObjectId

##############################################
##########실시간 불러와져있는 정보############
#############################################
client = MongoClient('localhost', 27017)
db = client.seungeun
response_collect = db["seungeun"]

## 튜플을 리스트 형태로 변환해주는 함수
def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str

## 항공 메뉴
# menu_list = ['항공', '항공권', '해외항공', '국내항공', '비행티켓', '비행기', '티켓', '항공편']
international_air = ['해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외','국내항공', '국내항공권','국내항공편','국내비행기', '국내','항공','항공권']
inter_air = ['해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외']
dome_air = ['국내항공', '국내항공권','국내항공편','국내비행기']
## 날짜 리스트
date_list = ['지금', '내일', '모레', '월', '일', '년도', '년']
## 숫자 리스트
number_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
               '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31','32','33']
air = ['항공','항공권']
##패키지 메뉴
pkgmenu_list = ['패키지', '패키지관광', '패키지여행', '패키지상품', '해외여행','패키지상품']
##국가 및 지역 리스트 해당 3가지외에 밑에 코드에서 어펜드중
loc_list = ['동남아', '국내', '유럽', '미서부', '미동부', '서유럽', '동유럽', '발칸', '북유럽', '지중해', '중동']
## 자유여행 메뉴
freetour_list = ['자유여행', '자유', '개별', '개별여행', '자유일정', '자유관광','자유상품','자유여행상품']

city_list = ['PIC','웨스틴','피에스타','쉐라톤','닛코','힐튼','켄싱턴','퀘백','뉴올리언스','올란도','마이애미','하와이','장강삼협','태항산','티벳','황산','하롱베이','푸꾸옥','달랏','보라카이','보홀','두짓타니','우유니'
             ,'옐로나이프','애틀란타','아오시마','비에이','하코네','다카마츠','디즈니랜드','료칸','나오시마','마츠야마','유후인','벳부','미야자키','오키야마','고베','노보리베츠','유니버셜','스튜디오','에노시마',
             '가마쿠라','코카서스','칸쿤','푸켓','푸껫','카오락','크라비','치앙마이','파타야','큐슈','노보리베츠','도야','동경','오타루','시고쿠','화련','팔라완','지중해','발리','슬로베키아']

largo_list = ['라르고','Largo','LARGO','largo']

premuim_list = ['프리미엄','plus','PLUS','Plus','라르고플러스','플러스']

dep_loc_list = ['인천','김포','부산','대구','청주','무안','양양']

domestic_loc_list = ['청주','제주','김포','진주','포항','군산','광주','무안','부산','여수','대구','울산','원주']

arr_loc_list = ['홍콩','방콕','타이페이','싱가폴','클락','도쿄','오사카','나고야','후쿠오카','북경','상해','청도','광주','런던','파리','로마','이스탄불','프랑크푸르트','LA','뉴욕','샌프란시스코','보스턴','벤쿠버',
                '시드니','멜버른','브리즈번','오클랜드','괌']

## 국가 리스트 어펜드 과정 사내 디비 연결 데이터 튜플형태로 불러온디 리스트형태로 변환
## 서버정보는 제거

cursor = conn.cursor()

# cursor.execute('select kor_name from pub_nation where is_use = 1')
cursor.execute('select kor_name from pub_nation')
fetch2 = cursor.fetchall()

str = convertTuple(fetch2)

loc_db = list(str)
##리스트형태로 변환된 값을 어팬드(형태맞추기)
for i in loc_db:
    loc_list.append(i)

conn.close()
## 도시 리스트 위에 같은 방법으로 진행
## 서버정보는 제거
cursor = conn.cursor()

# cursor.execute("select kor_name from pub_city where is_use_air = 1 and major_yn = 'Y'")
cursor.execute("select kor_name from pub_city where kor_name not in ('인천','김포','부산','대구','부산','청주','무안','양양')")

fetch3 = cursor.fetchall()

str = convertTuple(fetch3)

city_db = list(str)
##리스트형태로 변환된 값을 어팬드(형태맞추기)
for i in city_db:
    city_list.append(i)

conn.close()

## 서버정보는 제거
cursor = conn.cursor()

# cursor.execute("select kor_name from pub_city where is_use_air = 1 and major_yn = 'Y'")
cursor.execute("select kor_name from pub_city where kor_name not in ('인천','김포','부산','대구','부산','청주','무안','양양') and is_use_air = 1 and major_yn = 'y'")

fetch4 = cursor.fetchall()

str = convertTuple(fetch4)

inter_city_db = list(str)
##리스트형태로 변환된 값을 어팬드(형태맞추기)
for i in inter_city_db:
    arr_loc_list.append(i)

conn.close()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)
###########################################################
##################### 자연어 처리 함수#####################
###########################################################
def nlu_request(request):
#    init_jvm("C:/Program Files/Java/jdk-11.0.1")
    kkma = Kkma()
    ## 디버그용 명령어
    logger.info(request['input_data'])
    ## 유저의 채팅 아이디 호출
    user_id = request['chat_id']
    print(user_id,'#1')
    ## 자연어처리 인풋 데이터
    preprocessed = kkma.pos(request['input_data'])
    logger.info(preprocessed)

    ## 스토리 슬롯 엔티티 항공 패키지 자유 세가지로 분류
    story_slot_entity = {"항공": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None},
                         "패키지": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None},
                         "자유": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None},
                         "라르고": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None},
                         "프리미엄": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None},
                         "의도": {"메뉴": None, "장소": None, "숫자": None, "날짜": None, "출발": None}
                         }
    logger.info(story_slot_entity)
    ## 유저의 마지막 대화가 존재한다면 불러오기 몽고db의 response_collect에서 search
    user_last_response = []
    logger.info(user_last_response)
    ## 유저 대화목록 db에서 현재 들어온 유저의 아이디와 같고 마지막 대화만을 호출
    docs = response_collect.find({"chat_id":user_id}).sort([("message_id",-1)]).limit(1)
    print(docs)
    ## 마지막 대화를 입력
    for doc in docs:
        user_last_response.append(doc)
    print(user_last_response, '#3')

    ## 만약에 몽고db에 유저의 마지막 대화 기록이 있으면 실행
    if user_last_response != []: ## 유저의 마지막 대화가 있다면 .... --->
        ## 전대화에서 only 메뉴 장소만 있을때 상품을 노출시켜줫으니 전대화 초기화 및 제거k\
        if user_last_response[0]['story_slot_entity']['메뉴'] != None and user_last_response[0]['story_slot_entity']['장소'] != None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] == None:
            pre_user_slot_value = []
            pre_user_intent_id = []
            response_collect.remove({"chat_id": user_id})
        ## 전대화에서 only 메뉴 장소, 출발이 있을때 상품을 노출시켜줫으니 전대화 초기화 및 제거
        elif user_last_response[0]['story_slot_entity']['메뉴'] != None and user_last_response[0]['story_slot_entity']['장소'] != None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] != None:
            pre_user_slot_value = []
            pre_user_intent_id = []
            response_collect.remove({"chat_id": user_id})
        ## 전대화에서 only 장소만 있을때 상품을 안보여줫으니 아직,,,, 전대화 슬롯이랑 의도 불러오기
        elif user_last_response[0]['story_slot_entity']['메뉴'] == None and user_last_response[0]['story_slot_entity']['장소'] != None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] == None:
            pre_user_slot_value = user_last_response[0]['story_slot_entity']
            pre_user_intent_id = user_last_response[0]['intent_id']
        ## 전대화에서 only 메뉴만 있을때 상품을 안보여줫으니 아직,,,, 전대화 슬롯이랑 의도 불러오기
        elif user_last_response[0]['story_slot_entity']['메뉴'] != None and user_last_response[0]['story_slot_entity']['장소'] == None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] == None:
            pre_user_slot_value = user_last_response[0]['story_slot_entity']
            pre_user_intent_id = user_last_response[0]['intent_id']
        ## 전대화에서 지역과 출발만 들어왓을때 의도로 분류해서 상품을 보여줫으니 초기화 하는걸로 우선 작성 추후 변경 될수도
        elif user_last_response[0]['story_slot_entity']['메뉴'] == None and user_last_response[0]['story_slot_entity']['장소'] != None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] != None:
            pre_user_slot_value = []
            pre_user_intent_id = []
            response_collect.remove({"chat_id": user_id})
        # elif user_last_response[0]['story_slot_entity']['메뉴'] == '해외항공' and user_last_response[0]['story_slot_entity']['장소'] == None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] == None:
        #     pre_user_slot_value = []
        #     pre_user_intent_id = []
        #     response_collect.remove({"chat_id": user_id})
        # elif user_last_response[0]['story_slot_entity']['메뉴'] == '국내항공' and user_last_response[0]['story_slot_entity']['장소'] != None and user_last_response[0]['story_slot_entity']['숫자'] == None and user_last_response[0]['story_slot_entity']['날짜'] == None and user_last_response[0]['story_slot_entity']['출발'] == None:
        #     pre_user_slot_value = []
        #     pre_user_intent_id = []
        #     response_collect.remove({"chat_id": user_id})
        # else:
        #     pre_user_slot_value = user_last_response[0]['story_slot_entity']
        #     pre_user_intent_id = user_last_response[0]['intent_id']
        # pre_user_slot_value = response_collect.find_one({'chat_id': user_id})['story_slot_entity']
        # pre_user_intent_id = response_collect.find_one({'chat_id': user_id})['intent_id']
    ## 유저의 마지막 대화가 없다면 무조건 빈값으로 전대화 리스트를....
    elif user_last_response == []:
        pre_user_intent_id = []
        pre_user_slot_value = []

    print(pre_user_intent_id, '#4')
    print(pre_user_slot_value, '#5')


    #### 기초 1차 의도 분류#####
    ## 전에 입력했던 대화값이 없으면 story_slot_entity를 통해 진행
    if pre_user_intent_id == []:
        intent_id = []
        for pos_tag in preprocessed:
            if pos_tag[1] in ['NNG', 'NNP', 'NR', 'NNM','OL']:
                if pos_tag[0] in ['해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외','국내항공', '국내항공권','국내항공편','국내비행기', '국내','항공','항공권']:
                    intent_id = "항공"
                elif pos_tag[0] in ['패키지', '패키지관광', '패키지여행', '패키지상품', '해외여행','패키지상품']:
                    intent_id = "패키지"
                elif pos_tag[0] in ['자유여행', '자유', '개별', '개별여행', '자유일정', '자유관광','자유상품','자유여행상품']:
                    intent_id = "자유"
                elif pos_tag[0] in ['라르고','Largo','LARGO','largo']:
                    intent_id = '라르고'
                elif pos_tag[0] in ['프리미엄','plus','PLUS','Plus','라르고플러스','플러스']:
                    intent_id = '프리미엄'
                else:
                    intent_id = '의도'

        print(intent_id, '#전대화없을떄 1차 의도추출')

    ## 의도 분류후 선정된 의도의 슬롯만 불러와서 slot_value로 저장
        slot_value = story_slot_entity[intent_id]  #  story_slot_entity['항공'] or ['패키지']
        print(slot_value, '#6 의도추출')

    ## 각 의도에 따른 메뉴 장소 숫자 날짜를 슬롯 필링하는 과정
        if intent_id == '항공' or intent_id == '패키지' or intent_id == '자유' or intent_id == '라르고' or intent_id == '프리미엄' or intent_id == '의도':
            for val, pos_tag in preprocessed:
                if(pos_tag) in ['NNG', 'NNP', 'NR', 'NNM','OL']:
                    if intent_id == '항공':
                        if val in international_air:
                            slot_value['메뉴'] = val
                        elif val in domestic_loc_list:
                            slot_value['장소'] = val
                        elif val in arr_loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val

                    elif intent_id == '패키지':
                        if val in pkgmenu_list:
                            slot_value['메뉴'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in ['국'] and ['내']:
                            slot_value['장소'] = '국내'
                        elif val in dep_loc_list:
                            slot_value['출발'] = val

                    elif intent_id == '자유':
                        if val in freetour_list:
                            slot_value['메뉴'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in ['국'] and ['내']:
                            slot_value['장소'] = '국내'
                        elif val in dep_loc_list:
                            slot_value['출발'] = val

                    elif intent_id == '라르고':
                        if val in largo_list:
                            slot_value['메뉴'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in ['국'] and ['내']:
                            slot_value['장소'] = '국내'
                        elif val in dep_loc_list:
                            slot_value['출발'] = val

                    elif intent_id == '프리미엄':
                        if val in premuim_list:
                            slot_value['메뉴'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in ['국'] and ['내']:
                            slot_value['장소'] = '국내'
                        elif val in dep_loc_list:
                            slot_value['출발'] = val

                    elif intent_id == '의도':
                        if val in pkgmenu_list:
                            slot_value['메뉴'] = val
                        elif val in premuim_list:
                            slot_value['메뉴'] = val
                        elif val in freetour_list:
                            slot_value['메뉴'] = val
                        elif val in largo_list:
                            slot_value['메뉴'] = val
                        elif val in international_air:
                            slot_value['메뉴'] = val
                        # elif val in domestic_loc_list:
                        #     slot_value['장소'] = val
                        # elif val in arr_loc_list:
                        #     slot_value['장소'] = val
                        elif val in loc_list:
                            slot_value['장소'] = val
                        elif val in city_list:
                            slot_value['장소'] = val
                        elif val in ['국'] and ['내']:
                            slot_value['장소'] = '국내'
                        elif val in dep_loc_list:
                            slot_value['출발'] = val

                    if val in number_list:
                        slot_value['숫자'] = val
                    if val in  date_list:
                        slot_value['날짜'] = val

                    print(slot_value, '##채워졋나확인')

# 전에 입력했던 값이 있으면 전에 입력했던 slot_value를 불러와서 채우기
    if pre_user_intent_id in ['항공','패키지','자유','라르고','프리미엄']:
        # slot_value = pre_user_slot_value  # story_slot_entity['항공'] or ['패키지']
        intent_id = []
        for pos_tag in preprocessed:
            if pos_tag[1] in ['NNG', 'NNP', 'NR', 'NNM','OL']:
                if pos_tag[0] in ['해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외','해외'+'항공권','국내항공', '국내항공권','국내항공편','국내비행기', '국내','항공','항공권']:
                    intent_id = "항공"
                elif pos_tag[0] in ['패키지', '패키지관광', '패키지여행', '패키지상품', '해외여행','패키지상품']:
                    intent_id = "패키지"
                elif pos_tag[0] in ['자유여행', '자유', '개별', '개별여행', '자유일정', '자유관광','자유상품','자유여행상품']:
                    intent_id = "자유"
                elif pos_tag[0] in ['라르고','Largo','LARGO','largo']:
                    intent_id = '라르고'
                elif pos_tag[0] in ['프리미엄','plus','PLUS','Plus','라르고플러스','플러스']:
                    intent_id = '프리미엄'

    elif pre_user_intent_id == '의도':
        pre_user_intent_id = []
        intent_id = []
        for pos_tag in preprocessed:
            if pos_tag[1] in ['NNG', 'NNP', 'NR', 'NNM','OL']:
                if pos_tag[0] in ['해외항공','해외항공권','해외비행기','해외비행편','해외국적기','해외','국내항공', '국내항공권','국내항공편','국내비행기', '국내','항공','항공권']:
                    pre_user_intent_id = "항공"
                elif pos_tag[0] in ['패키지', '패키지관광', '패키지여행', '패키지상품', '해외여행','패키지상품']:
                    pre_user_intent_id = "패키지"
                elif pos_tag[0] in ['자유여행', '자유', '개별', '개별여행', '자유일정', '자유관광','자유상품','자유여행상품']:
                    pre_user_intent_id = "자유"
                elif pos_tag[0] in ['라르고','Largo','LARGO','largo']:
                    pre_user_intent_id = "라르고"
                elif pos_tag[0] in ['프리미엄','plus','PLUS','Plus','라르고플러스','플러스']:
                    pre_user_intent_id = "프리미엄"
                else:
                    pre_user_intent_id = "의도"

    if intent_id == []:
            intent_id = pre_user_intent_id
            slot_value = pre_user_slot_value  # story_slot_entity['항공'] or ['패키지']
    elif intent_id !=  []:
        slot_value = story_slot_entity[intent_id]
        print(slot_value, '#전 대화 슬롯벨류 안비었을떄 6')
        print(intent_id, '전 대화 인텐트 안비었을떄 7')
        ## 각 의도에 따른 메뉴 장소 숫자 날짜를 슬롯 필링하는 과정

    if intent_id == '항공' or intent_id == '패키지' or intent_id == '자유' or intent_id == '라르고' or intent_id == '프리미엄' or intent_id == '의도':
        for val, pos_tag in preprocessed:
            if (pos_tag) in ['NNG', 'NNP', 'NR', 'NNM', 'OL']:
                if intent_id == '항공':
                    if val in international_air:
                        slot_value['메뉴'] = val
                    elif val in domestic_loc_list:
                        slot_value['장소'] = val
                    elif val in arr_loc_list:
                        slot_value['장소']= val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val

                elif intent_id == '패키지':
                    if val in pkgmenu_list:
                        slot_value['메뉴'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in ['국'] and ['내']:
                        slot_value['장소'] = '국내'
                    elif val in dep_loc_list:
                        slot_value['출발'] = val

                elif intent_id == '자유':
                    if val in freetour_list:
                        slot_value['메뉴'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in ['국'] and ['내']:
                        slot_value['장소'] = '국내'
                    elif val in dep_loc_list:
                        slot_value['출발'] = val

                elif intent_id == '라르고':
                    if val in largo_list:
                        slot_value['메뉴'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in ['국'] and ['내']:
                        slot_value['장소'] = '국내'
                    elif val in dep_loc_list:
                        slot_value['출발'] = val

                elif intent_id == '프리미엄':
                    if val in premuim_list:
                        slot_value['메뉴'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in ['국'] and ['내']:
                        slot_value['장소'] = '국내'
                    elif val in dep_loc_list:
                        slot_value['출발'] = val

                elif intent_id == '의도':
                    if val in pkgmenu_list:
                        slot_value['메뉴'] = val
                    elif val in premuim_list:
                        slot_value['메뉴'] = val
                    elif val in freetour_list:
                        slot_value['메뉴'] = val
                    elif val in largo_list:
                        slot_value['메뉴'] = val
                    elif val in international_air:
                        slot_value['메뉴'] = val
                    elif val in loc_list:
                        slot_value['장소'] = val
                    # elif val in domestic_loc_list:
                    #     slot_value['장소'] = val
                    # elif val in arr_loc_list:
                    #     slot_value['장소'] = val
                    elif val in city_list:
                        slot_value['장소'] = val
                    elif val in ['국'] and ['내']:
                        slot_value['장소'] = '국내'
                    elif val in dep_loc_list:
                        slot_value['출발'] = val

                if val in number_list:
                    slot_value['숫자'] = val
                if val in date_list:
                    slot_value['날짜'] = val

            print(slot_value, '처리후 슬롯벨류')

        ## 3차본 방식과는 다르게 가독성이 좋게 코드를 구현 간단 명료
        ## 의도만 나올경우 output_data에 패키지, 항공, 자유
        ## 의도와 장소가 함께 나올 경우 output_data = 의도 + 장소
        ## 의도, 장소, 숫자, 날짜가 함께 나올경우 날짜항목은 다로 남겨놓고 날짜를 정규화시켜 항공 api에 파라미터를 전달해야됨
        if intent_id == '패키지' or intent_id == '항공' or intent_id == '자유' or intent_id == '라르고' or intent_id == '프리미엄' or intent_id == '의도':
            # if slot_value['메뉴'] in inter_air and slot_value['장소'] == None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
            #     intent_id = intent_id
            #     output_data = '해외항공'
            # elif slot_value['메뉴'] in dome_air and slot_value['장소'] == None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
            #     intent_id = intent_id
            #     output_data = '국내항공'
            # Only 메뉴 ## 해외항공, 국내항공, 그냥 항공권 입력 세단계 구분
            if slot_value['메뉴'] != None and slot_value['장소'] == None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
                ## 메뉴만들어오는경우에서 항공일경우 해외항공, 국내항공, 항공으로 나눠서 각각 다른 파라미터를 던져 다른 질문형식을 노출할 수 있게끔 수정
                if intent_id == '항공' and slot_value['메뉴'] in inter_air:
                    output_data = '해외항공'
                elif intent_id == '항공' and slot_value['메뉴'] in dome_air:
                    output_data = '국내항공'
                else:
                    output_data = intent_id
            # elif slot_value['메뉴'] == '항공' and slot_value['장소'] != None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
            #     intent_id = '항공'+'장소'
            #     output_data = slot_value['장소']

            # Only 메뉴랑 장소
            elif slot_value['메뉴'] != None and slot_value['장소'] != None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
                intent_id = intent_id + '장소'
                output_data = slot_value['장소']

            # ## Only 메뉴 장소 숫자 날짜 모두 들어왓을 경우 -> 출발 제외##########################################################################################################날짜미완
            # elif slot_value['메뉴'] != None and slot_value['장소'] != None and slot_value['숫자'] != None and slot_value['날짜'] != None and slot_value['출발'] == None:
            #     intent_id = intent_id + '장소' + '날짜'
            #     output_data = slot_value['장소'] + slot_value['숫자'] + slot_value['날짜']

            # 메뉴, 장소, 출발 들어왓을경우
            elif slot_value['메뉴'] != None and slot_value['장소'] != None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] != None:
                intent_id = intent_id + '장소'
                output_data = slot_value['장소']
            # Only 장소
            elif slot_value['메뉴'] == None and slot_value['장소'] != None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] == None:
                output_data = intent_id
                #output_data = '의도'
            # ## Only 장소 숫자 날짜만 들어왓을경우 ####################################################################################################################### 날짜미완
            # elif slot_value['메뉴'] == None and slot_value['장소'] != None and slot_value['숫자'] != None and slot_value['날짜'] != None and slot_value['출발'] == None:
            #     intent_id = '패키지' + '장소'
            #     output_data = slot_value['장소'] + slot_value['숫자'] + slot_value['날짜']

            ## Only 장소, 출발만 들어왓을경우
            elif slot_value['메뉴'] == None and slot_value['장소'] != None and slot_value['숫자'] == None and slot_value['날짜'] == None and slot_value['출발'] != None:
                intent_id = '패키지' + '장소'
                output_data = slot_value['장소']
                print(intent_id, '마지막')
                print(output_data, '마지막')

            # ## Only 장소 숫자 날짜 출발만 들어왓을경우 -> 메뉴제외 #######################################################################################################날짜미완
            # elif slot_value['메뉴'] == None and slot_value['장소'] != None and slot_value['숫자'] != None and slot_value['날짜'] != None and slot_value['출발'] != None:
            #     intent_id = '패키지' + '장소' + '출발'
            #     output_data = slot_value['장소'] + slot_value['숫자'] + slot_value['날짜'] + slot_value['출발']
            response = {
                    "chat_id": request['chat_id'],
                    "message_id": request['message_id'],
                    "intent_id": intent_id,
                    "input_data": request['input_data'],
                    "request_type": "text",
                    "story_slot_entity": slot_value,
                    "output_data": output_data
                }
            print(response)
            response_collect.insert(
                    dict(chat_id=request['chat_id'], message_id=request['message_id'], intent_id=intent_id,
                         input_data=request['input_data'], request_type="text", story_slot_entity=slot_value,
                         output_data=output_data)
                    )
            logging.info(response_collect)
            document = response_collect.find()
            # for doc in document:
            #     print(doc)
            return response