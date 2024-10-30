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
  '마포': './Minseok/res/reviews.json', 
  '서대문': './Minseok/res/shillastay_Seodaemun.json',
  '역삼': './Minseok/res/shillastay_Yeoksam.json'
}

# Pickle file open example
# with open('./Minseok/res/prompt_1shot.pickle', 'rb') as f:
#     PROMPT = pickle.load(f)



def preprocess_reviews(path='./res/reviews.json'):
    # 모델 실습의 입력 데이터가 고도화된 전처리 함수와 동일합니다. 
    return 


def summarize(reviews):
    # 1. prompt를 불러와서 review를 합쳐줍니다. 
    # 2. OpenAI API를 불러와서 prompt를 넣어줍니다. 
    # 3. 결과를 반환합니다.
    return 


def fn(accom_name):
    # 1. MAPPING을 통하여 파일 경로를 받아옵니다. 
    # 2. preprocess_reviews를 통하여 리뷰를 받아옵니다.
    # 3. summarize를 통하여 리뷰를 요약합니다.
    # 4. 요약된 리뷰를 반환합니다.
    return 

def run_demo():
  demo = gr.Interface(
    fn = fn,
    inputs=[gr.Radio(['마포', '서대문', '역삼'], label='숙소')],
    outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
  )
  demo.launch(share=True)


if __name__ == '__main__':
    run_demo()