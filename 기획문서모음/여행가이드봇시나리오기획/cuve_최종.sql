-------------------------------------------
-- 현재 큐비 알고리즘
-------------------------------------------

--  전체 로그 데이터에서 연도별로 분리
select *
into tmp_2016_log_data
from vglog..sys_inflow_log
where SEQ_NO >=300000000 and IN_DATE >= '2016-01-01' and IN_DATE < '2016-12-31'

select *
into tmp_2017_log_data
from vglog..sys_inflow_log
where SEQ_NO >=500000000 and IN_DATE >= '2017-01-01' and IN_DATE < '2017-12-31'


create index tmp_2016_log_data
on tmp_2016_log_data(IN_DATE, IN_IP)
include (IN_PATH, IN_QUERY, IN_TYPE1, IN_PRO_CODE, IN_MASTER_CODE);

create index tmp_2017_log_data
on tmp_2016_log_data(IN_DATE, IN_IP)
include (IN_PATH, IN_QUERY, IN_TYPE1, IN_PRO_CODE, IN_MASTER_CODE);


-- 훈련 데이터 전처리

-- 가. 예약 완료에 도달한 로그 데이터 분리
select *
into TMP_RES_COMPLETE_LOG_2016
from tmp_2016_log_data
where IN_PATH LIKE '%Reserve/Package/Complete%'



SELECT
	ROW_NUMBER() OVER(ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC) AS RES_LOG_SEQ
	, X.IN_IP
	, CONVERT(VARCHAR(10), X.IN_DATE, 120) AS IN_DATE
	, DATEPART(WEEK,IN_DATE) AS RES_WEEK
	, X.RES_CODE
	, B.MASTER_CODE
into TMP_RES_COMPLETE_LOG_2016_2
FROM
(
	SELECT IN_IP, IN_DATE, RIGHT(IN_QUERY, LEN(IN_QUERY)-CHARINDEX('=',IN_QUERY)) AS RES_CODE
	FROM TMP_RES_COMPLETE_LOG_2016 a
		
) X

INNER JOIN Diablo..RES_MASTER_damo b WITH(NOLOCK) ON X.RES_CODE = b.RES_CODE
INNER JOIN Diablo..RES_CUSTOMER_damo C WITH(NOLOCK) ON b.RES_CODE = C.RES_CODE

WHERE 
b.RES_STATE < 7 
AND C.RES_STATE = 0 
AND IN_IP NOT LIKE '110.11%' --내부 접속 IP 제거
GROUP BY X.IN_IP, CONVERT(VARCHAR(10),X.IN_DATE,120), DATEPART(WEEK,IN_DATE),X.RES_CODE, b.MASTER_CODE
ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC



-- 나. 상품열람 횟수가 극단값에 해당하는 Data를 제거하기 위한 CTE문
WITH LIST AS    
	(
		SELECT B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
		FROM tmp_2016_log_data A --2016년의 모든 로그가 담긴 테이블
		INNER JOIN TMP_RES_COMPLETE_LOG_2016_2 B -- [나]에서 분류한 실예약로그와 JOIN 
		ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK --예약완료한 주차와 동일 아이피의 상세 열람상품을 조회
		WHERE 
		A.IN_PRO_CODE IS NOT NULL --상품상세페이지 열람로그로 조건 한정
		GROUP BY 
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE
		HAVING COUNT(*) < 25 -- 25회 이상 상품을 바꿔가며 조회한 DATA는 생략(상위,하위 5%를 제외한 절사평균 기준)
	) 


SELECT RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK, SEQ, OPEN_MASTER
into TMP_RES_RESULT_PROCESS_LOG_2016
FROM
(
	SELECT 
	B.RES_LOG_SEQ, 
	B.IN_IP, 
	B.IN_DATE,
	B.RES_WEEK AS OPEN_WEEK,
	DENSE_RANK() OVER (PARTITION BY A.IN_IP, DATEPART(WEEK, A.IN_DATE) ORDER BY A.IN_DATE) AS SEQ,
	SUBSTRING(A.IN_PRO_CODE, 0, CHARINDEX('-', IN_PRO_CODE)) AS OPEN_MASTER

	FROM tmp_2016_log_data A
		
	INNER JOIN TMP_RES_COMPLETE_LOG_2016_2 B ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK
	INNER JOIN LIST C ON A.IN_IP = C.IN_IP AND DATEPART(WEEK,A.IN_DATE) = C.RES_WEEK
		
	WHERE 
	A.IN_PRO_CODE IS NOT NULL
	
) K 
	
WHERE OPEN_MASTER <> ''
GROUP BY RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK,SEQ,OPEN_MASTER
ORDER BY RES_LOG_SEQ , IN_IP, IN_DATE, SEQ




-- 다. 연관규칙을 위해 데이터 형태 변경
SELECT A.MASTER_CODE, B.IN_IP, B.OPEN_WEEK, B.OPEN_MASTER
INTO #TEMP
FROM 
TMP_RES_COMPLETE_LOG_2016_2 A
INNER JOIN TMP_RES_RESULT_PROCESS_LOG_2016 B ON A.RES_LOG_SEQ = B.RES_LOG_SEQ 
GROUP BY A.MASTER_CODE, B.IN_IP, B.OPEN_WEEK, B.OPEN_MASTER
ORDER BY OPEN_WEEK, IN_IP

SELECT * FROM #TEMP
ORDER BY OPEN_WEEK, IN_IP



