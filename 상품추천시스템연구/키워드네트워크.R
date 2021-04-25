library #
library("RColorBrewer")
library("wordcloud")
library("arules")
library("igraph")
library("ggplot2")
data <- as.matrix(read.csv("customer_r.csv", header = FALSE))
                  
# data #
data = as.matrix(read.csv("C:\\Users\\VGL_P17041\\Documents\\customer.txt", fill=TRUE, sep="\t", header=FALSE))

data = gsub("[^[:alnum:] ]", "", data)

txt = list(); N = nrow(data)
for (i in 1:N) {
  txt[i] = strsplit(data[i], " ")
}


#-------------------------------------------------------------------------------------------------------------#

# frequency analysis #

wordcount = function(x) {
  myword_cloud = as.matrix(unlist(x))
  wc = table(myword_cloud)
  return( list(data=myword_cloud, table=wc))
}

wordcount(data)



# text histogram #
wordhist = function(x, color) {
  y = as.matrix(unlist(x)); y = y[!is.na(y)]
  ggplot(data.frame(y), aes(x=y)) +
    geom_bar(fill=color) +
    theme(text = element_text(size=5)) +
    labs(x="") +
    labs(y="")
}

wordhist(data, "skyblue")

# text plot #

wordplot = function(x) {
  myword_cloud = as.matrix(unlist(x))
  wordcount = table(myword_cloud)
  palete = brewer.pal(7, "Set1")
  wordcloud(names(wordcount), freq=wordcount, scale=c(3,3), random.order=F, random.color=F, colors = palete,
            , max.word=300)
}
wordplot(data)
# text correlation #
wordcor = function(x) {
  word_list = unique(unlist(x)); n_word = length(word_list)
  wordcor = matrix(0, n_word, n_word); rownames(wordcor) = colnames(wordcor) = word_list;
  for (i in 1:length(x)) {
    word_comb = combn(x[[i]], 2)
    for (j in 1:ncol(word_comb)) {
      a = word_comb[1,j]; b = word_comb[2,j]
      wordcor[a,b] = wordcor[b,a] = wordcor[a,b]+1
    }
  }
  diag(wordcor)=0
  return(wordcor)
}

wordcor(data)



# text corrleation plot #
textMatrix = wordcor(data)
index = which(apply(textMatrix, 1, max) >= 30)
tm = textMatrix[names(index),names(index)]


g <- graph.adjacency(tm, weighted=T, mode = "directed", diag=FALSE)

tkplot(g, layout = layout.reingold.tilford, vertex.color = "mistyrose", edge.color = "red",
       edge.arrow.size = 1, vertext.frame.color = "white", background.color = "white", vertex.size = 30,
       vertexlabel.cex = 2, xlim=30, ylim=30, font.size=0.1, bg.color = "white")

