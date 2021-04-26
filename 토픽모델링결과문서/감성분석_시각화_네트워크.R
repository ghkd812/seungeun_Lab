####################################################
### 키워드 네트워크 감성분석 (명사, 형용사 포함) ###
####################################################

library(rvest)
library(KoNLP)
library(stringr)
library(tm)
library(qgraph)
library(dplyr)
library(data.table)

## 1. 파일 호출 ##
data <- as.matrix(fread("C:/Users/VGL_P17041/Documents/customer_2019.txt", fill=TRUE, sep="\t", header=FALSE, encoding = "UTF-8"))


## 2. 명사, 형용사 추출 함수 ##
words <- function(doc)
{
  doc <- as.character(doc)
  doc2 <- paste(SimplePos22(doc))
  doc3 <- str_match(doc2, "([가-힣]+)/NC+|([가-힣]+)/PA")
  doc4 <- doc3[,2:3]
  doc4[!is.na(doc4)]
}


## 3. TDM tokenize옵션 작동안해서 수동 작업 ##

# 3-1. 한 문장 안에서 명사, 형용사만 추출하여 이어붙이기
x <- sapply(data, words, USE.NAMES = F)
x2 <- sapply(x, paste, collapse=" ")

# 3-2. 명사, 형용사만 이어붙인 문장 write
write.table(x2, "C:/Users/VGL_P17041/Documents/customer_2018_1.txt", sep = ",", row.names = FALSE, quote = FALSE)



## 4. TDM 생성 ##   *한글깨짐이 발생하기 때문에 3-2 먼저 수행  

# 4-1. 명사, 형용사로 이어붙인 파일 호출  
data_ncpa <- as.matrix(read.csv("C:/Users/VGL_P17041/Documents/customer_2019.csv", fill=TRUE, sep="\t", header=FALSE))

# 4-2. 말뭉치 생성
corpus <- Corpus(VectorSource(data_ncpa))

# 4-3. 불용어 처리
stopWord <- c("상품","참좋은여행","진행","생각","이번","다르","사람","어떻","마이페이지","궁금","동유럽","여행사"
              ,"안녕","그렇")

# 4-4. TDM 생성 
tdm <- TermDocumentMatrix(corpus, control=list(removePunctuation=TRUE, 
                                               removeNumbers=TRUE, 
                                               wordLengths=c(4, 20), 
                                               weighting=weightBin,
                                               stopwords = stopWord))


## 5. 메트릭스로 변경 후 빈도수 top 30만 추출 ##
tdm.matrix <- as.matrix(tdm)

word.count <- rowSums(tdm.matrix)

word.order <- order(word.count, decreasing=TRUE)

freq.words <- tdm.matrix[word.order[1:50], ]

co.matrix <- freq.words %*% t(freq.words)



## 6. 시각화 ##
par(family="Apple SD Gothic Neo")
qgraph(co.matrix, labels=rownames(co.matrix),
       diag=FALSE, layout='spring', threshold=1, edge.color = 'orange',
       vsize=log(diag(co.matrix)) * 2.5)




