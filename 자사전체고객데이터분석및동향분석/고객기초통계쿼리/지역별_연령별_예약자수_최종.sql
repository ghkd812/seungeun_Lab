DECLARE @START_DATE DATETIME, @END_DATE DATETIME
SELECT @START_DATE = '2017-01-01', @END_DATE = '2018-01-01'

DECLARE @REGION_NAME_LIST VARCHAR(300);
SELECT @REGION_NAME_LIST = STUFF((SELECT ',[' + KOR_NAME + ']' AS [text()] FROM PUB_REGION WITH(NOLOCK) FOR XML PATH('')), 1, 1, ''); 

WITH LIST AS 
( 
 SELECT 
  LEFT(CONVERT(VARCHAR(4),A.DEP_DATE,121),7) AS 출발년도
  ,CASE 
   WHEN LEN(DATEDIFF(YEAR,ISNULL(A.BIRTH_DATE,C.BIRTH_DATE), A.DEP_DATE) + 1) = 1 THEN '0'
   WHEN LEN(DATEDIFF(YEAR,ISNULL(A.BIRTH_DATE,C.BIRTH_DATE), A.DEP_DATE) + 1) = 3 THEN '10'
   ELSE LEFT((DATEDIFF(YEAR,ISNULL(A.BIRTH_DATE,C.BIRTH_DATE), A.DEP_DATE) + 1),1) END AS AGE 
  ,ISNULL(A.GENDER,C.GENDER) AS [GENDER]
  ,(SELECT SIGN_CODE FROM PKG_MASTER WHERE MASTEr_CODE = A.MASTER_CODE ) AS SIGN_CODE 
 FROM RES_MASTER_DAMO A WITH(NOLOCK)
 LEFT JOIN CUS_CUSTOMER C WITH(NOLOCK) ON A.CUS_NO = C.CUS_NO
 WHERE 
 A.DEP_DATE >= @START_DATE 
  AND A.DEP_DATE < @END_DATE 
  AND A.RES_STATE <= 7
  AND A.BIRTH_DATE IS NOT NULL
  AND A.GENDER IS NOT NULL
  AND A.CUS_NO > 1
)
, LIST_2 AS (
 SELECT
   출발년도
  ,CONVERT(INT, 연령대) AS 연령대
  ,여행지역
  ,COUNT(*) AS 인원
 FROM
 (
 SELECT
   A.출발년도
  ,A.GENDER AS [성별]
  ,CASE WHEN A.AGE IN ('7','8','9','10') THEN '7' ELSE A.AGE END AS 연령대
  ,B.KOR_NAME AS [여행지역]
  FROM LIST A
  LEFT JOIN PUB_REGION B WITH(NOLOCK) ON A.SIGN_CODE =B.SIGN
 ) B
 GROUP BY B.출발년도,B.성별,B.연령대,B.여행지역
)
SELECT 
  출발년도, 
  CASE 
  WHEN 연령대 = 0 THEN '10대 미만'
  WHEN 연령대 = 7 THEN '70대 이상'
  ELSE CONVERT(VARCHAR(2), 연령대) + '0대' END AS 연령대,  
 ISNULL([북미지역], '0') AS [북미지역],
 ISNULL([중미지역], '0') AS [중미지역],
 ISNULL([남미지역], '0') AS [남미지역],
 ISNULL([유럽], '0') AS [유럽],
 ISNULL([중동지역], '0') AS [중동지역],
 ISNULL([아프리카], '0') AS [아프리카],
 ISNULL([국내], '0') AS [국내],
 ISNULL([일본], '0') AS [일본],
 ISNULL([중국], '0') AS [중국],
 ISNULL([동남아], '0') AS [동남아],
 ISNULL([대양주], '0') AS [대양주],
 ISNULL([서인도], '0') AS [서인도],
 ISNULL([사이판/괌], '0') AS[사이판/괌],
 ISNULL([극동지역], '0') AS [극동지역],
 ISNULL([기타지역], '0') AS [기타지역]
FROM LIST_2
PIVOT
(
 SUM(인원)
 FOR 
 여행지역 IN ( [북미지역],[중미지역],[남미지역],[유럽],[중동지역],[아프리카],[국내],[일본],[중국],[동남아],[대양주],[서인도],[사이판/괌],[극동지역],[기타지역] )
) PV
ORDER BY 출발년도, LEFT(연령대, 2) ASC
