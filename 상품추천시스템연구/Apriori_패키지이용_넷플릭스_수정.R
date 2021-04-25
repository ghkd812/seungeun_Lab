install.packages('RODBC') #SQL로 연동하는 패키지 설치 
library(arules) #aporiori 알고리즘 이용하는 패키지
library('RODBC') #sql 이용하는 패키지
library(arulesViz)
library('data.table')

rm(list = ls())
con = odbcConnect('TEST_DB', uid='sa', pwd='ckawhgdms4000')    #182.162.173.89

netflix_movie_order <- sqlQuery(con, "SELECT TOP 1000 MOVIE_ID, CUS_ID FROM tmp_nfx_ibcf_data ORDER BY NEWID();") #고객id정렬 상태로 
as.data.frame(netflix_movie_order)

odbcClose(con)





##############  2. Training 데이터와 Test 데이터 분리 ##############  

##############  1) Train/Test set 생성 ##############  


netflix_ibcf_test_num <- sample(1:nrow(verygood), size = round(0.3*nrow(verygood)))   # test 데이터 추출
netflix_ibcf_training_num <- verygood[-netflix_ibcf_test_num,]  # training 데이터 추출
netflix_ibcf_test <- verygood[netflix_ibcf_test_num, ] 


##############  2) 파일로 내보내기 ##############  
verygood <- netflix_ibcf_test[,-3] # test data 레이팅 정보 삭제
verygood <- netflix_ibcf_test[order(netflix_ibcf_test$CUS_ID,netflix_ibcf_test$MOVIE_ID),]
verygood <- verygood[,c(1,2)] # 열 순서 변경(cus_id, movie_id)

verygood # 조회 

setwd("D:\\netflix")

verygood = read.csv("netflix_AP_test_data_all.csv")

test = read.csv("word.csv")

verygoodtraining = read.csv("netflix_AP_test_data_tran.csv")
  
verygood.목록 <- split(verygood$MOVIE_ID, verygood$CUS_ID) # 고객을 중심으로 구매목록 나누기

verygood.목록

verygoodtraining.목록 <- split(verygoodtraining$MOVIE_ID, verygoodtraining$CUS_ID)

verygoodtraining.목록

verygood.tran <- as(verygood.목록,"transactions")

verygood.tran

verygoodtraining.tran <- as(verygoodtraining.목록, "transactions")

verygoodtraining.tran

#11개의 트랜잭션과 10개의 아이템으로 구성 더 자세한 정보를 보기 위해 summary함수 사용

summary(verygood.tran)

itemFrequency(verygood.tran)

itemFrequency(verygood.tran[,1:10])

itemFrequencyPlot(verygood.tran, topN = 10, main = "지지도 상위 top5 항목들")

verygood.rules <- apriori(verygood.tran, control=list(verbose=F), parameter =  list(minlen= 4, support= 0.2, confidence = 0.2))

summary(verygood.rules)

inspect(verygood.rules)

quality(verygood.rules) <- round(quality(verygood.rules), digits= 3)

verygood.rules.sorted <- sort(verygood.rules, by= "confidence")

inspect(verygood.rules.sorted)

write.table(verygood.rules.sorted, 'verygood.rules', row.names = FALSE, col.names = FALSE)

plot(verygood.rules, method = "graph")

very.predict <- predict.lm(verygood.rules.sorted, netflix_ibcf_training_num)
very

plot(test, method ="wordcloud")

