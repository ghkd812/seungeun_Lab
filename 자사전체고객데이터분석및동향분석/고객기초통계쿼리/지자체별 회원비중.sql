DECLARE @START_DATE DATETIME, @END_DATE DATETIME
SELECT @START_DATE = '2016-01-01', @END_DATE = '2017-01-01';

WITH LIST AS
(
	--SELECT CUS_NO, ZIP_CODE FROM CUS_MEMBER A
	--WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE and LEFT(zip_code,1)=1 AND LEFT(ZIP_CODE,3) <> '12-'
	--SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A
	--WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE and ADDRESS1 LIKE '서울%'
	--UNION ALL 
	SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A
	WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE and ADDRESS1 LIKE '서울%'
)
select [거주지] ,count(*) as 회원수 FROM 
(
SELECT CUS_NO,
 case when address1 like '%송파구%' then '송파'
 when address1 like '%강남구%' then '강남' 
 when address1 like '%서초구%' then '서초' 
 when address1 like '%노원구%' then '노원' 
 when address1 like '%양천구%' then '양천' 
 when address1 like '%강서구%' then '강서' 
 when address1 like '%동작구%' then '동작' 
 when address1 like '%영등포구%' then '영등포' 
 when address1 like '%강동구%' then '강동'
 when address1 like '%구로구%' then '구로'
 when address1 like '%성북구%' then '성북'
 when address1 like '%마포구%' then '마포' 
 when address1 like '%관악구%' then '관악'
 when address1 like '%광진구%' then '광진'
 when address1 like '%은평구%' then '은평'
 when address1 like '%서대문구%' then '서대문'
 when address1 like '%도봉구%' then '도봉'
 when address1 like '%성동구%' then '성동'
 when address1 like '%동대문구%' then '동대문'
 when address1 like '%중랑구%' then '중랑'
 when address1 like '%금천구%' then '금천'
 when address1 like '%중구%' then '중구'
 when address1 like '%용산구%' then '용산'
 when address1 like '%종로구%' then '종로'
 when address1 like '%강북구%' then '강북'
 else '기타' END AS [거주지]  FROM  LIST 
 ) T 
 GROUP BY [거주지] 
 ORDER BY count(*)  DESC  
