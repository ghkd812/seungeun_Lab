--=================================================================================================================
-- 큐비 알고리즘 (2017~8년도 데이터 업데이트)
--=================================================================================================================

--=================================================================================================================
-- 1. 전체 로그 데이터에서 연도별로 분리
--=================================================================================================================

-- 1-1. 연도별 로그 데이터 테이블 생성

-- 트레이닝 데이터 (2017.3.1 ~ 2018.2.29)
create table CUVE_2017_log_data(
	SEQ_NO int,
	IN_DATE datetime,
	IN_IP varchar(20),
	IN_PATH varchar(500),
	IN_URL varchar(1000),
	IN_QUERY VARCHAR(500),
	INFLOW VARCHAR(50),
	IN_TYPE1 VARCHAR(50),
	IN_TYPE2 VARCHAR(50),
	IN_PRO_CODE VARCHAR(100),
	IN_MASTER_CODE VARCHAR(100)
);

-- 테스트 데이터 (2018.3.1 ~ 2018.10.30)
create table CUVE_2018_log_data(
	SEQ_NO int,
	IN_DATE datetime,
	IN_IP varchar(20),
	IN_PATH varchar(500),
	IN_URL varchar(1000),
	IN_QUERY VARCHAR(500),
	INFLOW VARCHAR(50),
	IN_TYPE1 VARCHAR(50),
	IN_TYPE2 VARCHAR(50),
	IN_PRO_CODE VARCHAR(100),
	IN_MASTER_CODE VARCHAR(100)
);


-- 1-2. 생성된 테이블에 데이터 넣기

-- 트레이닝 데이터
insert into CUVE_2017_log_data
select *
from vglog..sys_inflow_log 
where SEQ_NO >=610000000 and IN_DATE >= '2017-03-01' and IN_DATE < '2018-03-01'
order by SEQ_NO asc

--테스트 데이터
insert into CUVE_2018_log_data
select *
from vglog..sys_inflow_log 
where SEQ_NO >=800000000 and IN_DATE >= '2018-03-01' and IN_DATE < '2018-11-01'
order by SEQ_NO asc


-- 1-3. 트레이닝 및 테스트 데이터 테이블에 인덱스 생성

-- 트레이닝 데이터 테이블 인덱스 생성
CREATE NONCLUSTERED INDEX [IDX_2017_LOG_DATA] ON dbo.cuve_2017_log_data
(
	SEQ_NO ASC,
	IN_DATE ASC,
	IN_IP ASC,
	IN_PATH ASC,
	IN_QUERY ASC,
	IN_TYPE1 ASC,
	IN_PRO_CODE ASC,
	IN_MASTER_CODE ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80 ) ON [PRIMARY]
GO

-- 테스트 데이터 테이블 인덱스 생성
CREATE NONCLUSTERED INDEX [IDX_2018_LOG_DATA] ON dbo.cuve_2018_log_data
(
	SEQ_NO ASC,
	IN_DATE ASC,
	IN_IP ASC,
	IN_PATH ASC,
	IN_QUERY ASC,
	IN_TYPE1 ASC,
	IN_PRO_CODE ASC,
	IN_MASTER_CODE ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80 ) ON [PRIMARY]
GO


--=================================================================================================================
-- 2. 트레이닝 데이터 전처리
--=================================================================================================================

-- 2-1. 예약 완료에 도달한 로그 데이터 분리
select *
into TMP_RES_COMPLETE_LOG_2017
from CUVE_2017_log_data
where IN_PATH LIKE '%Reserve/Package/Complete%'


SELECT
	ROW_NUMBER() OVER(ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC) AS RES_LOG_SEQ
	, X.IN_IP
	, CONVERT(VARCHAR(10), X.IN_DATE, 120) AS IN_DATE
	, DATEPART(WEEK,IN_DATE) AS RES_WEEK
	, X.RES_CODE
	, B.MASTER_CODE
