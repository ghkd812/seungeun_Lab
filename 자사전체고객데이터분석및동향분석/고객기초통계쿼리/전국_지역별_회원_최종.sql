DECLARE @START_DATE DATETIME, @END_DATE DATETIME			
SELECT @START_DATE = '2017-01-01', @END_DATE = '2018-01-01';			
			
WITH LIST AS			
(			
	--SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A		
	--WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE		
	--UNION ALL 		
	SELECT CUS_NO, address1 , address2 , zip_code FROM CUS_MEMBER A		
	WHERE NEW_DATE >= @START_DATE AND NEW_DATE < @END_DATE 		
	AND ADDRESS1 IS NOT NULL		
	)		
	select [거주지], count(*) as 회원수 from		
	(		
	select cus_no, 		
	case		
	when ADDRESS1 LIKE  '경기%' OR ADDRESS1 LIKE  '인천%' then '인천, 경기'		
	when ADDRESS1 LIKE  '강원%' then '강원'		
	when ADDRESS1 LIKE  '충청%' then '충청'		
	when ADDRESS1 LIKE  '전라%' then '전라'		
	when ADDRESS1 LIKE  '대구%' OR ADDRESS1 LIKE '경북' then '대구, 경북'		
	when ADDRESS1 LIKE  '부산%' OR ADDRESS1 LIKE  '경남%' OR ADDRESS1 LIKE  '제주%' then '부산, 경남, 제주'		
	when ADDRESS1 LIKE  '서울%' then '서울'		
	else '기타' END AS [거주지] FROM LIST		
	) T		
	GROUP BY [거주지]		
	ORDER BY count(*) DESC		