SELECT MASTER_CODE, B.IN_IP, B.OPEN_WEEK, REPLACE(B.OPEN_MASTER,' ','') AS OPEN_MASTER
INTO TMP_APORIORI_DATA
FROM
(
	SELECT MASTER_CODE, IN_IP, OPEN_WEEK,
	STUFF((
	SELECT ',' + OPEN_MASTER
			FROM #TEMP A
			WHERE A.IN_IP = B.IN_IP AND A.MASTER_CODE= B.MASTER_CODE and A.OPEN_WEEK = B.OPEN_WEEK
			FOR XML PATH('')
			),1,1,'') AS OPEN_MASTER
	FROM #TEMP B
	GROUP BY MASTER_CODE,OPEN_WEEK, IN_IP
) B

WHERE 
B.OPEN_MASTER LIKE '%,%' -- 1개 이상의 페이지를 열어본 경우로 한정



-- 라. R에서 연관규칙 실행

/*
#install.packages('RODBC')
library(arules) #aporiori 알고리즘 이용하는 패키지
library('RODBC') #sql 이용하는 패키지


con = odbcConnect('TEST_CUVE', uid='sa', pwd='ckawhgdms@!**4000') #서버에 연결
rm(a)
# 변수 a에 마스터코드 전체를 담는다. 

a <- as.data.frame(sqlQuery(con, 
                            "select b.master_code
                            from  
                            (
                            SELECT lower(MASTER_CODE) as master_code, count(*) as cnt 
                            FROM TMP_RES_COMPLETE_LOG_2016_2
                            group by master_code
                            ) b
                            where b.cnt >= 5"))    # 실예약건이 5개 이상인 마스터만 추출(분석을 위한 데이터수량 확보)
result <- NULL

for(i in 1:NROW(a)) {
  b <-  (sqlQuery(con, 
                  paste("SELECT
                        OPEN_MASTER
                        FROM 
                        TMP_APORIORI_DATA
                        WHERE MASTER_CODE ='",a$master_code[i],"'",sep ='')))
  write.table(b,file="temp_basket.txt",sep=",",row.names=FALSE, quote = FALSE, append=FALSE) #매번 저장시킴
  trans<-read.transactions("temp_basket.txt",format = "basket", sep=",",skip=1,rm.duplicates=TRUE) #skip=1 은 한줄을 건너부터 읽어드리는 인자
  
  c <- apriori(trans,
               parameter = list(supp = 0.001, conf = 0.001, minlen=2, maxlen=3)) # ,
  #appearance = list(default="lhs",rhs=a$master_code[i])) #상품갯수는 최소,최대3개로 기준
  
  c<-sort(c, by="support", decreasing=TRUE)
  options(digits=3) # 소수점 최대 . 이하 3째자리
  
  d <- inspect(head(sort(c, by="support"), 30)) #지지도(비중)기준 상위 30개 불러오기
  
  result <- rbind(result, d)
  
  quries <- paste0("INSERT INTO TMP_RES_RESULT_APORIORI_TEST VALUES('",a$master_code[i],"','",
                   d$lhs,"', '",
                   d$rhs, "',",
                   d$support, ",",
                   d$confidence, ",",
                   d$lift, ")")
  
  for (insertSql in quries)
  {
    sqlQuery(con, insertSql)
    
  }
  
}  
odbcClose(con)  

*/

-- 마. 검증전 전처리 --


WITH LIST AS --R에서 불러올 떄 자동으로 생기는 { } 문자열 제거 
(
	
	SELECT SEQ, [1]+','+[2] AS [1] , 지지도, 예약상품
	FROM
	(
		SELECT
		ROW_NUMBER() OVER (ORDER BY SUPPORT DESC) AS SEQ
		,REPLACE(REPLACE(REPLACE(LHS,' ',''),'{',''),'}','') AS '1'
		,REPLACE(REPLACE(REPLACE(RHS,' ',''),'{',''),'}','') AS '2'
		,REPLACE(SUPPORT,' ','') AS 지지도
		,REPLACE(MASTER_CODE,' ','') AS '예약상품'
		FROM dbo.TMP_RES_RESULT_APORIORI_TEST
	) A


) 
,LIST2 AS 
(
	SELECT P.SEQ, Split.a.value('.', 'varchar(100)') as 마스터코드, P.지지도, P.예약상품
	FROM 
	(
	select SEQ, CAST ('<M>' + REPLACE([1], ',', '</M><M>') + '</M>' AS XML) AS MASTER_CODE, 지지도, 예약상품
	from LIST
	) AS P cross apply MASTER_CODE.nodes ('/M') AS Split(a)
	--WHERE 
	--ISNULL(LIST.[1],'') <> ''  
)
,LIST3 AS
(
 SELECT
 seq, row_number() OVER (PARTITION BY seq ORDER BY SEQ DESC ) AS NO,
 마스터코드,지지도,예약상품 
 FROM LIST2

)

SELECT *
INTO 
	TMP_APRIORI_DATA_CONFIRM_TEST
FROM 
LIST3 A
WHERE 
SEQ NOT IN 
(
	SELECT SEQ 
	FROM LIST3 B 
	WHERE A.SEQ = B.SEQ
	AND LEFT(마스터코드,1) <> LEFT(예약상품,1) -- 고객이 본 상품과 같은 지역의 상품 추천 규칙으로 한정  
)











