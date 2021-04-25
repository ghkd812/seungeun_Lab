

setwd("C:\\Users\\Son\\Desktop")

library(arules)

library(arulesViz)

verygoodIT <- read.csv("구매내역3.csv",as.is=T)

verygoodIT

verygoodIT$구매항목[verygoodIT$고객명=="여승은"]

verygoodIT.목록 <- split(verygoodIT$구매항목, verygoodIT$고객명)

verygoodIT.목록

verygoodIT.목록 <- sapply(verygoodIT.목록,unique)

verygoodIT.tran <- as(verygoodIT.목록, "transactions")

verygoodIT.tran

summary(verygoodIT.tran)

itemFrequency(verygoodIT.tran)

itemFrequency(verygoodIT.tran[,1:5])

itemFrequencyPlot(verygoodIT.tran, support = 0.01, main = "지지도 1% 이상의 항목들")

itemFrequencyPlot(verygoodIT.tran, topN = 5, main = "지지도 상위 tiio 5 항목들")

verygoodIT.rules <- apriori(verygoodIT.tran)

summary(verygoodIT.rules)

inspect(verygoodIT.rules)

verygoodIT.rules <- apriori(verygoodIT.tran, parameter =  list(minlen=2, support= 0.2, confidence = 0.2))

plot(verygoodIT.rules, method = "graph", control = list(type="items"))

plot(verygoodIT.rules, method = "grouped")

plot(verygoodIT.rules, method = "word"

     