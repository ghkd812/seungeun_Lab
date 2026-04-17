
verygood = read.csv("netflix_AP_test_data_all.csv")
library(arules)
library(dplyr)

verygood.list <- split(verygood$MOVIE_ID, verygood$CUS_ID) # 고객을 중심으로 구매list 나누기

verygood.list



## 트레인셋 형성
verygood_train = verygood.list[1:6000][]

## 테스트셋 형성
verygood_test = verygood.list[6001:10000][]

## 트레인셋을 트랜잭션형태로 변환
verygood_train_tran <- as(verygood_train,"transactions")

## 테스트셋을 트랜잭션형태로 변환
verygood_test_tran <- as(verygood_test,"transactions")


#아이템으로 구성 더 자세한 정보를 보기 위해 summary함수 사용

summary(verygood_train_tran)

summary(verygood_test_tran)

itemFrequency(verygood_train_tran)

itemFrequency(verygood_test_tran)

itemFrequency(verygood_train_tran[,1:5])

itemFrequency(verygood_test_tran[,1:5])

itemFrequencyPlot(verygood_train_tran, topN = 5, main = "지지도 상위 top5 항목들")

itemFrequencyPlot(verygood_test_tran, topN = 5, main = "지지도 상위 top5 항목들")

## 트레인데이터를 어프리오리에 대입 = 조건으로 지지도 0.1이상, 신뢰도 0.2이상 최대 집합길이 5로 지정
verygood_train_rules <- apriori(verygood_train_tran, parameter = list(support= 0.11, confidence = 0.837, minlen = 5))

## 테스트데이터를 어프리오리에 대입 = 조건으로 지지도 0.1이상, 신뢰도 0.2이상 최대 집합길이 5로 지정
verygood_test_rules <- apriori(verygood_test_tran, parameter = list(support= 0.11, confidence = 0.837, minlen = 5))


verygood_train_rules <- apriori(verygood_train_tran)

summary(verygood_train_rules)

verygood_test_rules <- apriori(verygood_test_tran)

summary(verygood_test_rules)

summary(verygood_train_rules)

ins_train = inspect(verygood_train_rules)

ins_test = inspect(verygood_test_rules)

ins_train

ins_test

rule_interest <- subset(verygood_train_rules, items %in% c("4996", "16384")) v## 원하는 항목에 대한 규칙만 뽑아낼때 사용

inspect(rule_interest)

write.table(ins_train, 'ins_train.csv', row.names = FALSE, col.names = TRUE)

write.table(ins_test, 'ins_test.csv', row.names = FALSE, col.names = TRUE)

plot(verygood_train_rules, method = "graph")

plot(verygood_test_rules, method = "graph")

plot(verygood_test_rules, control = list(col=brewer.pal(11,"Spectral")),main="")
