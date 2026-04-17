DECLARE @START_DATE DATETIME, @END_DATE DATETIME
SELECT @START_DATE = '2017-01-01', @END_DATE = '2018-01-01';

WITH LIST AS
(
	SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A
	WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE
	UNION ALL 
	SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A
	WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE 
	AND ADDRESS1 IS NOT NULL
	)
	select [거주지], count(*) as 회원수 from
	(
	select cus_no, 
	case
	when ADDRESS1 LIKE  '강원%' then '강원'
	when ADDRESS1 LIKE  '경기%' then '경기'
	when ADDRESS1 LIKE  '경상남%' then '경남'
	when ADDRESS1 LIKE  '경상북%' then '경북'
	when ADDRESS1 LIKE  '광주%' then '광주'
	when ADDRESS1 LIKE  '대구%' then '대구'
	when ADDRESS1 LIKE  '대전%' then '대전'
	when ADDRESS1 LIKE  '부산%' then '부산'
	when ADDRESS1 LIKE  '서울%' then '서울'
	when ADDRESS1 LIKE  '울산%' then '울산'
	when ADDRESS1 LIKE  '인천%' then '인천'
	when ADDRESS1 LIKE  '전라남%' then '전남'
	when ADDRESS1 LIKE  '전라북%' then '전북'
	when ADDRESS1 LIKE  '제주%' then '제주'
	when ADDRESS1 LIKE  '충청남%' OR ADDRESS1 LIKE '세종' then '충남, 세종'
	when ADDRESS1 LIKE  '충청북%' then '충북'
	else '기타' END AS [거주지] FROM LIST
	) T
	GROUP BY [거주지]
	ORDER BY count(*) DESC