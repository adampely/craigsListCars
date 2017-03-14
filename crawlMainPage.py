import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import numpy


def crawlMainPage(url = "https://seattle.craigslist.org/search/cto?s=1"):
    #Declare and assign value for apiParam variable here
    #Declare and assign value for outputFormat variable forresponse format in querystring
    r = requests.get(url)
    
    soup = BeautifulSoup(r.content)
    links=[]
    titles=[]
    for item in soup.find_all("a"):
        try:
            if item.get("class")[0] == "result-title":
               links.append(item.get("href"))
               titles.append(item.text)
        except:
            pass
    priceList=soup.findAll('span', {'class' : 'result-meta'})
    prices = []
    for i in priceList:
        priceList2 = i.findAll('span', {'class' : 'result-price'})
        try:
            price = priceList2[0].contents[0]
        except:
            price = None
        prices.append(price)
    print('done')
    return links, titles, prices

links = []
titles = []
prices = []
for carsNum in range(0,100,100):
    url="https://seattle.craigslist.org/search/cto?s="+ str(carsNum)
    linkTmp, titlesTmp, pricesTmp = crawlMainPage()
    links = links + linkTmp
    titles = titles + titlesTmp
    prices = prices + pricesTmp

df = pd.DataFrame()
priceCounter = 0
for link in links:
    mergedUrl = 'https://seattle.craigslist.org' + link
    r = requests.get(mergedUrl)
    soup = BeautifulSoup(r.content)
    count=0
    for item in soup.find_all("p"):
        try:
            if item.get("id") == "display-date":
                dateInAd = item.contents[1].contents[0][:10]
                postingDate = dateInAd
                #postingDate = datetime.datetime.strptime(dateInAd, '%Y-%m-%d').date()
            if item.get("class")[0] == "attrgroup":
                count = count+1
                if count%2==1:
                    parameters = ['title', 'year', 'make', 'model', 'post date', 'price', 'link']
                    postTitle = str(item.contents[1]).replace('<span>','').replace('<b>', '').replace('</span>','').replace('</b>', '')
                    year = postTitle.split()[0]
                    make = postTitle.split()[1]
                    model = postTitle.split()[2:]
                    price = prices[priceCounter]
                    values=[postTitle, year, make, model, postingDate, price, link]
                if count%2==0:
                    for k in item.children:
                        try:
                            parameters.append(str(k.contents[0]).replace(':', ''))
                            values.append(str(k.contents[1]).replace('<','').replace('>','').replace('b','').replace('/',''))
                        except:
                            pass
                    dictionary = dict(zip(parameters, values))
                    df2 = pd.Series(dictionary)
                    df = df.append(df2, ignore_index=True)
        except:
            pass
    priceCounter = priceCounter + 1
df.to_excel('test.xlsx')
print('done')