into TMP_RES_COMPLETE_LOG_2017_2
FROM
(
	SELECT IN_IP, IN_DATE, RIGHT(IN_QUERY, LEN(IN_QUERY)-CHARINDEX('=',IN_QUERY)) AS RES_CODE
	FROM TMP_RES_COMPLETE_LOG_2017 a
		
) X

INNER JOIN Diablo..RES_MASTER_damo b WITH(NOLOCK) ON X.RES_CODE = b.RES_CODE
INNER JOIN Diablo..RES_CUSTOMER_damo C WITH(NOLOCK) ON b.RES_CODE = C.RES_CODE

WHERE 
b.RES_STATE < 7 
AND C.RES_STATE = 0 
AND IN_IP NOT LIKE '110.11%' --내부 접속 IP 제거
GROUP BY X.IN_IP, CONVERT(VARCHAR(10),X.IN_DATE,120), DATEPART(WEEK,IN_DATE),X.RES_CODE, b.MASTER_CODE
ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC

-- 2-2. 상품열람 횟수가 극단값에 해당하는 Data를 제거하기 위한 CTE문
WITH LIST AS    
	(
		SELECT B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
		FROM CUVE_2017_log_data A --2017년의 모든 로그가 담긴 테이블
		INNER JOIN TMP_RES_COMPLETE_LOG_2017_2 B -- [나]에서 분류한 실예약로그와 JOIN 
		ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK --예약완료한 주차와 동일 아이피의 상세 열람상품을 조회
		WHERE 
		A.IN_PRO_CODE IS NOT NULL --상품상세페이지 열람로그로 조건 한정
		GROUP BY 
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE
		HAVING COUNT(*) < 25 -- 25회 이상 상품을 바꿔가며 조회한 DATA는 생략(상위,하위 5%를 제외한 절사평균 기준)
	) 

SELECT RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK, SEQ, OPEN_MASTER
into TMP_RES_RESULT_PROCESS_LOG_2017
FROM
(
	SELECT 
	B.RES_LOG_SEQ, 
	B.IN_IP, 
	B.IN_DATE,
	B.RES_WEEK AS OPEN_WEEK,
	DENSE_RANK() OVER (PARTITION BY A.IN_IP, DATEPART(WEEK, A.IN_DATE) ORDER BY A.IN_DATE) AS SEQ,
	SUBSTRING(A.IN_PRO_CODE, 0, CHARINDEX('-', IN_PRO_CODE)) AS OPEN_MASTER

	FROM dbo.cuve_2017_log_data A
		
	INNER JOIN TMP_RES_COMPLETE_LOG_2017_2 B ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK
	INNER JOIN LIST C ON A.IN_IP = C.IN_IP AND DATEPART(WEEK,A.IN_DATE) = C.RES_WEEK
		
	WHERE 
	A.IN_PRO_CODE IS NOT NULL
	
) K 
	
WHERE OPEN_MASTER <> ''
GROUP BY RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK,SEQ,OPEN_MASTER
ORDER BY RES_LOG_SEQ , IN_IP, IN_DATE, SEQ

-- 2-3. 연관규칙을 위해 데이터 형태 변경
SELECT A.MASTER_CODE, B.IN_IP, B.OPEN_WEEK, B.OPEN_MASTER
INTO #TEMP1
FROM 
TMP_RES_COMPLETE_LOG_2017_2 A
INNER JOIN TMP_RES_RESULT_PROCESS_LOG_2017 B ON A.RES_LOG_SEQ = B.RES_LOG_SEQ 
GROUP BY A.MASTER_CODE, B.IN_IP, B.OPEN_WEEK, B.OPEN_MASTER
ORDER BY OPEN_WEEK, IN_IP

SELECT * FROM #TEMP1
ORDER BY OPEN_WEEK, IN_IP


