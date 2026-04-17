data(iris)
library(stats)
myiris <- iris
myiris$Species <- NULL
iris.kmeans <- kmeans(myiris, centers=2)
myiris.kmeans <- kmeans(myiris, 3)
table(iris$Species)
#sepal.length 꽃받침길이
#sepal.width 꽃받침폭
#petal.Length 꽃잎길이
# petal.width 꽃잎폭
#3가지 종류 class : setosa, versicolor, virginica
boxplot(as.list(iris[1:50,1:4]), main = "setosa")
boxplot(as.list(iris[51:100, 1:4]), main = "versicolour")
boxplot(as.list(iris[101:150, 1:4]), main = "virginica")
boxplot(sepal.length~species, data=iris)

pairs(iris[1:4], main = "Anderson's Iris Data -- 3pecies", pch = 21, 
      bg = c("red","green3","blue")[unclass(iris$Species)])

table(iris$Species, myiris.kmeans$cluster)
conf.mat <- table(iris$Species, myiris.kmeans$cluster)
(accuracy <- sum(diag(conf.mat))/sum(conf.mat*100))

new.mat <- data.frame("c1"=conf.mat[,1], "c3"=conf.mat[,3], "c2"=conf.mat[,2])
new.mat <- as.matrix(new.mat)
(accuracy <- sum(diag(new.mat))/sum(new.mat)*100)

new.mat <- conf.mat[,c(1,3,2)]

myiris.kmeans

myiris.kmeans$centers

table(iris$Species, myiris.kmeans$cluster)
conf.mat <- table(iris$Species, myiris.kmeans$cluster)
plot(myiris[c("Sepal.Length", "Sepal.Width")], col=myiris.kmeans$cluster)
points(myiris.kmeans$centers[,c("Sepal.Length","Sepal.Width")], col=1:3,
       pch='*', cex= 10)

ave <- 0
for(i in 1:ncol(myiris)) ave[i]<- sum(myiris.kmeans$centers[,i])/nrow(myiris.kmeans$centers)
ave # 출력

km <- kmeans(myiris, centers=3)
ss <- km$withinss

conf.mat <- table(iris$Species, km$cluster)
(accuracy <- sum(diag(conf.mat))/sum(conf.mat)*100)

sim_eu <- dist(myiris, method = "euclidean")
dendrogram <- hclust(sim_eu^2, method = "single") #median, centroid, average, complete
plot(dendrogram)
cluster <- cutree(dendrogram, k=3)
table(iris$Species, cluster)

iris.num <- dim(iris)[1] # nrow(iris) 와 동일
idx <-sample(1:iris.num, 50)
smalliris <- iris[idx,]
smalliris$Species <-NULL
sim <- dist(smalliris)
den <- hclust(sim^2, method="single")
plot(den, hang= -1)
plot(den, hang= -1, labels=iris$Species[idx])