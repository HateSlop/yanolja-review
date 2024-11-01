import datetime
import json
import os
import pickle
from dateutil import parser

import gradio as gr
import openai
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

openai.api_key = OPENAI_API_KEY

# 숙소 이름과 리뷰 파일 매핑
MAPPING_EXAMPLE = {
    '레지던스': 'mw/레지던스_reviews.json', 
    '엘본스': 'mw/엘본스_reviews.json',
    '위더스': 'mw/위더스_reviews.json',
}

def preprocess_reviews(path='./res/reviews.json'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            review_list = json.load(f)
        logging.info(f"리뷰 파일을 성공적으로 로드했습니다: {path}")
    except FileNotFoundError:
        logging.error(f"리뷰 파일을 찾을 수 없습니다: {path}")
        return
    except json.JSONDecodeError:
        logging.error(f"JSON 파싱 오류: {path}")
        return 
    
    reviews_good, reviews_bad = [], []

    current_date = datetime.datetime.now()
    date_boundary = current_date - datetime.timedelta(days=6*30)

    for review in review_list:
        review_date_str = review.get('date', '')
        try:
            review_date = parser.parse(review_date_str)
        except (ValueError, TypeError):
            review_date = current_date
        
        if review_date < date_boundary:
            continue

        review_text = review.get('review', '')
        if len(review_text) < 30:
            continue

        if review.get('stars') == '5점':
            reviews_good.append('[REVIEW_START]' + review_text + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + review_text + '[REVIEW_END]')

    review_good_text = '\n'.join(reviews_good)
    review_bad_text = '\n'.join(reviews_bad)

    logging.info(f"긍정적 리뷰 수: {len(reviews_good)}, 부정적 리뷰 수: {len(reviews_bad)}")
    return review_good_text, review_bad_text

def summarize(reviews, prompt, temperature=0.0, model='gpt-3.5-turbo'):
    combined_prompt = f"{prompt}\n\n{reviews}"
    logging.info("프롬프트 생성 완료.")

    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': combined_prompt}],
            temperature=temperature
        )
        summary = completion.choices[0].message.content.strip()
        logging.info("요약 생성 성공")
        return summary
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API 호출 중 오류 발생: {e}")
        return "요약 생성에 실패."
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {e}")
        return "요약 생성에 실패."

def fn(accom_name):
    logging.info(f"숙소 선택됨: {accom_name}")
    file_path = MAPPING_EXAMPLE.get(accom_name)
    if not file_path:
        logging.warning(f"매핑되지 않은 숙소 이름: {accom_name}")
        return "해당 숙소의 리뷰 파일이 존재하지 않습니다."

    review_good_text, review_bad_text = preprocess_reviews(path=file_path)
    if not review_good_text and not review_bad_text:
        logging.warning("전처리된 리뷰가 없습니다.")
        return "리뷰가 충분하지 않습니다."

    try:
        with open('mw/prompt_1shot.pickle', 'rb') as f:
            prompt = pickle.load(f)
        logging.info("프롬프트 파일 로드 성공")
    except FileNotFoundError:
        logging.error("프롬프트 파일을 찾을 수 없습니다: prompt_1shot.pickle")
        return "프롬프트 파일을 찾을 수 없습니다.", "프롬프트 파일을 찾을 수 없습니다."
    except Exception as e:
        logging.error(f"프롬프트 로드 중 오류 발생: {e}")
        return f"프롬프트 로드 중 오류 발생: {e}", f"프롬프트 로드 중 오류 발생: {e}"

    summary_good = summarize(reviews=review_good_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo')
    summary_bad = summarize(reviews=review_bad_text, prompt=prompt, temperature=0.0, model='gpt-3.5-turbo')

    return summary_good, summary_bad

def run_demo():
    demo = gr.Interface(
        fn=fn,
        inputs=[gr.Radio(['레지던스', '엘본스', '위더스'], label='호텔')],
        outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')],
        title="호텔 리뷰 제공",
        description="선택한 호텔의 긍정적 및 부정적인 리뷰를 요약하여 제공합니다.",
        theme="default"
    )
    demo.launch(share=True)

if __name__ == '__main__':
    run_demo()