SELECT MASTER_CODE, B.IN_IP, B.OPEN_WEEK, REPLACE(B.OPEN_MASTER,' ','') AS OPEN_MASTER
INTO CUVE_APORIORI_DATA
FROM
(
	SELECT MASTER_CODE, IN_IP, OPEN_WEEK,
	STUFF((
	SELECT ',' + OPEN_MASTER
			FROM #TEMP1 A
			WHERE A.IN_IP = B.IN_IP AND A.MASTER_CODE= B.MASTER_CODE and A.OPEN_WEEK = B.OPEN_WEEK
			FOR XML PATH('')
			),1,1,'') AS OPEN_MASTER
	FROM #TEMP1 B
	GROUP BY MASTER_CODE, OPEN_WEEK, IN_IP
) B

WHERE 
B.OPEN_MASTER LIKE '%,%' -- 1개 이상의 페이지를 열어본 경우로 한정

-- 2-4. 빈발항목 집합 결과를 저장할 테이블 생성
CREATE TABLE CUVE_RES_RESULT_APORIORI
(	MASTER_CODE VARCHAR(20),
	lhs VARCHAR(100),
	rhs VARCHAR(100),
	support numeric(18,15),
	confidence numeric(18,15),
	lift numeric(18,15)
)

-- 2-5. R에서 연관규칙 실행

