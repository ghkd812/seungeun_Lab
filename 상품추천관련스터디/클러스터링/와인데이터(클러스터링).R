wssplot <- function(data, nc=15, seed=1234){
  wss <- (nrow(data)-1)*sum(apply(data,2,var))
  for (i in 2:nc){
    set.seed(seed)
    wss[i] <- sum(kmeans(data, centers=i)$withinss)}
  plot(1:nc, wss, type="b", xlab="Number of Clusters", ylab="Within groups sum of squares")} 
## 와인데이터
data(wine, package="rattle")
head(wine)
## 분석을 시작하기전 scale함수를 통하여 표준화를 수행
df <- scale(wine[-1])

## 그래프를 그려보기위한 함수
wssplot(df)

library(NbClust)
set.seed(1234)
nc <- NbClust(df, min.nc=2, max.nc=15, method="kmeans")
table(nc$Best.n[1,])
## 최적의 군집수를 정하기 위해 사용되는 지수 26개가 계산되고 3을 최적의 군집수로 투표한 결과를 보여준다
barplot(table(nc$Best.n[1,]),
        xlab="Numer of Clusters", ylab="Number of Criteria", main="Number of Clusters Chosen by 26 Criteria") 


set.seed(1234)
fit.km <- kmeans(df, 3, nstart=25) 
fit.km$size
fit.km$centers 

plot(df, col=fit.km$cluster)

points(fit.km$center, col=1:3, pch=8, cex=1.5)

ct.km <- table(wine$Type, fit.km$cluster)

ct.km

aggregate(wine[-1], by=list(cluster=fit.km$cluster), mean)

barplot(ct.km)
clusplot(df, col=fit.km$cluster)
library(flexclust)

randIndex(ct.km)

library(flexclust)
data("Nclus")
plot(Nclus)


cl <- kcca(Nclus, k=4, family=kccaFamily("kmeans"))

image(cl)
points(Nclus)

barplot(cl)

stripes(cl)


library(cclust)
cl.1 <- cclust(Nclus, 4, 20, method="kmeans")
plot(Nclus, col=cl.1$cluster)
points(cl.1$center, col = 1:4, pch = 8, cex=5)

library(cluster)
clusplot(Nclus, cl.1$cluster)

