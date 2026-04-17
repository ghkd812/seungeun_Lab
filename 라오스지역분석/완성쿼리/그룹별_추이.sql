with list as (
SELECT
	P.*,
	(
		CASE 										
			WHEN P.출발인원 = 1													THEN 'ALONE'
			WHEN P.출발인원 = 2 AND P.연령차 <=2 AND (P.남성 = 2 OR P.여성 = 2)	THEN 'FRIEND'
			WHEN P.예약팀내최저연령 <= 12 OR P.연령차 >= 20						THEN 'FAMILY'
			WHEN P.출발인원 % 2 = 0 AND P.출발인원 / 2 = P.남성					THEN 'COUPLE'
			WHEN P.출발인원 >= 3													THEN 'MEETING'
			ELSE 'ETC'
		END
	) AS [TOUR_TYPE]
FROM (

		SELECT 										
			A2.MASTER_CODE,
			A2.PRO_CODE,
			A2.RES_CODE,
			MAX(A2.DEP_DATE) AS [DEP_DATE],				
			COUNT(*) AS [출발인원],
			MAX(A2.출발자나이) AS [예약팀최고연령],
			MIN(A2.출발자나이) AS [예약팀내최저연령],
			(MAX(A2.출발자나이) - MIN(A2.출발자나이)) AS [연령차],
			SUM(CASE WHEN A2.출발자성별 = 'F' THEN 1 ELSE 0 END) AS '여성',									
			SUM(CASE WHEN A2.출발자성별 = 'M' THEN 1 ELSE 0 END) AS '남성'								
		FROM (
			SELECT
			A.MASTER_CODE,					
									A.PRO_CODE,					
									A.RES_CODE,					
									A.GENDER AS [예약자성별],
									DATEDIFF(YEAR,A.BIRTH_DATE,A.DEP_DATE) + 1 AS [예약자나이],
									B.CUS_NO AS [출발자고객번호],
									DATEDIFF(YEAR,B.BIRTH_DATE,A.DEP_DATE) + 1 AS [출발자나이],
									B.GENDER AS [출발자성별],
									A.DEP_DATE
			FROM RES_CUSTOMER_DAMO B
			INNER JOIN RES_MASTER_DAMO A ON A.RES_CODE = B.RES_CODE
			INNER JOIN PKG_DETAIL C ON A.PRO_CODE = C.PRO_CODE
			INNER JOIN PRO_TRANS_SEAT D ON C.SEAT_CODE = D.SEAT_CODE
			LEFT JOIN PUB_AIRPORT E ON D.DEP_ARR_AIRPORT_CODE = E.AIRPORT_CODE  
			LEFT JOIN PUB_CITY F ON E.CITY_CODE = F.CITY_CODE 
			LEFT JOIN PUB_NATION G ON F.NATION_CODE = G.NATION_CODE 
			WHERE A.RES_STATE < 7 AND B.RES_STATE = 0
			AND A.PRO_CODE LIKE 'E%'
			AND G.KOR_NAME = '독일'
			AND F.KOR_NAME = '프랑크푸르트'
			AND A.DEP_DATE >= '2019-02-01'
			AND A.DEP_DATE < '2019-06-01'
			AND B.BIRTH_DATE IS NOT NULL
		) A2									
		GROUP BY									
			A2.MASTER_CODE,
			A2.PRO_CODE,								
			A2.RES_CODE
) P
)
select year(a.DEP_DATE), a.TOUR_TYPE, count(*)
from list a
group by grouping sets ((year(a.DEP_DATE), a.TOUR_TYPE)
	, year(a.dep_date)
	, ())
--order by year(a.dep_date), a.TOUR_TYPE

SELECT TOP 100 *
FROM PUB_NATION

SELEC TOP 100 *
