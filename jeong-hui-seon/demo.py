import datetime
import json
import os
import pickle
from dateutil import parser

import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MAPPING_EXAMPLE = {
  '제주': './res/crawling1/jeju_marevo.json',
  '순천':'./res/crawling2/suncheon.json',
  '여수': './res/crawling3/yeosu.json'
}

# Pickle file open example
with open('./res/prompt_1shot.pickle', 'rb') as f:
    PROMPT = pickle.load(f)


def preprocess_reviews(path):
    # 모델 실습의 입력 데이터가 고도화된 전처리 함수와 동일합니다. 
    with open(path, 'r', encoding='utf-8') as f:
        review_list = json.load(f)

    reviews_good, reviews_bad = [], []

    current_date = datetime.datetime.now()
    date_boundary = current_date - datetime.timedelta(days=6*30)

    for review in review_list:
        review_date_str = review['date']
        try:
            review_date = parser.parse(review_date_str)
        except (ValueError, TypeError):
            review_date = current_date

        if review_date < date_boundary:
            continue

        if review['stars']==5:
            reviews_good.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')

    reviews_good_text = '\n'.join(reviews_good)
    reviews_bad_text = '\n'.join(reviews_bad)

    return reviews_good_text, reviews_bad_text


def summarize(review, prompt, temperature=0.0, model='gpt-3.5-turbo-0125'):
    # 1. prompt를 불러와서 review를 합쳐줍니다. 
    # 2. OpenAI API를 불러와서 prompt를 넣어줍니다. 
    # 3. 결과를 반환합니다.
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = prompt + '\n\n' + review
    
    completion = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content':prompt}],
        temperature=temperature
    )
    return completion


def fn(accom_name):
    # 1. MAPPING을 통하여 파일 경로를 받아옵니다. 
    # 2. preprocess_reviews를 통하여 리뷰를 받아옵니다.
    # 3. summarize를 통하여 리뷰를 요약합니다.
    # 4. 요약된 리뷰를 반환합니다.
    FilePath = MAPPING_EXAMPLE[accom_name]
    ReviewGood, ReviewBad = preprocess_reviews(FilePath)
    summary_good = summarize(ReviewGood, PROMPT, temperature=0.0, model='gpt-3.5-turbo-0125').choices[0].message.content
    summary_bad = summarize(ReviewBad, PROMPT, temperature=0.0, model='gpt-3.5-turbo-0125').choices[0].message.content

    return summary_good,summary_bad

def run_demo():
  demo = gr.Interface(
    fn = fn,
    inputs=[gr.Radio(['제주', '순천', '여수'], label='숙소')],
    outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
  )
  demo.launch(share=True)


if __name__ == '__main__':
    run_demo()