-- 최종 TRAIN 데이터 
--=================================================================================================================
SELECT * FROM TMP_APRIORI_DATA_CONFIRM_TEST  -- <- 최종형태의 TRAIN 데이터 
where 예약상품 = 'cpp867'
--=================================================================================================================
--drop table #TRAIN_DATA3





--=================================================================================================================
---- 2. TEST DATASET 생성 x  
--=================================================================================================================


--가. 2017년 전체 로그테이블에서 예약완료페이지로만 조건설정 후 별도 테이블 생성

SELECT * 
INTO 
	TMP_RES_COMPLETE_LOG_2017 
FROM 
	TMP_2017_LOG_DATA --전체 로그테이블에서 2017년 로그만 별도 분리한 테이블
WHERE 
	IN_PATH LIKE '%Reserve/Package/Complete%' -- PC예약완료페이지 로그
--모바일예약완료로그 IN_PATH LIKE '%Mobile/Reserve/RegisterForm%' 



--나. 예약완료페이지 로그의 예약코드를 예약테이블과 연결시켜 예약상품을 조회하고, 별도 테이블로 분리

SELECT
	ROW_NUMBER() OVER(ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC) AS RES_LOG_SEQ
	,X.IN_IP
	, CONVERT(VARCHAR(10),X.IN_DATE,120) AS IN_DATE
	, DATEPART(WEEK,IN_DATE) AS RES_WEEK
	, X.RES_CODE
	, B.MASTER_CODE
INTO 
	TMP_RES_COMPLETE_LOG_2017_2
FROM
	(
		SELECT IN_IP, IN_DATE, RIGHT(IN_QUERY,LEN(IN_QUERY)-CHARINDEX('=',IN_QUERY)) AS RES_CODE
		FROM TMP_RES_COMPLETE_LOG_2017 A
		
	) x

	INNER JOIN diablo..RES_MASTER_damo b WITH(NOLOCK) ON X.RES_CODE = b.RES_CODE
	INNER JOIN diablo..RES_CUSTOMER_damo C WITH(NOLOCK) ON B.RES_CODE = C.RES_CODE

WHERE 
	B.RES_STATE < 7 
	AND C.RES_STATE = 0 -- 한 주차에 한 아이피가 여러개의 마스터를 막 예약하는 케이스가 있기 때문에. 실예약한 것으로만 추리기 위해.
	AND IN_IP NOT LIKE '110.11%' --내부 접속 IP 제거
GROUP BY 
	X.IN_IP, CONVERT(VARCHAR(10),X.IN_DATE,120), DATEPART(WEEK,IN_DATE),X.RES_CODE, B.MASTER_CODE
ORDER BY 
	CONVERT(VARCHAR(10),X.IN_DATE,120) ASC




--다. [나]에서 분류되는 실예약건의 상세 상품열람 로그를 조회해서 TEST 데이터로 만듬

WITH LIST AS    -- 상품열람 횟수가 극단값에 해당하는 Data를 제거하기 위한 CTE문
(
	SELECT
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
	FROM 
		TMP_2017_LOG_DATA A --2015년의 모든 로그가 담긴 테이블
		INNER JOIN TMP_RES_COMPLETE_LOG_2017_2 B -- [나]에서 분류한 실예약로그와 JOIN 
		ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK --예약완료한 주차와 동일 아이피의 상세 열람상품을 조회
	WHERE 
		A.IN_PRO_CODE IS NOT NULL --상품상세페이지 열람로그로 조건 한정
	GROUP BY 
		 B.IN_IP
		,B.RES_WEEK
		,B.MASTER_CODE
	HAVING 
		--COUNT(*) < 100 AND COUNT(*) >=3 -- ,3회 미만, 100회 이상 상품을 조회한 DATA는 생략
		count(*) <25
) 


SELECT 
	RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK AS RES_WEEK, SEQ AS [NO], OPEN_MASTER AS 마스터코드, MASTER_CODE AS 예약상품
INTO 
	TMP_2017_LOG_TEST_DATA 

FROM
(
	SELECT 
		B.RES_LOG_SEQ, B.IN_IP, B.IN_DATE
		,B.RES_WEEK AS OPEN_WEEK
		,DENSE_RANK() OVER (PARTITION BY A.IN_IP, DATEPART(WEEK, A.IN_DATE) ORDER BY A.IN_DATE) AS SEQ
		,SUBSTRING(A.IN_PRO_CODE, 0, CHARINDEX('-', IN_PRO_CODE)) AS OPEN_MASTER
		,B.MASTER_CODE
	FROM
		TMP_2017_LOG_DATA A
		INNER JOIN TMP_RES_COMPLETE_LOG_2017_2 B ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK
		INNER JOIN LIST C ON A.IN_IP = C.IN_IP AND DATEPART(WEEK,A.IN_DATE) = C.RES_WEEK
	WHERE 
		A.IN_PRO_CODE IS NOT NULL
	
) K 
	
WHERE 
	OPEN_MASTER <> ''
GROUP BY 
	RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK, SEQ, OPEN_MASTER, MASTER_CODE
ORDER BY
	RES_LOG_SEQ , IN_IP, IN_DATE, SEQ



SELECT * FROM TMP_2017_LOG_TEST_DATA 
ORDER BY RES_LOG_SEQ , [NO] ASC




--라. TEST 데이터에 최종 속성코드 등 추가해서 최종 형태 만듬.

SELECT A.*, B.ATT_CODE, LEFT(B.MASTER_CODE,1) AS REGION 

INTO TMP_2017_LOG_TEST_DATA_city_code 

