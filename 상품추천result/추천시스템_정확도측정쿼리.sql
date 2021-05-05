

-- ��ó�� �� ������ ���� �ܰ�� �ٸ� �������� ����
-- ���Ȼ��� ������ ���� ������ ���ε�

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
