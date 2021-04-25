--=================================================================================================================
-- ť�� �˰��� (2017~8�⵵ ������ ������Ʈ)
--=================================================================================================================

--=================================================================================================================
-- 1. ��ü �α� �����Ϳ��� �������� �и�
--=================================================================================================================

-- 1-1. ������ �α� ������ ���̺� ����

-- Ʈ���̴� ������ (2017.3.1 ~ 2018.2.29)
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

-- �׽�Ʈ ������ (2018.3.1 ~ 2018.10.30)
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


-- 1-2. ������ ���̺� ������ �ֱ�

-- Ʈ���̴� ������
insert into CUVE_2017_log_data
select *
from vglog..sys_inflow_log 
where SEQ_NO >=610000000 and IN_DATE >= '2017-03-01' and IN_DATE < '2018-03-01'
order by SEQ_NO asc

--�׽�Ʈ ������
insert into CUVE_2018_log_data
select *
from vglog..sys_inflow_log 
where SEQ_NO >=800000000 and IN_DATE >= '2018-03-01' and IN_DATE < '2018-11-01'
order by SEQ_NO asc


-- 1-3. Ʈ���̴� �� �׽�Ʈ ������ ���̺� �ε��� ����

-- Ʈ���̴� ������ ���̺� �ε��� ����
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

-- �׽�Ʈ ������ ���̺� �ε��� ����
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
-- 2. Ʈ���̴� ������ ��ó��
--=================================================================================================================

-- 2-1. ���� �Ϸῡ ������ �α� ������ �и�
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
AND IN_IP NOT LIKE '110.11%' --���� ���� IP ����
GROUP BY X.IN_IP, CONVERT(VARCHAR(10),X.IN_DATE,120), DATEPART(WEEK,IN_DATE),X.RES_CODE, b.MASTER_CODE
ORDER BY CONVERT(VARCHAR(10),X.IN_DATE,120) ASC