FROM [dbo].[TMP_2017_LOG_TEST_DATA] A
INNER JOIN Diablo..PKG_MASTER B
ON A.마스터코드 = B.MASTER_CODE



-- 최종 테스트 데이터 형태 
--=================================================================================================================
SELECT * FROM TMP_2017_LOG_TEST_DATA_city_code
ORDER BY RES_LOG_SEQ ,[NO]
--=================================================================================================================
/* 

   추전 적용 기법은 크게 세가지를 혼합시킴. Apriori 알고리즘 , 내용기반필터링, Rule based 추천.
   먼저, Apriori 알고리즘으로 상품별 예약자들의 빈발 조회 상품집합을 찾고 지지도(비중) 를 구해 훈련데이터셋을 만들어 놓는다.
   이후 TEST 유저가 특정 패턴으로 상품을 조회할 경우  과거에 그 패턴과 가장 유사한 패턴을 보인 유저들이 예약한 상품을 TOP N개로 추천한다.
   
   + 

   그러나 위와 같은 추천기법은 고질적인 문제가 있는데, 이는 흔히 cold start라고 불리우는 문제로써 과거 훈련 집합에 없는 신규 상품의 경우
   추천해줄 수 없다는 단점이 있다. 따라서 이와 같은 단점을 해결하기 위하여 Contents based filtering을 추가하였다.
   Contents based filtering은 특정 상품을 조회했을 경우 그 상품과 특성이 가장 유사한 상품을 TOP N 개로 추천해주는 것이다.
   이를 위해 우리는 상품의 상품속성, 대표지역, 패키지/자유여부, 대표도시, 상품가격, 상품일정을 사용하였다. 
   
   + 

   위와 같은 기본적인 추천기법 이외에 여행상품의 특성상 한 상품(MASTER_CODE)에 여러개의 종속행사(IN_PRO_CODE)가 달려 있는데, 
   여러개의 종속된 행사를 조회하는 경우(한 마스터상품의 날짜를 바꿔가며 조회) 해당 마스터상품을 예약하는 확률이 높아진다는 것을 알게됨에 따라 
   3회 이상 연속된 종속 행사를 조회했을 경우 상위 마스터상품을 추천(강조)하는 것을 RULE로 별도 추가하였다. 

   
   ※ 
     일반적으로 비즈니스 추천시스템에서 사용하는 추천기법은 CF(collaborative filtering = user based CF + item based CF)가 대표적이나
     여행상품의 특성상 상품 단가가 높고, 구매주기가 길고 빈도가 적어 구매이력데이터가 희박하며,
	 동시에 복수의 상품을 구매하지 않기 때문에(동시에 여러곳을 여행할 수 없는) CF을 사용하기에 적합하지 않다고 판단하였다.
	 랜덤포레스트나 XGBOOST 알고리즘의 경우 binomial 분류 문제의 경우에는 적합하나 기본적으로 분류해야할 level(상품갯수)이 4천-5천개인 
	 상품시스템에서는 적용하기 어렵다고 판단하였다. 

*/    

-------------------------------------------------------------
select * from TMP_APRIORI_DATA_CONFIRM_TEST where (seq=seq) and (마스터코드=마스터코드) 
select * from TMP_2017_LOG_TEST_DATA order by res_log_seq, no


-- 가.  연관규칙/연관규칙+룰 1개 상품 추천

SET NOCOUNT ON


DECLARE @IN_IP VARCHAR(20)
DECLARE @RES_WEEK INT
DECLARE @마스터코드1 VARCHAR(20)
DECLARE @마스터코드2 VARCHAR(20)
DECLARE @마스터코드3 VARCHAR(20)
DECLARE @추천상품 VARCHAR(20)
DECLARE @정답상품 VARCHAR(20)
DECLARE @상품갯수 INT
DECLARE @TOTAL_COUNT INT
DECLARE @O_COUNT INT
DECLARE @X_COUNT INT

SET @TOTAL_COUNT = 0
SET @O_COUNT = 0
SET @X_COUNT = 0

DECLARE C_USER CURSOR FOR 
	SELECT A.IN_IP, A.RES_WEEK FROM TMP_2017_LOG_TEST_DATA A
	WHERE A.예약상품 IN (SELECT 마스터코드 FROM TMP_APRIORI_DATA_CONFIRM_TEST) -- 2015년과 2016년 마스터코드 갯수 맞추기
	GROUP BY IN_IP, RES_WEEK

OPEN C_USER
FETCH NEXT FROM C_USER INTO  @IN_IP, @RES_WEEK


