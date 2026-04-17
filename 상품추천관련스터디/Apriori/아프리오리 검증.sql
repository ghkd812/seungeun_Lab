
select count(*)
from train_set

SELECT TOP 100 *
FROM netflix_train_AR
select *
from APRIORI_RESULT_TEST


-- 여기서 부터 시작 ---------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
with list as
(
-- netflix_train_AR(TRAIN데이터에서 뽑은 연관규칙 테이블)에서 두개항목 집합의 규칙을 TRAIN_SET의 CUS_ID와 조인하여 추천항목을 형성
SELECT top 100
m1.cus_id , ar.lhs1 , ar.lhs2 , ar.rhs, ar.freq
FROM netflix_train_AR ar  
	inner join train_set m1 
		on ar.lhs1 = m1.movie_id 
	inner join test_set m2 
		on ar.lhs2 = m2.movie_id 
		and m1.cus_id = m2.cus_id 
--WHERE ar.lhs1 = 2452 
--and  ar.lhs2 = 14240 
--order by cus_id 
union all
-- netflix_train_AR(TRAIN데이터에서 뽑은 연관규칙 테이블)에서 한개항목 집합의 규칙을 TRAIN_SET의 CUS_ID와 조인하여 추천항목을 형성
SELECT top 100 
m1.cus_id , ar.lhs1 , ar.lhs2 , ar.rhs, ar.freq
FROM netflix_train_AR ar  
	inner join train_set m1 
		on ar.lhs1 = m1.movie_id 
--WHERE ar.lhs1 = 5582 
--and  ar.lhs2 = '' 
--order by cus_id 
)
--CREATE TABLE APRIORI_RESULT(cus_id int, rhs int, freq int) ; -- 고객에게 추천된 상품 테이블 생성
--insert into APRIORI_RESULT -- 고객에게 추천된 상품 데이터 넣기
select TOP 100 cus_id, lhs1, lhs2, rhs, freq --avg(convert(bigint,freq)) as 평균빈도 -- 한사람에게 같은 항목이 여러번 추천되는 경우의 중복 제거
from list
--where rhs = 11521
--group by cus_id, rhs, freq
order by cus_id
-- APRIORI_RESULT 결과 56184604개
--------------------------------------------------------------------
-- TEST_SET의 고객이 본 상품을 중심으로 APRIORI_RESULT(트레인 데이터에서 추천된 데이터) 와 TEST_SET에서 실제로 추천이 되었는지 비교하여 나오는 %로 정확도 측정
CREATE TABLE APRIORI_RESULT_TEST(cus_id INT, rhs int)
insert into APRIORI_RESULT_TEST
SELECT b.cus_id, b.rhs
FROM test_set A
INNER JOIN APRIORI_RESULT B
	ON A.MOVIE_ID = B.rhs AND A.CUS_ID = B.cus_id
	order by a.cus_id
-- 결과 3,859,298 / 테스트셋 20,094,310 = 19%의 정확도C
--------------------------------------------------------------------
-- cus _id별 카운트수를 랭크를 부여하여 탑 파이브만 추천하게끔 하는 쿼리
create table APRIORI_RESULT_TRAIN(cus_id int, rhs int, freq_rank int, freq int)
insert into APRIORI_RESULT_TRAIN_TOP_20
--create table APRIORI_RESULT_TRAIN_TOP_20(cus_id int, rhs int, freq_rank int, freq int)
--create table APRIORI_RESULT_TRAIN_TOP_40(cus_id int, rhs int, freq_rank int, freq int)
--insert into APRIORI_RESULT_TRAIN_TOP_40
create table APRIORI_RESULT_TRAIN_TOP_100(cus_id int, rhs int, freq_rank int, freq int)
insert into APRIORI_RESULT_TRAIN_TOP_100
select *
from
(
SELECT cus_id, rhs,
DENSE_RANK() OVER ( PARTITION BY cus_id ORDER BY freq DESC ) AS freq_rank,
freq
FROM 
(
select cus_id, rhs, freq
from APRIORI_RESULT
	) tbl 
) tt
where freq_rank <= 100
--------------------------------------------------------------------
--CREATE TABLE APRIORI_RESULT_TEST(cus_id INT, rhs int, freq_rank int)
--CREATE TABLE APRIORI_RESULT_TEST_top20(cus_id INT, rhs int, freq_rank int)
--CREATE TABLE APRIORI_RESULT_TEST_top40(cus_id INT, rhs int, freq_rank int)
CREATE TABLE APRIORI_RESULT_TEST_top100(cus_id INT, rhs int, freq_rank int)
insert into APRIORI_RESULT_TEST_top100
SELECT b.cus_id, b.rhs, freq_rank
FROM test_set A
INNER JOIN APRIORI_RESULT_TRAIN_TOP_100 B
	ON A.MOVIE_ID = B.rhs AND A.CUS_ID = B.cus_id
	order by a.cus_id

select *
from APRIORI_RESULT_TEST_top40
ORDER BY cus_id, rhs desc
-- 그냥 전체 추천 결과 3,859,298 / 테스트셋 20,094,310 = 19%의 정확도C
-- 2차 방법 변형 결과 225,247 / 20,094,310 = 1%의 정확도, 1분 11초  탑 5 추천 
-- 3차 방법 변형 767,871 / 20,094,310 = 3.8%의 정확도, 1분 13초  탑 20 추천 3.69
-- 4차 방법 변형 1,378,878 / 20,094,310 = 6.8%의 정확도  1분 23초 탑 40추천 5.8 
-- 5차 방법 변형 1,931,090 / 20,094,310 = 9.6%의 정확도 1분 35초 탑 60 추천 7.1
-- 6차 방법 변형 2,428,465 / 20,094,310 = 12%의 정확도 1분 46초 탑 80 추천 7.3
-- 7차 방법 변형 2,900,937 /20,094,310  = 14%의 정확도 2분 24초 탑 100 추천 6.9
SELECT distinct cus_id 
FROM TEST_SET
---------------------------------------------------------------------

SELECT COUNT(*)
FROM TEST_SET
SELECT 
select top 100 * from test_set
select top 100 * from train_set
select top 100 * from APRIORI_RESULT
select top 100 * from netflix_train_AR
select distinct top 100 * from APRIORI_RESULT 

-- 각 테이블의 인덱스 생성 여부 체크
sp_helpindex netflix_train_AR
sp_helpindex test_set
sp_helpindex APRIORI_RESULT

select top 100 *
from nfx_reserve
-- INDEX 생성 쿼리-------------------------------------------------------------------------------
CREATE NONCLUSTERED INDEX [IDX_train_set_1] ON [dbo].train_set
(
	CUS_ID ASC,
	MOVIE_ID ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IDX_netflix_train_AR_1] ON [dbo].netflix_train_AR
(
	lhs1 ASC,
	lhs2 ASC,
	rhs asc,
	freq asc 
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO


CREATE NONCLUSTERED INDEX [IDX_APRIORI_RESULT_1] ON [dbo].APRIORI_RESULT
(
	cus_id ASC,
	rhs asc,
	freq_rank asc,
	freq asc
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IDX_test_set_1] ON [dbo].test_set
(
	CUS_ID ASC,
	MOVIE_ID ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IDX_NFX_RESERVE_1] ON [dbo].NFX_RESERVE
(
	movie_id ASC,
	rating asc 
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [IDX_train_rating_1] ON [dbo].train_rating
(
	movie_id ASC,
	rating asc 
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 80) ON [PRIMARY]
GO