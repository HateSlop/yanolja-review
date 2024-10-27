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
client = OpenAI(api_key=OPENAI_API_KEY)
MAPPING_EXAMPLE = {
  '그랜드하얏트': 'review_list_그랜드 하얏트 제주.json', 
  '롯데': 'review_list_롯데 호텔 제주.json',
  '신라': 'review_list_신라 호텔 제주.json',
}

# Pickle file open example
# with open('./Minseok/res/prompt_1shot.pickle', 'rb') as f:
#     PROMPT = pickle.load(f)


# 모델 실습의 입력 데이터가 고도화된 전처리 함수와 동일합니다.
def preprocess_reviews(path='./res/reviews.json'):
    with open(path, 'r', encoding='UTF8') as f:
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

        if len(review['review']) < 30:
            continue

        if review['stars'] == 5:
            reviews_good.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + review['review'] + '[REVIEW_END]')

    review_good_text = '\n'.join(reviews_good)
    review_bad_text = '\n'.join(reviews_bad)

    return review_good_text, review_bad_text



# 1. prompt를 불러와서 review를 합쳐줍니다. 
# 2. OpenAI API를 불러와서 prompt를 넣어줍니다. 
# 3. 결과를 반환합니다.
def summarize(reviews, prompt, temperature=0.0, model='gpt-3.5-turbo-0125'):
    prompt = prompt + '\n\n' + reviews

    completion = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature
    )

    return completion.choices[0].message.content




# 1. MAPPING을 통하여 파일 경로를 받아옵니다. 
# 2. preprocess_reviews를 통하여 리뷰를 받아옵니다.
# 3. summarize를 통하여 리뷰를 요약합니다.
# 4. 요약된 리뷰를 반환합니다.
def fn(accom_name):
    # 1. MAPPING을 통해 파일 경로를 받아옵니다.
    file_path = MAPPING_EXAMPLE.get(accom_name)
    if not file_path:
        return "해당 숙소의 리뷰 파일이 존재하지 않습니다.", "해당 숙소의 리뷰 파일이 존재하지 않습니다."

    # 2. preprocess_reviews를 통해 리뷰를 받아옵니다.
    review_good_text, review_bad_text = preprocess_reviews(path=file_path)

    # 3. Pickle 파일에서 Prompt를 로드합니다.
    with open('prompt_1shot.pickle', 'rb') as f:
        prompt = pickle.load(f)

    # 4. summarize를 통해 리뷰를 요약합니다.
    summary_good = summarize(reviews=review_good_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo-0125')
    summary_bad = summarize(reviews=review_bad_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo-0125')

    # 5. 요약된 리뷰를 반환합니다.
    return summary_good, summary_bad


def run_demo():
  demo = gr.Interface(
    fn = fn,
    inputs=[gr.Radio(['그랜드하얏트', '롯데', '신라'], label='제주 호텔 숙소')],
    outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
  )
  demo.launch(share=True)


if __name__ == '__main__':
    run_demo()