WHILE @@FETCH_STATUS = 0
BEGIN
	SET @TOTAL_COUNT = @TOTAL_COUNT + 1

	SELECT @마스터코드1 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @마스터코드2 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @마스터코드3 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 3  

	SET @추천상품 = 'X'
	SET @정답상품 = 'O'

	IF (@마스터코드1 = @마스터코드2) AND (@마스터코드2 = @마스터코드3)
	BEGIN
		SET @추천상품 = @마스터코드1
	END
	-------
	ELSE
	BEGIN
		SELECT TOP 1 @추천상품= 예약상품
		FROM (
			SELECT 
				예약상품,
			(	SELECT 
					COUNT(*)
				FROM TMP_APRIORI_DATA_CONFIRM_TEST Z
				WHERE Z.SEQ = A.SEQ AND (
					마스터코드 = @마스터코드1 OR
					마스터코드 = @마스터코드2 OR
					마스터코드 = @마스터코드3
				)
			)  AS 상품갯수,
			지지도
			 FROM TMP_APRIORI_DATA_CONFIRM_TEST A
			WHERE SEQ IN (
				SELECT SEQ FROM TMP_APRIORI_DATA_CONFIRM_TEST
				WHERE 
					마스터코드 = @마스터코드1 OR
					마스터코드 = @마스터코드2 OR
					마스터코드 = @마스터코드3
				GROUP BY SEQ
			)
		) B
		ORDER BY 상품갯수 DESC, 지지도 DESC
	END	

     ------
	-- 추천상품 과  예약상품 같은 지를 판별
	SELECT TOP 1 @정답상품 = 예약상품 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK

	-- 예약상품 == 정답상품
	IF (@추천상품 = @정답상품)
	BEGIN
		PRINT '정답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 + ' / ' + @정답상품
		SET @O_COUNT = @O_COUNT + 1

	END
	ELSE
	BEGIN
		PRINT '오답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 + ' / ' + @정답상품
		SET @X_COUNT = @X_COUNT + 1
	END

	FETCH NEXT FROM C_USER INTO  @IN_IP, @RES_WEEK
END 

PRINT '전체 ' + CAST(@TOTAL_COUNT AS VARCHAR) + ' 중 ' + CAST(@O_COUNT AS VARCHAR) + ' 문제를 맞혔습니다.'
DECLARE @WIN_RATE DECIMAL
SET @WIN_RATE = CAST(@O_COUNT AS DECIMAL) / CAST(@TOTAL_COUNT AS DECIMAL) * 100.0
PRINT '정확도 ' + CAST(@WIN_RATE  AS VARCHAR) + '%'


CLOSE C_USER;
DEALLOCATE C_USER;

SET NOCOUNT OFF








--나. 연관규칙/연관규칙 + 룰 3개 추천 

SET NOCOUNT ON

DECLARE @RES_LOG_SEQ INT
DECLARE @IN_IP VARCHAR(20)
DECLARE @RES_WEEK INT
DECLARE @마스터코드1 VARCHAR(20)
DECLARE @마스터코드2 VARCHAR(20)
DECLARE @마스터코드3 VARCHAR(20)
DECLARE @추천상품 VARCHAR(100)
DECLARE @정답상품 VARCHAR(20)
DECLARE @상품갯수 INT
DECLARE @TOTAL_COUNT INT
DECLARE @O_COUNT INT
DECLARE @X_COUNT INT

SET @TOTAL_COUNT = 0
SET @O_COUNT = 0
SET @X_COUNT = 0


DECLARE C_USER CURSOR FOR 

	SELECT A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK 
	FROM TMP_2017_LOG_TEST_DATA  A
	GROUP BY A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK
	ORDER BY A.RES_LOG_SEQ

OPEN C_USER
FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK


WHILE @@FETCH_STATUS = 0
BEGIN
	SET @TOTAL_COUNT = @TOTAL_COUNT + 1

	SELECT @마스터코드1 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @마스터코드2 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @마스터코드3 = 마스터코드 FROM TMP_2017_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 3

	-----------------------------------------------------------------
	SET @추천상품 = 'X'
	SET @정답상품 = 'O'
	
	IF (@마스터코드1 = @마스터코드2) AND (@마스터코드2 = @마스터코드3)
	BEGIN
	SET @추천상품 = @마스터코드1
	END
	
	ELSE
	-----------------------------------------------------------------

	BEGIN
	
	WITH LIST AS 
	
	(
		
SELECT TOP 3 * FROM (
	SELECT *,
	ROW_NUMBER() OVER(PARTITION BY 예약상품 ORDER BY 상품갯수 DESC, 지지도 DESC) AS RANK_NO
			FROM 
			(
				SELECT 	SEQ, 예약상품,
					(SELECT COUNT(*) FROM TMP_APRIORI_DATA_CONFIRM_TEST Z
						WHERE Z.SEQ = A.SEQ 
						AND (
							마스터코드 = @마스터코드1 OR
							마스터코드 = @마스터코드2 OR
							마스터코드 = @마스터코드3
							)
					)  AS 상품갯수,
				지지도
				 FROM TMP_APRIORI_DATA_CONFIRM_TEST A
				WHERE 
				SEQ IN	(
					SELECT SEQ FROM TMP_APRIORI_DATA_CONFIRM_TEST
					WHERE 
						마스터코드 = @마스터코드1 OR
						마스터코드 = @마스터코드2 OR
						마스터코드 = @마스터코드3
					GROUP BY SEQ
					)
			) B
) C
WHERE C.RANK_NO = 3

	)	
	
	SELECT @추천상품 = 예약상품 
	FROM
	(	
	SELECT T.RANK_NO,
	STUFF((	SELECT ',' + P.예약상품
		FROM LIST P
		WHERE (P.RANK_NO = T.RANK_NO)
		FOR XML PATH('')),1,1,'') AS 예약상품
	FROM LIST T
	) KK
	END	
     ------
	-- 추천상품 과  예약상품 같은 지를 판별
	SELECT TOP 1 @정답상품 = 예약상품 FROM TMP_2017_LOG_TEST_DATA 
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK

	-- 예약상품 == 정답상품
	IF (CHARINDEX(@정답상품,@추천상품) >= 1)
	BEGIN
		PRINT '정답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 + ' / ' + @정답상품
		SET @O_COUNT = @O_COUNT + 1

	END
	ELSE
	BEGIN
		PRINT '오답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 + ' / ' + @정답상품
		SET @X_COUNT = @X_COUNT + 1
	END

	FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK
