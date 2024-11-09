from flask import Blueprint, request, jsonify, render_template
import joblib
import numpy as np
import pandas as pd

# Blueprint 초기화
predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/', methods = ['GET'])
def main():
    return render_template('index.html')

@predict_bp.route('/predict', methods=['POST'])
def predict():
    print('예측 시작')
    # 사용자 입력 받기
    전형구분명 = request.form.get('radio')
    학과명 = request.form.get('department')
    입력_평균 = float(request.form.get('score'))

    print('전형구분:', 전형구분명)
    print('학과:', 학과명)
    print('점수:', 입력_평균)

    # 모델 불러오기, 경로 설정
    model_path = './general_model.pkl'
    try:
        model = joblib.load(model_path)
    except FileNotFoundError:
        result_message = "일반화된 모델 가중치 파일이 존재하지 않습니다. 먼저 모델을 학습하고 가중치를 저장하세요."
        return render_template('result.html', predicted_average=None, result_message=result_message)

    # 예측 수행
    next_year = 2024
    prediction_input = pd.DataFrame([[전형구분명, 학과명, next_year]], columns=['전형구분명_통합', '학과명', '연도'])
    
    try:
        predicted_average = model.predict(prediction_input)[0]
    except ValueError as e:
        print(f"예측 에러: {e}")
        result_message = "입력한 전형 구분명 또는 학과명이 모델이 학습하지 않은 값입니다. 다시 입력해 주세요."
        return render_template('result.html', predicted_average=None, result_message=result_message)

    # 합격 컷 설정 및 차이 계산
    합격_컷 = predicted_average
    차이 = 합격_컷 - 입력_평균  # 예상 합격 평균 - 입력 평균으로 계산

    # 합격 확률 계산 로직 (30% ~ 80%로 제한)
    if 입력_평균 <= 9.0:
        기본확률 = 65  # 기본 확률을 65%로 설정

        if 차이 > 0:
            # 입력 평균이 예상 합격 평균보다 낮음 -> 합격 확률이 높아짐
            # 기본 65%에서 시작하여, 차이에 따라 빠르게 증가 (최대 80%)
            확률 = min(80, 기본확률 + (차이 * 150))  # 차이에 따라 최대 80%까지 증가
            result_message = f"합격 확률이 높습니다! 예상 합격 평균은 {합격_컷:.2f}, 입력하신 평균은 {입력_평균:.2f}입니다. 합격 확률은 {확률:.2f}%입니다."
        else:
            # 입력 평균이 예상 합격 평균보다 높음 -> 합격 확률이 낮아짐
            # 기본 65%에서 시작하여, 차이에 따라 빠르게 감소 (최소 30%)
            확률 = max(30, 기본확률 + (차이 * 150))  # 차이에 따라 최소 30%까지 감소
            result_message = f"합격 확률이 낮습니다. 예상 합격 평균은 {합격_컷:.2f}, 입력하신 평균은 {입력_평균:.2f}입니다. 합격 확률은 {확률:.2f}%입니다."
    else:
        result_message = f"최저 등급 기준인 9.0을 초과했습니다. 합격 확률을 계산할 수 없습니다."

    print(f'예측 결과: {합격_컷}, 차이: {차이:.2f}, 확률: {확률:.2f}%')

    # 결과 페이지 렌더링
    return render_template('result.html', predicted_average=합격_컷, result_message=result_message)
