setwd("D:\\netflix")
netflix <- read.csv("NETFLIX_ALL.csv") ##1억개 데이터 다보낸거
library(arules)
library(arulesViz)
library(dplyr)


##테스트셋 형성
sample_num = sample(1:nrow(netflix), size = round(0.2 * nrow(netflix)))

test_netflix = netflix[sample_num,]

##트레인셋 형성
train_netflix = netflix[ -sample_num, ]

##트레인셋 CSV파일로 쓰기(불러올때마다 데이터가 다르기 때문에 결과를 저장하기위해)
write.table(train_netflix, 'train_set.csv', row.names = FALSE, col.names = TRUE, sep = ",")
##테스트셋 CSV파일로 쓰기(불러올때마다 데이터가 다르기 때문에 결과를 저장하기위해)
write.table(test_netflix, 'test_set.csv', row.names = FALSE, col.names = TRUE, sep = ",")

train_netflix <- read.csv("train_set.csv")

test_netflix <- read.csv("test_set.csv")


##CUS_ID중심으로 MOVIE_ID 묶기
netflix.train <- split(train_netflix$MOVIE_ID, train_netflix$CUS_ID)

netflix.train

## 트레인셋을 트랜잭션형태로 변환
netflix_train_tran <- as(netflix.train,"transactions")

## 빈도
itemFrequency(netflix_train_tran)

## 빈발항목집합 측정
netflix_train_EC <- eclat(netflix_train_tran, parameter =list(support=0.2))

inspect(netflix_train_EC)

## 폐쇠항목집합 측정
inspect(netflix_train_EC[!is.closed(netflix_train_EC)])

plot(is.closed(netflix_train_EC))

is.closed(netflix_train_EC)
## 최대항목집합 측정
inspect(netflix_train_EC[!is.maximal(netflix_train_EC)])

plot(is.maximal(netflix_train_EC))

is.maximal(netflix_train_EC)
## APRIORI 연관규칙 생성
netflix_train_AR <- apriori(netflix_train_tran, parameter= list(support = 0.1, smax = 0.2, confidence = 0.2))

inspect(netflix_train_AR)

plot(netflix_train_AR)

plot(netflix_AR)

summary(netflix_train_AR)
## lift 순으로 정렬
rules.sorted <- sort(subset(netflix_train_AR, lift >= 1.0), by="lift")

rules.sorted =  rules.sorted

plot(rules.sorted)

summary(rules.sorted)

rules.sorted = inspect(rules.sorted)
## 만들어진 연관규칙 csv로 보내기
write.table(rules.sorted, 'netflix_train_AR.csv', row.names = FALSE, col.names = TRUE)

write.csv(netflix.list, 'netflix_list.csv', row.names = NULL, col.names = NULL)

write.csv(netflix.list)