END 


PRINT '전체 ' + CAST(@TOTAL_COUNT AS VARCHAR) + ' 중 ' + CAST(@O_COUNT AS VARCHAR) + ' 문제를 맞혔습니다.'
DECLARE @WIN_RATE DECIMAL
SET @WIN_RATE = CAST(@O_COUNT AS DECIMAL) / CAST(@TOTAL_COUNT AS DECIMAL) * 100.0
PRINT '정확도 ' + CAST(@WIN_RATE  AS VARCHAR) + '%'


CLOSE C_USER;
DEALLOCATE C_USER;

SET NOCOUNT OFF

select * from tmp_2017_log_test_data_city_code




-- 다. 연관 + 룰 + 컨텐츠 
SET NOCOUNT ON

DECLARE @IN_IP VARCHAR(20)
DECLARE @RES_WEEK INT
DECLARE @마스터코드1 VARCHAR(20)
DECLARE @마스터코드2 VARCHAR(20)
DECLARE @마스터코드3 VARCHAR(20)
DECLARE @추천상품 VARCHAR(100)
DECLARE @정답상품 VARCHAR(20)
DECLARE @상품갯수 INT


DECLARE @RES_LOG_SEQ INT
DECLARE @CITY_CODE1 VARCHAR(20)
DECLARE @CITY_CODE2 VARCHAR(20)
DECLARE @CITY_CODE3 VARCHAR(20)
DECLARE @CITY_CODE4 VARCHAR(20)
DECLARE @CITY_CODE5 VARCHAR(20)
DECLARE @MASTER_CODE VARCHAR(20)
DECLARE @AVG_PRICE VARCHAR(20)
DECLARE @AVG_TOUR_DAY INT
DECLARE @DISTANCE INT
DECLARE @RES_MASTER_CODE  VARCHAR(20)

DECLARE @TOTAL_COUNT INT
DECLARE @O_COUNT INT
DECLARE @X_COUNT INT

DECLARE @ATT_CODE VARCHAR(20)
DECLARE @REGION VARCHAR(20)


SET @TOTAL_COUNT = 0
SET @O_COUNT = 0
SET @X_COUNT = 0

DECLARE C_USER CURSOR FOR 
	
	SELECT 
		A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK 
	FROM 
		dbo.tmp_2017_log_test_data_city_code  A
	GROUP BY 
		A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK
	ORDER BY 
		A.RES_LOG_SEQ

OPEN C_USER
FETCH NEXT FROM C_USER 
INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK


