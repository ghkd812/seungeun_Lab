install.packages('RODBC') #SQL로 연동하는 패키지 설치 
library(arules) #aporiori 알고리즘 이용하는 패키지
library('RODBC') #sql 이용하는 패키지
library('data.table')

rm(list = ls())
con = odbcConnect('TEST_DB', uid='sa', pwd='ckawhgdms4000')    #182.162.173.89

netflix_movie_order <- sqlQuery(con, "SELECT  CUS_ID, MOVIE_ID FROM tmp_nfx_ibcf_data Order by CUS_ID;") #고객id정렬 상태로 
as.data.frame(netflix_movie_order)

odbcClose(con)





##############  2. Training 데이터와 Test 데이터 분리 ##############  

##############  1) Train/Test set 생성 ##############  
library(dplyr)

netflix_AP_test <- sample(1:nrow(netflix_movie_order), size = round(0.3*nrow(netflix_movie_order)))   # test 데이터 추출
netflix_AP_training <- netflix_movie_order[-netflix_ibcf_test,]  # training 데이터 추출
netflix_AP_test <- netflix_movie_order[netflix_AP_test, ]

getwd()
setwd("D:\\netflix") # 경로설정

write.table(netflix_AP_test, 'netflix_AP_test_data.csv', row.names = FALSE, col.names = TRUE)

write.table(netflix_movie_order, 'netflix_AP_test_data_all.csv', row.names = FALSE, col.names = TRUE)

dt = read.csv("netflix_AP_test_data_all.csv")
dt = data.frame(dt)

dt1 = group_by(dt, dt$CUS_ID) 
dt1 = summarise(dt1) 
t = nrow(dt1)
dt2 = group_by(dt, "MOVIE_ID" = dt$MOVIE_ID) 
dt2 = summarise(dt2, n = n())

dt2$supp = dt2$n/t


dt3 = filter(dt2, supp >= 0.1)

dt4 = 
  
  vec <- c(1, 2, 3, 4, 5)
1 %in% vec # true
10 %in% vec # false
  
  
  
  


