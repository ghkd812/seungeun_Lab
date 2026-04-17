
SELECT CUS_KEY , COUNT(*) FROM (
	SELECT TOP 100  A.BIRTH_DATE, A.GENDER, A.CUS_NAME, A.RES_CODE , 
	CONVERT(VARCHAR(10),A.BIRTH_DATE,121) + A.CUS_NAME AS CUS_KEY, 
	A.NOR_TEL1 ,A.NOR_TEL2 ,A.NOR_TEL3 

	FROM RES_CUSTOMER_DAMO A	 -- 행사(상품) 
		INNER JOIN RES_MASTER_DAMO B  -- 예약건(예약자) 
			ON A.RES_CODE = B.RES_CODE
		INNER JOIN PKG_DETAIL C  -- 출발자 
			ON B.PRO_CODE = C.PRO_CODE
		INNER JOIN PRO_TRANS_SEAT D  --좌석정보 
			ON C.SEAT_CODE = D.SEAT_CODE
		-- 부가 정보는 LEFT JOIN 사용 
		LEFT JOIN PUB_AIRPORT E  -- 공항정보 
			ON D.DEP_ARR_AIRPORT_CODE = E.AIRPORT_CODE  
		LEFT JOIN PUB_CITY F  -- 도시정보
			ON E.CITY_CODE = F.CITY_CODE 
		LEFT JOIN PUB_NATION G  -- 국가정보
			ON F.NATION_CODE = G.NATION_CODE 

	--WHERE B.DEP_DATE > GETDATE()  -- 출발하지 않은 ( 출발날짜가 오늘날짜 보다 큰거 ) 
	WHERE B.RES_STATE NOT IN ( 7,8,9 ) -- 정상인 예약건 ( 7,8,9=취소환불이동)
	AND A.RES_STATE = 0 -- 정상인 출발자 
	AND A.BIRTH_DATE IS NOT NULL 
	AND B.PRO_TYPE = 1 -- 패키지 예약만 
	AND F.NATION_CODE = 'LA' 
	AND C.PRO_CODE LIKE 'A%' 
	--AND B.RES_CODE = 'RP1712223898'
	--AND B.DEP_DATE >= '2015-01-01 00:00:00'
	AND B.DEP_DATE >= '2015-01-01 00:00:00'
	AND B.DEP_DATE < '2018-01-01 00:00:00'
) T 
GROUP BY CUS_KEY 
HAVING COUNT(*) > 1 




AND ISNULL(A.BIRTH_DATE,A.BIRTH_DATE) IS NOT NULL
AND ISNULL(A.CUS_NAME,A.CUS_NAME) IS NOT NULL
A.BIRTH_DATE = A.BIRTH_DATE
--AND A.BIRTH_DATE > '1988-01-01'
--AND C.BIRTH_DATE > '1999-01-01'
--ORDER BY B.DEP_DATE 
ORDER BY SALE_PRICE


SELECT TOP 10 *
FROM RES_CUSTOMER

select name, count_1 as "COUNT"
  from (
        select a.*
             , row_number() over (partition by name, birth order by birth) as "COUNT_1"
             , row_number() over (partition by name, phone order by birth) as "COUNT_2"
        from same_people a
       )
 where count_1 = 1
   and count_2 = 1
order by name;