WHILE @@FETCH_STATUS = 0
BEGIN

	SET @TOTAL_COUNT = @TOTAL_COUNT + 1

	SELECT @마스터코드1 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @마스터코드2 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @마스터코드3 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 3

	SELECT @CITY_CODE1 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	SELECT @CITY_CODE2 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 2
	SELECT @CITY_CODE3 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 3
	SELECT @CITY_CODE4 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 4
	SELECT @CITY_CODE5 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 5

	SELECT @AVG_PRICE  = AVG_PRICE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	SELECT @AVG_TOUR_DAY = AVG_TOUR_DAY FROM TMP_CONTENTS_BASED_FILTERING_TEST_2 WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	
	SELECT TOP 1 @ATT_CODE = ATT_CODE FROM dbo.tmp_2017_log_test_data_city_code A WHERE RES_LOG_SEQ =@RES_LOG_SEQ GROUP BY RES_LOG_SEQ, ATT_CODE ORDER BY COUNT(*) DESC
	SELECT TOP 1 @REGION = REGION FROM dbo.tmp_2017_log_test_data_city_code A WHERE RES_LOG_SEQ = @RES_LOG_SEQ GROUP BY RES_LOG_SEQ, REGION ORDER BY COUNT(*) DESC

	----------------------------------------------------------------------------------------------------------------------
	SET @추천상품 = 'X'
	SET @정답상품 = 'O'
	
	IF (@마스터코드1 = @마스터코드2) AND (@마스터코드2 = @마스터코드3)
	BEGIN
		SET @추천상품 = @마스터코드1
	END
	
	ELSE
	----------------------------------------------------------------------------------------------------------------------

	BEGIN
	
	WITH LIST AS 
	
	(
		
		SELECT TOP 2 * 
		FROM 
		(
			SELECT *,
				ROW_NUMBER() OVER(PARTITION BY 예약상품 ORDER BY 상품갯수 DESC, 지지도 DESC) AS RANK_NO
			FROM 
				(
					SELECT 	
						SEQ,
						예약상품,
						(SELECT 
							COUNT(*) 
						 FROM 
							TMP_APRIORI_DATA_CONFIRM_TEST Z
						 WHERE 
							Z.SEQ = A.SEQ 
						 AND (
								마스터코드 = @마스터코드1 OR
								마스터코드 = @마스터코드2 OR
								마스터코드 = @마스터코드3														
							 )
						) AS 상품갯수,
						지지도
					FROM 
						TMP_APRIORI_DATA_CONFIRM_TEST A

					WHERE 
						SEQ IN
							(
							SELECT
								SEQ 
							FROM 
								TMP_APRIORI_DATA_CONFIRM_TEST
							WHERE 
								마스터코드 = @마스터코드1 OR
								마스터코드 = @마스터코드2 OR
								마스터코드 = @마스터코드3

							GROUP BY SEQ
							)
				) B
		) C
	
		WHERE 
			C.RANK_NO = 1
	)	
	

	SELECT 
		@추천상품 = 예약상품 
	FROM
		(	
		SELECT 
			T.RANK_NO,
			STUFF((	
				SELECT 
					',' + P.예약상품
				FROM 
					LIST P
				WHERE 
					(P.RANK_NO = T.RANK_NO)
				FOR XML PATH('')),1,1,'') AS 예약상품
		FROM 
			LIST T
		) KK
	END	


	BEGIN 

	SELECT TOP 1 
		@MASTER_CODE = MASTER_CODE,
		@DISTANCE = CAST(((ABS(@AVG_PRICE-PRICE) / @AVG_PRICE) * 10) AS INT) + ABS(@AVG_TOUR_DAY-TOUR_DAY) + ABS(5-CNT)
	FROM
		(
		SELECT 
			MASTER_CODE,
			REGION_CODE,
			ATT_CODE,
			COUNT(*) AS CNT,
			MAX(LOW_PRICE) AS PRICE,
			MAX(TOUR_DAY) AS TOUR_DAY

		fROM 
			TMP_MASTER_CODE_MAIN_CITY
	
		WHERE 
		  (CITY_CODE = @CITY_CODE1 --'IST'
		OR CITY_CODE = @CITY_CODE2 --'EFF'
		OR CITY_CODE = @CITY_CODE3 -- 'PAM'
		OR CITY_CODE = @CITY_CODE4 -- 'KAP'
		OR CITY_CODE = @CITY_CODE5 -- 'ASR'
		  )
		AND LOW_PRICE IS NOT NULL 
		AND TOUR_DAY IS NOT NULL

		GROUP BY 
			MASTER_CODE,
			ATT_CODE,
			REGION_CODE
		) T 
	WHERE 
		REGION_CODE = @REGION
	AND ATT_CODE = @ATT_CODE
	
	ORDER BY 
		 CAST(((ABS(@AVG_PRICE-PRICE) / @AVG_PRICE) * 10) AS INT)+ ABS(@AVG_TOUR_DAY-TOUR_DAY) + ABS(5-CNT) ASC

	END

	-- 추천상품 과  예약상품 같은 지를 판별

	SELECT TOP 1 
		@정답상품 = 예약상품 
	FROM 
		dbo.tmp_2017_log_test_data_city_code
	WHERE
		RES_LOG_SEQ = @RES_LOG_SEQ

	-- 예약상품 == 정답상품

	IF 
		(CHARINDEX(@정답상품,@추천상품) >= 1) 
	OR	@MASTER_CODE = @정답상품

	BEGIN
		PRINT '정답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 +'+'+ @MASTER_CODE + ' / ' + @정답상품
		SET @O_COUNT = @O_COUNT + 1

	END
	ELSE
	BEGIN
		PRINT '오답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @추천상품 +'+'+ @MASTER_CODE + ' / ' + @정답상품
		SET @X_COUNT = @X_COUNT + 1
	END

	FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK
END 


PRINT '전체 ' + CAST(@TOTAL_COUNT AS VARCHAR) + ' 중 ' + CAST(@O_COUNT AS VARCHAR) + ' 문제를 맞혔습니다.'
DECLARE @WIN_RATE DECIMAL
SET @WIN_RATE = CAST(@O_COUNT AS DECIMAL) / CAST(@TOTAL_COUNT AS DECIMAL) * 100.0
PRINT '정확도 ' + CAST(@WIN_RATE  AS VARCHAR) + '%'


CLOSE C_USER;
DEALLOCATE C_USER;

SET NOCOUNT OFF




-- 라. 

SET NOCOUNT ON

DECLARE @IN_IP VARCHAR(20)
DECLARE @RES_WEEK INT
DECLARE @마스터코드1 VARCHAR(20)
DECLARE @마스터코드2 VARCHAR(20)
DECLARE @마스터코드3 VARCHAR(20)
DECLARE @추천상품 VARCHAR(100)
DECLARE @정답상품 VARCHAR(20)
DECLARE @상품갯수 INT

DECLARE @RES_LOG_SEQ INT
DECLARE @CITY_CODE1 VARCHAR(20)
DECLARE @CITY_CODE2 VARCHAR(20)
DECLARE @CITY_CODE3 VARCHAR(20)
DECLARE @CITY_CODE4 VARCHAR(20)
DECLARE @CITY_CODE5 VARCHAR(20)
DECLARE @MASTER_CODE VARCHAR(20)
DECLARE @AVG_PRICE VARCHAR(20)
DECLARE @AVG_TOUR_DAY INT
DECLARE @DISTANCE INT
DECLARE @RES_MASTER_CODE  VARCHAR(20)

DECLARE @TOTAL_COUNT INT
DECLARE @O_COUNT INT
DECLARE @X_COUNT INT
DECLARE @ATT_CODE VARCHAR(20)
DECLARE @REGION VARCHAR(20)


SET @TOTAL_COUNT = 0
SET @O_COUNT = 0
SET @X_COUNT = 0

DECLARE C_USER CURSOR FOR 
	
	SELECT 
		A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK 
	FROM 
		dbo.tmp_2017_log_test_data_city_code  A
	GROUP BY 
		A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK
	ORDER BY 
		A.RES_LOG_SEQ

OPEN C_USER
FETCH NEXT FROM C_USER 
INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK

