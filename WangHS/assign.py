import json
import time
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


# 셀레눔 드라이버와 스크롤 횟수를 받아서 스크롤을 내리는 함수 
def scroll_page(driver, scroll_count):  # 스크롤 횟수만큼 스크롤을 내림
    for _ in range(scroll_count):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)


# BeautifulSoup로 리뷰를 추출하는 함수
def extract_reviews(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select(".review-item-container")
    data = []

    for item in items:
        if item:
            review_point = 0
            review_point = len(item.find_all('path', attrs={'fill': '#FDBD00'}))
            review_text = item.select_one(".content-text.css-c92dc4").text
            review_date = item.select_one(".css-1irbwe1").text
            data.append({"review" : review_text, "stars" : review_point, "date" : review_date})
    return data


# 리뷰를 엑셀로 저장하는 함수
def save_reviews_as_excel(name, review_list): 
    df = pd.DataFrame(review_list, columns = ['point','review'])
    df_unique = df.drop_duplicates()
    df_unique.to_excel(f"review_list_{name}.xlsx")
    return

# 리뷰를 json으로 저장하는 함수
def save_reviews_as_json(name, review_list):
    with open(f"review_list_{name}.json", "w", encoding="utf-8") as file:
        json.dump(review_list, file, ensure_ascii=False, indent=4)

def crawl_yanolja_reviews(name, url):
    # 드라이버 
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)

    # 스크롤 횟수
    scroll_count = 10
    # 스크롤 내리기 함수 실행
    scroll_page(driver, scroll_count)

    # 리뷰 추출
    html = driver.page_source
    # 리뷰 추출 함수 실행
    review_list = extract_reviews(html)

    # 리뷰 저장 함수 실행 
    save_reviews_as_json(name, review_list)
    driver.quit()

if __name__ == '__main__':
    name="그랜드 하얏트 제주"
    url="https://www.yanolja.com/reviews/domestic/1000111556"
    crawl_yanolja_reviews(name=name, url=url)

    name="신라 호텔 제주"
    url="https://www.yanolja.com/reviews/domestic/3001296"
    crawl_yanolja_reviews(name=name, url=url)

    name="롯데 호텔 제주"
    url="https://www.yanolja.com/reviews/domestic/3001207"
    crawl_yanolja_reviews(name=name, url=url)
