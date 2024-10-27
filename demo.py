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
client = OpenAI(api_key = OPENAI_API_KEY)

MAPPING_EXAMPLE = {
  '조선': './res/TheWestinJosunSeoul_reviews.json', 
  '시그': './res/SignielSeoul.json',
}

# Pickle file open example
# with open('./Minseok/res/prompt_1shot.pickle', 'rb') as f:
#     PROMPT = pickle.load(f)


prompt_1shot = """
당신은 숙소 리뷰 요약 전문가입니다. 다음 숙소 리뷰를 요약해 주세요. 
요약 결과는 다음 조건을 충족해야 합니다:
1. 모든 문장은 존댓말로 작성되어야 합니다.
2. 숙소에 대해 소개하는 톤으로 작성하세요.

예시 요약:
- "전반적으로 좋은 숙소였으며, 서비스가 훌륭하다는 평가가 많았습니다."

다음은 숙소에 대한 리뷰들입니다:
{reviews}
"""

prompt_2shot = """
당신은 숙소 리뷰 요약 전문가입니다. 다음 숙소 리뷰를 요약해 주세요. 
요약 결과는 다음 조건을 충족해야 합니다:
1. 모든 문장은 존댓말로 작성되어야 합니다.
2. 숙소에 대해 소개하는 톤으로 작성하세요.

예시 요약 1:
- "객실이 청결하고 넓어서 편안했다는 평이 많습니다."

예시 요약 2:
- "위치가 좋아 관광객에게 추천된다는 의견이 많습니다."

다음은 숙소에 대한 리뷰들입니다:
{reviews}
"""

def preprocess_reviews(path='./res/reviews.json'):
    # 모델 실습의 입력 데이터가 고도화된 전처리 함수와 동일합니다. 
    with open(path, 'r',encoding='UTF-8') as f:
      review_list = json.load(f)
      reviews_good, reviews_bad = [], []

      current_date = datetime.datetime.now()
      date_boundary = current_date - datetime.timedelta(days=6*30)

      for review in review_list:
          review_date_str = review['date']
          try:
              review_date = parser.parse(review_date_str) 
          except(ValueError, TypeError):
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


def summarize(reviews, prompt, temperature=0.0, model='gpt-3.5-turbo-0125'):
    # 1. prompt를 불러와서 review를 합쳐줍니다. 
    # 2. OpenAI API를 불러와서 prompt를 넣어줍니다. 
    # 3. 결과를 반환합니다.
    prompt = prompt + '\n\n' + reviews 
  
    completion = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature
    )

    return completion.choices[0].message.content



def fn(accom_name, shot_type='1-shot'):
    # 1. MAPPING을 통하여 파일 경로를 받아옵니다. 
    # 2. preprocess_reviews를 통하여 리뷰를 받아옵니다.
    # 3. summarize를 통하여 리뷰를 요약합니다.
    # 4. 요약된 리뷰를 반환합니다.
    file_path = MAPPING_EXAMPLE.get(accom_name)

    reviews_good, reviews_bad = preprocess_reviews(file_path)


    if shot_type == '1-shot':
        prompt = prompt_1shot
    else:
        prompt = prompt_2shot


    summary_good = summarize(reviews_good, prompt)
    summary_bad = summarize(reviews_bad, prompt)
    
    return summary_good, summary_bad


def run_demo():
  demo = gr.Interface(
      
    fn = fn,
    inputs=[gr.Radio(['조선', '시그'], label='숙소'),
            gr.Radio(['1-shot','2-shot'], label='프롬프트 선택')],
    outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
  )
  demo.launch(share=True)


if __name__ == '__main__':
    run_demo()
    