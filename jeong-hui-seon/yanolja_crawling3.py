from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
from collections import Counter
import re
import csv
import json

# Seleminum으로 웹페이지를 로드한다.
driver = webdriver.Chrome()
driver.get('https://www.yanolja.com/reviews/domestic/3016524')
time.sleep(3) # 페이지 로딩 기다리기

# 스크롤 횟수 설정
scroll_count = 10
for _ in range(scroll_count):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1) # 스크롤 이후 대기


# 웹페이지 소스를 가져온다.
page_source = driver.page_source

# BeautifulSoup를 사용해 HTML을 파싱한다.
soup = BeautifulSoup(page_source, 'html.parser')

# 날짜를 추출한다.
dates = []
date_containers = soup.select('.css-1ivchjf .css-1irbwe1')
for date in date_containers:
    text_date = date.get_text()
    dates.append(text_date)

# 별점을 추출한다.
ratings = []
rating_containers = soup.find_all('div', class_='css-rz7kwu')

for container in rating_containers:
    stars = container.find_all('svg', class_='css-1mhwecd')
    
    rating = 0
    for star in stars:
        if star.find('path', fill='#FDBD00'): # 채워진 별인지 확인
            rating += 1
    ratings.append(rating)

# 리뷰 텍스트를 추출한다.
reviews_class = soup.find_all(class_= 'content-text css-c92dc4')
reviews = []

for review in reviews_class:
    # 리뷰 텍스트 정리 후 리스트에 추가
    cleaned_text = review.get_text(strip=True).replace('\r', '').replace('\n', '')
    reviews.append(cleaned_text)

# 드라이버를 종료한다.
driver.quit()

data = list(zip(ratings, reviews,dates)) # 별점, 리뷰 결합한 리스트 생성

# DataFrame으로 변환
df_reviews = pd.DataFrame(data, columns=['Rating', 'Review', 'Date'])

Jdata = []
for i in data:
    Jdata.append({'review': i[1], 'stars': i[0], 'date': i[2]})

# 최종 결과
df_reviews.to_excel('./res/crawling3/yeosu.xlsx', index=False)

with open('./res/crawling3/yeosu.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['review','stars','date']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in Jdata:
        writer.writerow(item)
with open('./res/crawling3/yeosu.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(Jdata, jsonfile, ensure_ascii=False, indent=4)