-- 2-2. ��ǰ���� Ƚ���� �شܰ��� �ش��ϴ� Data�� �����ϱ� ���� CTE��
WITH LIST AS    
	(
		SELECT B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
		FROM CUVE_2017_log_data A --2017���� ��� �αװ� ��� ���̺�
		INNER JOIN TMP_RES_COMPLETE_LOG_2017_2 B -- [��]���� �з��� �ǿ���α׿� JOIN 
		ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK --����Ϸ��� ������ ���� �������� �� ������ǰ�� ��ȸ
		WHERE 
		A.IN_PRO_CODE IS NOT NULL --��ǰ�������� �����α׷� ���� ����
		GROUP BY 
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE
		HAVING COUNT(*) < 25 -- 25ȸ �̻� ��ǰ�� �ٲ㰡�� ��ȸ�� DATA�� ����(����,���� 5%�� ������ ������� ����)
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

-- 2-3. ������Ģ�� ���� ������ ���� ����
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
B.OPEN_MASTER LIKE '%,%' -- 1�� �̻��� �������� ��� ���� ����

-- 2-4. ����׸� ���� ����� ������ ���̺� ����
CREATE TABLE CUVE_RES_RESULT_APORIORI
(	MASTER_CODE VARCHAR(20),
	lhs VARCHAR(100),
	rhs VARCHAR(100),
	support numeric(18,15),
	confidence numeric(18,15),
	lift numeric(18,15)
)

-- 2-5. R���� ������Ģ ����

/*
#install.packages('RODBC')
library(arules) #aporiori �˰��� �̿��ϴ� ��Ű��
library('RODBC') #sql �̿��ϴ� ��Ű��


con = odbcConnect('ť��', uid='sa', pwd='ckawhgdms@!**4000') #������ ����
rm(a)
# ���� a�� �������ڵ� ��ü�� ��´�. 

a <- as.data.frame(sqlQuery(con, 
                            "select b.master_code
                            from  
                            (
                            SELECT lower(MASTER_CODE) as master_code, count(*) as cnt 
                            FROM TMP_RES_COMPLETE_LOG_2017_2
                            group by master_code
                            ) b
                            where b.cnt >= 5"))    # �ǿ������ 5�� �̻��� �����͸� ����(�м��� ���� �����ͼ��� Ȯ��)
result <- NULL

for(i in 1:NROW(a)) {
  b <-  (sqlQuery(con, 
                  paste("SELECT
                        OPEN_MASTER
                        FROM 
                        CUVE_APORIORI_DATA
                        WHERE MASTER_CODE ='",a$master_code[i],"'",sep ='')))
  write.table(b,file="temp_basket.txt",sep=",",row.names=FALSE, quote = FALSE, append=FALSE) #�Ź� �����Ŵ
  trans<-read.transactions("temp_basket.txt",format = "basket", sep=",",skip=1,rm.duplicates=TRUE) #skip=1 �� ������ �ǳʺ��� �о�帮�� ����
  
  c <- apriori(trans,
               parameter = list(supp = 0.001, conf = 0.001, minlen=2, maxlen=3)) # ,
  #appearance = list(default="lhs",rhs=a$master_code[i])) #��ǰ������ �ּ�,�ִ�3���� ����
  
  c<-sort(c, by="support", decreasing=TRUE)
  options(digits=3) # �Ҽ��� �ִ� . ���� 3°�ڸ�
  
  d <- inspect(head(sort(c, by="support"), 30)) #������(����)���� ���� 30�� �ҷ�����
  
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


-- 2-6. ������ ���� ������Ģ ��� ������ ����

WITH LIST AS --R���� �ҷ��� �� �ڵ����� ����� { } ���ڿ� ���� 
(
	
	SELECT SEQ, [1]+','+[2] AS [1] , ������, �����ǰ
	FROM
	(
		SELECT
		ROW_NUMBER() OVER (ORDER BY SUPPORT DESC) AS SEQ
		,REPLACE(REPLACE(REPLACE(LHS,' ',''),'{',''),'}','') AS '1'
		,REPLACE(REPLACE(REPLACE(RHS,' ',''),'{',''),'}','') AS '2'
		,REPLACE(SUPPORT,' ','') AS ������
		,REPLACE(MASTER_CODE,' ','') AS '�����ǰ'
		FROM dbo.CUVE_RES_RESULT_APORIORI
	) A


) 
,LIST2 AS 
(
	SELECT P.SEQ, Split.a.value('.', 'varchar(100)') as �������ڵ�, P.������, P.�����ǰ
	FROM 
	(
	select SEQ, CAST ('<M>' + REPLACE([1], ',', '</M><M>') + '</M>' AS XML) AS MASTER_CODE, ������, �����ǰ
	from LIST
	) AS P cross apply MASTER_CODE.nodes ('/M') AS Split(a)
	--WHERE 
	--ISNULL(LIST.[1],'') <> ''  
)
,LIST3 AS
(
 SELECT
 seq, row_number() OVER (PARTITION BY seq ORDER BY SEQ DESC ) AS NO,
 �������ڵ�,������,�����ǰ 
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
	AND LEFT(�������ڵ�,1) <> LEFT(�����ǰ,1) -- ���� �� ��ǰ�� ���� ������ ��ǰ ��õ ��Ģ���� ����  
)


--=================================================================================================================
-- 3. �׽�Ʈ ������ ��ó��
--=================================================================================================================

-- 3-1. �׽�Ʈ ������ �α����̺��� ����Ϸ��������θ� ���Ǽ��� �� ���� ���̺� ����

SELECT * 
INTO 
	TMP_RES_COMPLETE_LOG_2018 
FROM 
  CUVE_2018_log_data --��ü �α����̺��� 2017�� �α׸� ���� �и��� ���̺�
WHERE 
	IN_PATH LIKE '%Reserve/Package/Complete%' -- PC����Ϸ������� �α�
--����Ͽ���Ϸ�α� IN_PATH LIKE '%Mobile/Reserve/RegisterForm%' 


-- 3-2. ����Ϸ������� �α��� �����ڵ带 �������̺�� ������� �����ǰ�� ��ȸ�ϰ�, ���� ���̺�� �и�
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
	AND C.RES_STATE = 0 -- �� ������ �� �����ǰ� �������� �����͸� �� �����ϴ� ���̽��� �ֱ� ������. �ǿ����� �����θ� �߸��� ����.
	AND IN_IP NOT LIKE '110.11%' --���� ���� IP ����
GROUP BY 
	X.IN_IP, CONVERT(VARCHAR(10),X.IN_DATE,120), DATEPART(WEEK,IN_DATE),X.RES_CODE, B.MASTER_CODE
ORDER BY 
	CONVERT(VARCHAR(10),X.IN_DATE,120) ASC


-- 3-3. [3-2]���� �з��Ǵ� �ǿ������ �� ��ǰ���� �α׸� ��ȸ�ؼ� TEST �����ͷ� ����

WITH LIST AS    -- ��ǰ���� Ƚ���� �شܰ��� �ش��ϴ� Data�� �����ϱ� ���� CTE��
(
	SELECT
		B.IN_IP, B.RES_WEEK, B.MASTER_CODE, COUNT(*) AS CNT
	FROM 
		CUVE_2018_log_data A --2017���� ��� �αװ� ��� ���̺�
		INNER JOIN TMP_RES_COMPLETE_LOG_2018_2 B -- [��]���� �з��� �ǿ���α׿� JOIN 
		ON A.IN_IP = B.IN_IP AND DATEPART(WEEK,A.IN_DATE) = B.RES_WEEK --����Ϸ��� ������ ���� �������� �� ������ǰ�� ��ȸ
	WHERE 
		A.IN_PRO_CODE IS NOT NULL --��ǰ�������� �����α׷� ���� ����
	GROUP BY 
		 B.IN_IP
		,B.RES_WEEK
		,B.MASTER_CODE
	HAVING 
		--COUNT(*) < 100 AND COUNT(*) >=3 -- ,3ȸ �̸�, 100ȸ �̻� ��ǰ�� ��ȸ�� DATA�� ����
		count(*) <25
) 


SELECT 
	RES_LOG_SEQ, IN_IP, IN_DATE, OPEN_WEEK AS RES_WEEK, SEQ AS [NO], OPEN_MASTER AS �������ڵ�, MASTER_CODE AS �����ǰ
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
-- 4. ���� (������Ģ + ��Ģ���) : 1, 3, 5�� ��õ
--=================================================================================================================

SET NOCOUNT ON

DECLARE @RES_LOG_SEQ INT
DECLARE @IN_IP VARCHAR(20)
DECLARE @RES_WEEK INT
DECLARE @�������ڵ�1 VARCHAR(20)
DECLARE @�������ڵ�2 VARCHAR(20)
DECLARE @�������ڵ�3 VARCHAR(20)
DECLARE @��õ��ǰ VARCHAR(100)
DECLARE @�����ǰ VARCHAR(20)
DECLARE @��ǰ���� INT
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

	SELECT @�������ڵ�1 = �������ڵ� FROM CUVE_2018_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 1

	SELECT @�������ڵ�2 = �������ڵ� FROM CUVE_2018_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 2

	SELECT @�������ڵ�3 = �������ڵ� FROM CUVE_2018_LOG_TEST_DATA
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK AND NO = 3

	-----------------------------------------------------------------
	SET @��õ��ǰ = 'X'
	SET @�����ǰ = 'O'
	
	IF (@�������ڵ�1 = @�������ڵ�2) AND (@�������ڵ�2 = @�������ڵ�3)
	BEGIN
	SET @��õ��ǰ = @�������ڵ�1
	END
	
	ELSE
	-----------------------------------------------------------------

	BEGIN
	
	WITH LIST AS 
	
	(
		
SELECT TOP 1 * FROM (
	SELECT *,
	ROW_NUMBER() OVER(PARTITION BY �����ǰ ORDER BY ��ǰ���� DESC, ������ DESC) AS RANK_NO
			FROM 
			(
				SELECT 	SEQ, �����ǰ,
					(SELECT COUNT(*) FROM CUVE_APRIORI_DATA_FINAL Z
						WHERE Z.SEQ = A.SEQ 
						AND (
							�������ڵ� = @�������ڵ�1 OR
							�������ڵ� = @�������ڵ�2 OR
							�������ڵ� = @�������ڵ�3
							)
					)  AS ��ǰ����,
				������
				 FROM CUVE_APRIORI_DATA_FINAL A
				WHERE 
				SEQ IN	(
					SELECT SEQ FROM CUVE_APRIORI_DATA_FINAL
					WHERE 
						�������ڵ� = @�������ڵ�1 OR
						�������ڵ� = @�������ڵ�2 OR
						�������ڵ� = @�������ڵ�3
					GROUP BY SEQ
					)
			) B
) C
WHERE C.RANK_NO = 1

	)	
	
	SELECT @��õ��ǰ = �����ǰ 
	FROM
	(	
	SELECT T.RANK_NO,
	STUFF((	SELECT ',' + P.�����ǰ
		FROM LIST P
		WHERE (P.RANK_NO = T.RANK_NO)
		FOR XML PATH('')),1,1,'') AS �����ǰ
	FROM LIST T
	) KK
	END	
     ------
	-- ��õ��ǰ ��  �����ǰ ���� ���� �Ǻ�
	SELECT TOP 1 @�����ǰ = �����ǰ FROM CUVE_2018_LOG_TEST_DATA 
	WHERE IN_IP = @IN_IP AND RES_WEEK = @RES_WEEK

	-- �����ǰ == �����ǰ
	IF (CHARINDEX(@�����ǰ,@��õ��ǰ) >= 1)
	BEGIN
		PRINT '����!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @��õ��ǰ + ' / ' + @�����ǰ
		SET @O_COUNT = @O_COUNT + 1

	END
	ELSE
	BEGIN
		PRINT '����!! ' + @IN_IP + ' ' + CAST(@RES_WEEK AS VARCHAR) + ' : ' + @��õ��ǰ + ' / ' + @�����ǰ
		SET @X_COUNT = @X_COUNT + 1
	END

	FETCH NEXT FROM C_USER INTO  @RES_LOG_SEQ, @IN_IP, @RES_WEEK
END 


PRINT '��ü ' + CAST(@TOTAL_COUNT AS VARCHAR) + ' �� ' + CAST(@O_COUNT AS VARCHAR) + ' ������ �������ϴ�.'
DECLARE @WIN_RATE DECIMAL
SET @WIN_RATE = CAST(@O_COUNT AS DECIMAL) / CAST(@TOTAL_COUNT AS DECIMAL) * 100.0
PRINT '��Ȯ�� ' + CAST(@WIN_RATE  AS VARCHAR) + '%'


CLOSE C_USER;
DEALLOCATE C_USER;

SET NOCOUNT OFF
