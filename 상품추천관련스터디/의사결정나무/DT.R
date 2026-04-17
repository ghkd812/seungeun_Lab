setwd("D:\\netflix")
tatanic <- read.csv("titanic_raw.csv")

library('data.table')

install.packages("rpart.plot")

##### 타이타닉 전체 데이터 로드(단, crew는 제거) #####
titanic<-read.table('titanic.csv', header = TRUE)


##### 데이터 분리 #####
titanic_dt_test_num <- sample(1:nrow(titanic), size = round(0.3*nrow(titanic)))   # test 데이터로 사용할 번호 추출
titanic_dt_test <- titanic[titanic_dt_test_num, ] # test 데이터 추출
titanic_dt_test <- data.frame(titanic_dt_test) # test 데이터 데이터프레임으로 변경

titanic_dt_training <- titanic[-titanic_dt_test_num,]  # training 데이터 추출
titanic_dt_training <- data.frame(titanic_dt_training) # training 데이터 데이터프레임으로 변경


write.table(titanic_dt_test, "titanic_dt_test.csv", col.names = FALSE, row.names = FALSE)   # test 데이터 내보내기
write.table(titanic_dt_training, "titanic_dt_training.csv", col.names = FALSE, row.names = FALSE)  # training 데이터 내보내기


##### 의사결정나무 모델 생성 #####
titanic_train<-fread('titanic_dt_training.csv', header = FALSE)   # training 데이터 불러오기

library(rpart)  # 의사결정나무 rpart알고리즘 라이브러리 호출

titanic_dt_model <- rpart(titanic_train$V4~., data = titanic_train)  # survive를 기준으로 의사결정나무 실행


library(rpart.plot)
prp(titanic_dt_model, type=4, extra=2, digits=3)   # 생성된 모델 시각화


##### 의사결정나무 모델 검증 ##### 
titanic_test<-fread('titanic_test_data.csv', header = FALSE)  # test 데이터 불러오기

titanic_dt_model_check_temp <- predict(titanic_dt_model, titanic_test)   # predict함수로 모델 검증
titanic_dt_model_check <- as.data.frame(titanic_dt_model_check_temp)   # 검증 결과 데이터 프레임으로 변경



survive_result_all <- c()

for(i in 1:394){
  if(titanic_dt_model_check[i,1]>titanic_dt_model_check[i,2]){
    survive_result_all <- append(survive_result_all, "No") # no타입에 해당할 확률이 더 클경우 no로 지정
  }
  else
    survive_result_all <- append(survive_result_all, "Yes")   # yes타입에 해당할 확률이 더 클경우 yes로 지정
}

survive_result_all <- as.data.frame(survive_result_all) #테스트 데이터 생존 여부 결과 값 데이터 프레임으로 변경  

#모델에 의해 결정된 생존결과와 실제 데이터 비교
count <- 0
for(j in 1:394){
  if(titanic_test$V4[j]==survive_result_all$survive_result_all[j][1]){
    count<-count+1;
  }
}


##### 정확도 결과 #####

# 테스트 데이터 수 : 394
# 정답자 수 : 316
# 정확도 : 80.2%

#######################
