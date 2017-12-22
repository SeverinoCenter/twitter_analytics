#set your working directory
setwd("F:/R/crunchbasedata")
rm(list=ls())
options(scipen=999)
library(XML)

df <- read.csv ( 't.csv' , header = T , stringsAsFactors = F )
final <-data.frame()
df$X<-NULL

for (i in 1:length(df$accelerator)){
  company <- df$link[i]
  
  url<-paste("http://www.seed-db.com",company,sep="")

  doc<-htmlParse(url)
  root <- xmlRoot(doc)
  table <- readHTMLTable(doc, header=T,stringsAsFactors=F)
  table<-as.data.frame(table[length(table)])
  #link_button <- xpathSApply(root, "//table/tbody/tr/td[3]/button[1]/a", xmlGetAttr,"href")
  #link<- xpathSApply(root, "//p[1]/a", xmlGetAttr,"href")
  #link<- xpathSApply(root, "//table/tbody/tr/td[3]/a", xmlGetAttr,"href")
  value <- xpathSApply(root, "//table/tbody/tr/td[2]/a", xmlValue)
  table <-cbind(value,table)
  table <- cbind(link, table)
  if (length(table) !=0) {
    table <- cbind (table, df$accelerator[i])
  }
  
  final<-rbind(final,table)
}

final[] <-lapply (final, as.character)
final[4]<-NULL
colnames(final)<- c("link",'company','state','date','exit','cos','funding','accelertor')
write.csv(final, file="startups_seeddb.csv")