/*
#install.packages('RODBC')
library(arules) #aporiori 알고리즘 이용하는 패키지
library('RODBC') #sql 이용하는 패키지


con = odbcConnect('큐비', uid='sa', pwd='ckawhgdms@!**4000') #서버에 연결
rm(a)
# 변수 a에 마스터코드 전체를 담는다. 

a <- as.data.frame(sqlQuery(con, 
                            "select b.master_code
                            from  
                            (
                            SELECT lower(MASTER_CODE) as master_code, count(*) as cnt 
                            FROM TMP_RES_COMPLETE_LOG_2017_2
                            group by master_code
                            ) b
                            where b.cnt >= 5"))    # 실예약건이 5개 이상인 마스터만 추출(분석을 위한 데이터수량 확보)
result <- NULL

for(i in 1:NROW(a)) {
  b <-  (sqlQuery(con, 
                  paste("SELECT
                        OPEN_MASTER
                        FROM 
                        CUVE_APORIORI_DATA
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
  
  quries <- paste0("INSERT INTO CUVE_RES_RESULT_APORIORI VALUES('",a$master_code[i],"','",
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


-- 2-6. 검증을 위한 연관규칙 결과 데이터 가공

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
		FROM dbo.CUVE_RES_RESULT_APORIORI
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
	CUVE_APRIORI_DATA_FINAL
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


--=================================================================================================================
-- 3. 테스트 데이터 전처리
--=================================================================================================================

-- 3-1. 테스트 데이터 로그테이블에서 예약완료페이지로만 조건설정 후 별도 테이블 생성

SELECT * 
INTO 
	TMP_RES_COMPLETE_LOG_2018 
FROM 
  CUVE_2018_log_data --전체 로그테이블에서 2017년 로그만 별도 분리한 테이블
WHERE 
	IN_PATH LIKE '%Reserve/Package/Complete%' -- PC예약완료페이지 로그
--모바일예약완료로그 IN_PATH LIKE '%Mobile/Reserve/RegisterForm%' 


-- 3-2. 예약완료페이지 로그의 예약코드를 예약테이블과 연결시켜 예약상품을 조회하고, 별도 테이블로 분리
SELECT
	ROW_NUMBER() OVER(ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC) AS RES_LOG_SEQ
	,X.IN_IP
	, CONVERT(VARCHAR(10),X.IN_DATE,120) AS IN_DATE
	, DATEPART(WEEK,IN_DATE) AS RES_WEEK
	, X.RES_CODE
	, B.MASTER_CODE
INTO 
	TMP_RES_COMPLETE_LOG_2018_2
FROM
	(
		SELECT IN_IP, IN_DATE, RIGHT(IN_QUERY,LEN(IN_QUERY)-CHARINDEX('=',IN_QUERY)) AS RES_CODE
		FROM TMP_RES_COMPLETE_LOG_2018 A
		
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


-- 3-3. [3-2]에서 분류되는 실예약건의 상세 상품열람 로그를 조회해서 TEST 데이터로 만듬

WITH LIST AS    -- 상품열람 횟수가 극단값에 해당하는 Data를 제거하기 위한 CTE문
(
	SELECT
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
	FROM 
		CUVE_2018_log_data A --2017년의 모든 로그가 담긴 테이블
		INNER JOIN TMP_RES_COMPLETE_LOG_2018_2 B -- [나]에서 분류한 실예약로그와 JOIN 
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
	CUVE_2018_LOG_TEST_DATA 

FROM
(
	SELECT 
		B.RES_LOG_SEQ, B.IN_IP, B.IN_DATE
		,B.RES_WEEK AS OPEN_WEEK
		,DENSE_RANK() OVER (PARTITION BY A.IN_IP, DATEPART(WEEK, A.IN_DATE) ORDER BY A.IN_DATE) AS SEQ
		,SUBSTRING(A.IN_PRO_CODE, 0, CHARINDEX('-', IN_PRO_CODE)) AS OPEN_MASTER
		,B.MASTER_CODE
	FROM
		CUVE_2018_LOG_DATA A
		INNER JOIN TMP_RES_COMPLETE_LOG_2018_2 B ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK
		INNER JOIN LIST C ON A.IN_IP = C.IN_IP AND DATEPART(WEEK,A.IN_DATE) = C.RES_WEEK
	WHERE 
		A.IN_PRO_CODE IS NOT NULL
	
) K 
	
WHERE 
	OPEN_MASTER <> ''
GROUP BY 
	RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK, SEQ, OPEN_MASTER, MASTER_CODE
ORDER BY
	RES_LOG_SEQ, IN_IP, IN_DATE, SEQ


--=================================================================================================================
-- 4. 검증 (연관규칙 + 규칙기반) : 1, 3, 5개 추천
--=================================================================================================================

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
	FROM CUVE_2018_LOG_TEST_DATA  A
	GROUP BY A.RES_LOG_SEQ, A.IN_IP, A.RES_WEEK
	ORDER BY A.RES_LOG_SEQ

OPEN C_USER
FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK


WHILE @@FETCH_STATUS = 0
BEGIN
	SET @TOTAL_COUNT = @TOTAL_COUNT + 1

	SELECT @마스터코드1 = 마스터코드 FROM CUVE_2018_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @마스터코드2 = 마스터코드 FROM CUVE_2018_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @마스터코드3 = 마스터코드 FROM CUVE_2018_LOG_TEST_DATA
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
		
SELECT TOP 1 * FROM (
	SELECT *,
	ROW_NUMBER() OVER(PARTITION BY 예약상품 ORDER BY 상품갯수 DESC, 지지도 DESC) AS RANK_NO
			FROM 
			(
				SELECT 	SEQ, 예약상품,
					(SELECT COUNT(*) FROM CUVE_APRIORI_DATA_FINAL Z
						WHERE Z.SEQ = A.SEQ 
						AND (
							마스터코드 = @마스터코드1 OR
							마스터코드 = @마스터코드2 OR
							마스터코드 = @마스터코드3
							)
					)  AS 상품갯수,
				지지도
				 FROM CUVE_APRIORI_DATA_FINAL A
				WHERE 
				SEQ IN	(
					SELECT SEQ FROM CUVE_APRIORI_DATA_FINAL
					WHERE 
						마스터코드 = @마스터코드1 OR
						마스터코드 = @마스터코드2 OR
						마스터코드 = @마스터코드3
					GROUP BY SEQ
					)
			) B
) C
WHERE C.RANK_NO = 1

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
	SELECT TOP 1 @정답상품 = 예약상품 FROM CUVE_2018_LOG_TEST_DATA 
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
