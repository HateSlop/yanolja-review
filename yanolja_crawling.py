import json
import time
import sys
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
    reviews = []

    # 리뷰 컨테이너 찾기 (class명은 실제 HTML 구조에 맞게 변경해야 할 수 있음)
    review_containers = soup.find_all('div', class_='review-item-container')

    for container in review_containers:
        # 별점 추출
        star_container = container.find('div', class_='css-rz7kwu')
        if star_container:
            stars = star_container.find_all('svg', class_='css-1mhwecd')
            star_rating = len(stars)
        else:
            star_rating = 0

        # 리뷰 내용 추출
        review_text_tag = container.find('p', class_='content-text')
        if review_text_tag:
            review_text = review_text_tag.get_text(strip=True)
        else:
            review_text = ''

        # 날짜 추출 (HTML에서 제공한 구조를 사용하여 추출)
        review_date_tag = container.find('p', class_='css-1irbwe1')
        if review_date_tag:
            review_date = review_date_tag.get_text(strip=True)
        else:
            review_date = 'Unknown'

        # 리뷰와 별점, 날짜를 딕셔너리 형태로 저장
        reviews.append({
            'review': review_text,
            'stars': star_rating,
            'date': review_date
        })

    return reviews

# 리뷰를 JSON 파일로 저장하는 함수
def save_reviews_as_json(name, review_list):
    filename = f"{name}_reviews.json"
    # JSON 파일로 저장
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(review_list, f, ensure_ascii=False, indent=4)
    print(f"Reviews saved to {filename}")

def crawl_yanolja_reviews(name, url):
    # 드라이버 
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)

    # 스크롤 횟수
    scroll_count = 5
    # 스크롤 내리기 함수 실행
    scroll_page(driver, scroll_count)

    # 리뷰 추출
    html = driver.page_source
    # 리뷰 추출 함수 실행
    review_list = extract_reviews(html)

    # 리뷰 저장 함수 실행 (JSON 형식으로)
    save_reviews_as_json(name, review_list)
    driver.quit()

if __name__ == '__main__':
    name = "신라스테이 여수"
    url = "https://www.yanolja.com/reviews/domestic/10046614"
    crawl_yanolja_reviews(name=name, url=url)
