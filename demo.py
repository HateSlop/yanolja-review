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
  'L7해운대': 'review_L7해운대.json', 
  '신라스테이 해운대': 'review_신라스테이 해운대.json',
  '해운대 베이몬드 호텔': 'review_해운대 베이몬드 호텔.json',
}



def preprocess_reviews(path='./res/reviews.json'):
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
        if review['stars'] == 5:
            reviews_good.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')
    
    review_good_text = '\n'.join(reviews_good)
    review_bad_text = '\n'.join(reviews_bad) 

    return review_good_text, review_bad_text


def summarize(reviews, prompt, temperature=0.0, model = 'gpt-3.5-turbo-0125'):
    # 1. prompt를 불러와서 review를 합쳐줍니다.
    prompt = prompt + '\n\n' + reviews
    # 2. OpenAI API를 불러와서 prompt를 넣어줍니다. 
    client = OpenAI(api_key=os.getenv('OPNEAI_API_KEY'))
    completion = client.chat.completions.create(
        model = model,
        messages = [{'role': 'user', 'content': prompt}],
        temperature=temperature
    )
    # 3. 결과를 반환합니다.
    return completion.choices[0].message.content

def fn(accom_name):
    # 1. MAPPING을 통하여 파일 경로를 받아옵니다. 
    file_path = MAPPING_EXAMPLE.get(accom_name)
    if not file_path:
        return "No review of such hotel." 
    # 2. preprocess_reviews를 통하여 리뷰를 받아옵니다.
    review_good_text, review_bad_text = preprocess_reviews(path = file_path)
    with open('res\prompt_1shot.pickle', 'rb') as f:
        prompt = pickle.load(f)
    # 3. summarize를 통하여 리뷰를 요약합니다.
    summary_good = summarize(reviews=review_good_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo-0125')
    summary_bad = summarize(reviews=review_bad_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo-0125')
    # 4. 요약된 리뷰를 반환합니다.
    return summary_good, summary_bad

def run_demo():
  demo = gr.Interface(
    fn = fn,
    inputs=[gr.Radio(['L7해운대', '신라스테이 해운대', '해운대 베이몬드 호텔'], label='해운대 4성급 호텔')],
    outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
  )
  demo.launch(share=True)


if __name__ == '__main__':
    run_demo()