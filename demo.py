import datetime
import json
import os
import pickle
from dateutil import parser

import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

MAPPING_EXAMPLE = {
  '마포': './res/reviews.json', 
  '서대문': './res/shillastay_Seodaemun.json',
  '역삼': './res/shillastay_Yeoksam.json',
}

def preprocess_reviews(path='./res/paju_mate.json'):
    # JSON 파일에서 리뷰 데이터 로드
    with open(path, 'r', encoding='utf-8') as f:
        review_list = json.load(f)
        reviews_good, reviews_bad = [], []

        # 6개월 전 날짜 기준으로 리뷰 필터링
        current_date = datetime.datetime.now()
        date_boundary = current_date - datetime.timedelta(days=6 * 30)

        for review in review_list:
            review_date_str = review['date']
            try:
                review_date = parser.parse(review_date_str)
            except (ValueError, TypeError):
                review_date = current_date  # 날짜 파싱 실패 시 현재 날짜로 설정

            # 6개월 이전 리뷰는 제외
            if review_date < date_boundary:
                continue

            # 리뷰 별점에 따라 분류
            if review['stars'] == 5:
                reviews_good.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')
            else:
                reviews_bad.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')

        review_good_text = '\n'.join(reviews_good)
        review_bad_text = '\n'.join(reviews_bad)

    return review_good_text, review_bad_text

def summarize(reviews, prompt, temperature=0.0, model='gpt-3.5-turbo-0125'):
    # 프롬프트와 리뷰 결합
    prompt_with_reviews = prompt + '\n\n' + reviews

    # OpenAI API 호출하여 요약 생성
    completion = client.Completion.create(
        model=model,
        prompt=prompt_with_reviews,
        temperature=temperature,
        max_tokens=150
    )

    return completion.choices[0].text.strip()

def fn(accom_name):
    # 숙소 이름을 통해 파일 경로 받아오기
    file_path = MAPPING_EXAMPLE.get(accom_name)
    
    if not file_path:
        return "해당 숙소에 대한 데이터를 찾을 수 없습니다.", ""

    # 리뷰 데이터를 전처리하여 요약할 수 있도록 준비
    reviews_good, reviews_bad = preprocess_reviews(file_path)

    # 요약에 사용할 프롬프트
    prompt = """당신은 요약 전문가입니다. 아래에 주어진 리뷰들을 5문장 내로 요약해 주세요.
    리뷰들:
    {reviews}
    요약:"""

    # 높은 평점 리뷰 요약
    summary_good = summarize(reviews_good, prompt)
    
    # 낮은 평점 리뷰 요약
    summary_bad = summarize(reviews_bad, prompt)
    
    return summary_good, summary_bad

def run_demo():
    # Gradio 인터페이스 설정
    demo = gr.Interface(
        fn=fn,
        inputs=[gr.Radio(['마포', '서대문', '역삼'], label='숙소')],
        outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
    )
    demo.launch(share=True)

if __name__ == '__main__':
    run_demo()