WHILE @@FETCH_STATUS = 0
BEGIN

	SET @TOTAL_COUNT = @TOTAL_COUNT + 1

	SELECT @마스터코드1 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code 
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @마스터코드2 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code 
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @마스터코드3 = 마스터코드 FROM dbo.tmp_2017_log_test_data_city_code 
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 3

	SELECT @CITY_CODE1 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	SELECT @CITY_CODE2 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 2
	SELECT @CITY_CODE3 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 3
	SELECT @CITY_CODE4 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 4
	SELECT @CITY_CODE5 = CITY_CODE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 5

	SELECT @AVG_PRICE  = AVG_PRICE FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	SELECT @AVG_TOUR_DAY = AVG_TOUR_DAY FROM TMP_CONTENTS_BASED_FILTERING_TEST_2  WHERE RES_LOG_SEQ = @RES_LOG_SEQ AND RANKING = 1
	
	SELECT TOP 1 @ATT_CODE = ATT_CODE FROM dbo.tmp_2017_log_test_data_city_code A WHERE RES_LOG_SEQ =@RES_LOG_SEQ GROUP BY RES_LOG_SEQ, ATT_CODE ORDER BY COUNT(*) DESC
	SELECT TOP 1 @REGION = REGION FROM dbo.tmp_2017_log_test_data_city_code A WHERE RES_LOG_SEQ = @RES_LOG_SEQ GROUP BY RES_LOG_SEQ, REGION ORDER BY COUNT(*) DESC
	
	----------------------------------------------------------------------------------------------------------------------
	SET @추천상품 = 'X'
	SET @정답상품 = 'O'
	
	IF (@마스터코드1 = @마스터코드2) AND (@마스터코드2 = @마스터코드3)
	BEGIN
		SET @추천상품 = @마스터코드1
	END
	
	ELSE
	----------------------------------------------------------------------------------------------------------------------
	
	BEGIN 

	SELECT TOP 1 
		@MASTER_CODE = MASTER_CODE,
		@DISTANCE = CAST(((ABS(@AVG_PRICE-PRICE) / @AVG_PRICE) * 10) AS INT) + ABS(@AVG_TOUR_DAY-TOUR_DAY) + ABS(5-CNT)
	FROM
		(
		SELECT 
			MASTER_CODE,
			REGION_CODE,
			ATT_CODE,
			COUNT(*) AS CNT,
			MAX(LOW_PRICE) AS PRICE,
			MAX(TOUR_DAY) AS TOUR_DAY

		fROM 
			TMP_MASTER_CODE_MAIN_CITY_TEST
	
		WHERE 
		  (CITY_CODE = @CITY_CODE1 --'IST'
		OR CITY_CODE = @CITY_CODE2 --'EFF'
		OR CITY_CODE = @CITY_CODE3 -- 'PAM'
		OR CITY_CODE = @CITY_CODE4 -- 'KAP'
		OR CITY_CODE = @CITY_CODE5 -- 'ASR'
		  )
		AND LOW_PRICE IS NOT NULL 
		AND TOUR_DAY IS NOT NULL

		GROUP BY 
			MASTER_CODE,
			ATT_CODE,
			REGION_CODE
		) T 
	WHERE 
		REGION_CODE = @REGION
	AND ATT_CODE = @ATT_CODE
	
	ORDER BY 
		 CAST(((ABS(@AVG_PRICE-PRICE) / @AVG_PRICE) * 10) AS INT)+ ABS(@AVG_TOUR_DAY-TOUR_DAY) + ABS(5-CNT) ASC

	END
    ------
	-- 추천상품 과  예약상품 같은 지를 판별

	SELECT TOP 1 
		@정답상품 = 예약상품 
	FROM 
		dbo.tmp_2017_log_test_data_city_code 
	WHERE
		RES_LOG_SEQ = @RES_LOG_SEQ

	-- 예약상품 == 정답상품

	IF 
		(CHARINDEX(@정답상품,@추천상품) >= 1) OR 
		@MASTER_CODE = @정답상품

	BEGIN
		PRINT '정답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @MASTER_CODE + ' / ' + @정답상품
		SET @O_COUNT = @O_COUNT + 1

	END
	ELSE
	BEGIN
		PRINT '오답!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @MASTER_CODE + ' / ' + @정답상품
		SET @X_COUNT = @X_COUNT + 1
	END

	FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK
END 


PRINT '전체 ' + CAST(@TOTAL_COUNT AS VARCHAR) + ' 중 ' + CAST(@O_COUNT AS VARCHAR) + ' 문제를 맞혔습니다.'
DECLARE @WIN_RATE DECIMAL
SET @WIN_RATE = CAST(@O_COUNT AS DECIMAL) / CAST(@TOTAL_COUNT AS DECIMAL) * 100.0
PRINT '정확도 ' + CAST(@WIN_RATE  AS VARCHAR) + '%'


CLOSE C_USER;
DEALLOCATE C_USER;

SET NOCOUNT OFF



select distinct(count(IN_PRO_CODE)) from TMP_2017_LOG_DATA
select * from keyword_log
select * from keyword_best_log

select count(*) from tmp_2017_log_data

select res_log_seq, in_ip, in_date, open_week, open_master, count(open_master) as 'master_count' 
from TMP_RES_RESULT_PROCESS_LOG_2016 
group by res_log_seq, in_ip, in_date, open_week, open_master 
having count(open_master) >0
order by in_ip, master_count desc

