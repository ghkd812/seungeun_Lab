


#########################################################################################################################################
# diamonds dataset으로 계층적 군집분석 후 군집수를 파악 후 k-means 알고리즘에 적용해 군집파악
library(ggplot2)
head(diamonds)
dim(diamonds) #53940행 10열 짜리 데이터 (양이많음)
#sample
t<-sample(1:nrow(diamonds),1000)
test <-diamonds[t,]

names(test)
#군집 파악용 변수 추출(변수 일부만 추출)
mydia <-test[c("price","carat","depth","table")]
head(mydia)

#계층적 군집작업
result <- hclust(dist(mydia),method = "average")
result
#계층적 군집분석 확인
plot(result,hang=-1)

#비계층적 군집분석 (분할군집) -k=3
result2 <-kmeans(mydia,3)
result2         # 3개의 그룹으로 나눠져있는것을 확인
result2$cluster # 3개의 그룹으로 나눠져있는것을 확인
mydia$Cluster <-result2$cluster
head(mydia)

#변수 간 상관 관계
cor(mydia[, -5], method="pearson")

plot(mydia[, -5])

#corrgram

library(corrgram)
corrgram(mydia[,-5])
corrgram(mydia[,-5],upper.panel = panel.conf)
corrgram(mydia[,-5],lower.panel = panel.conf)

#비계층적 군집 시각화
plot(mydia[(c("carat","price"))],col=mydia$Cluster)

#중심점 표시
points(result2$centers[,c("carat","price")],col=c(1,2,3),pch=8,cex=5)  

# 데이터값만 넣으면 알아서 나눔