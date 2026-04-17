

-- 전처리 및 데이터 추출 단계는 다른 쿼리에서 노출
-- 보안상의 문제로 검증 쿼리만 업로드

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
