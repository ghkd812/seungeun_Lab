-- DROP TABLE #TMP_SND_TYPE
CREATE TABLE #TMP_SND_TYPE 
( ID INT , DATA VARCHAR(100) ) 

INSERT INTO #TMP_SND_TYPE 
SELECT ID,DATA FROM DBO.FN_SPLIT('일정표,확정일정표,결제메일,입금안내,전달사항,여행자계약서,예약확정,예약완료,예약취소,회원가입,항공예약완료,항공예약취소,호텔예약완료,호텔예약취소,패스워드전송,포인트적립,포인트사용,포인트소멸,항공예약확정,항공출발완료,여행일정표,호텔결제완료,호텔결제취소,호텔바우처,호텔상세정보,호텔인보이스,상품추천,현금영수증,롯데면세점쿠폰,카드결제메일,포인트결제메일,수배요청,인보이스확정,룰렛이벤트,CTI_ARS,CTI_상담앱,휴면계정',',')
UNION ALL 
SELECT ID+99,DATA FROM DBO.FN_SPLIT('BTMS비밀번호초기화,BTMS호텔예약확정,BTMS호텔예약접수,BTMS호텔예약취소,BTMS호텔바우처,BTMS항공예약확정,BTMS항공예약취소,BTMS기타예약확정,BTMS기타예약취소,BTMS규정위반호텔,BTMS규정위반항공,BTMS온라인상담답변완료,BTMS출장반려,APP정보안내,신세계면세점쿠폰,제2여객터미널_안내,새벽출발_안내',',')
UNION ALL 
SELECT 0,'기타'




SELECT * FROM #TMP_SND_TYPE 


DECLARE @START_DATE DATE = '2018-04-01'
DECLARE @END_DATE DATE = '2018-04-30'

SELECT ( SELECT TOP 1 DATA FROM #TMP_SND_TYPE WHERE ID = A.SND_TYPE) , SND_TYPE, COUNT(*) AS 횟수 ,
 ( SELECT TOP 1 TITLE FROM RES_SND_EMAIL WHERE SND_TYPE = A.SND_TYPE ORDER BY SND_NO DESC) 
FROM RES_SND_EMAIL A
WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE
GROUP BY SND_TYPE
ORDER BY SND_TYPE