import numpy as np
import pandas as pd
import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification
from sklearn.model_selection import train_test_split

tf.config.list_physical_devices('GPU')

'''
깃허브에 있는 맛집 리뷰 데이터셋을 이용하지 못하기 때문에 크롤링한 데이터 내로 학습시킨다고 가정.
예를 들면 25년도부터 현재까지의 리뷰 데이터가 감성 분석 시킬 데이터라고 하면, 24년도부터 25년도까지의 리뷰 데이터로 학습을 하는 식.
실제 모델이 감성 분석을 수행해야 하는 전체 크롤링 데이터는 [데이터셋 B]로 가정.
모델이 감성 분석을 수행하기 위해서는 학습용 데이터셋이 필요하기 때문에, [데이터셋 A]로 가정한 학습용 데이터를 임의로 만들어서 모델을 학습시키는 형태로 진행.
'''

'''
코드 실행하기 위한 환경 설정
bert 수업에 진행했던 환경이 파이썬 3.9 환경이기에 일단 파이썬 3.9 환경으로 진행하였습니다.
uv venv --python 3.9
uv pip install tensorflow==2.10.0 pandas numpy scikit-learn
uv pip install "numpy<2" --force-reinstall
uv pip install torch --extra-index-url https://download.pytorch.org/whl/cu116 --index-strategy unsafe-best-match
uv pip install transformers==4.24.0
'''

# 데이터셋 로드, 실제로는 db에서 불러와야함
# [데이터셋 A] 학습용 데이터 (임의로 개수를 불렸음)
labeled_data = pd.DataFrame([
    {"content": "여기 전북대 앞 최애 맛집인데 오늘따라 국물이 깊고 너무 맛있네요", "label": 1}, 
    {"content": "객사 갈 때마다 무조건 들르는 곳! 분위기 아주 좋습니다", "label": 1}, 
    {"content": "신시가지에 주차장 넓은 식당 찾다가 왔는데 대만족이에요", "label": 1}, 
    {"content": "고기가 너무 질기고 서빙하시는 분 태도가 별로였습니다", "label": 0},
    {"content": "음식에서 머리카락 나오고 사장님 대응도 적반하장이네요 절대 안감", "label": 0},
    {"content": "웨이팅 긴 거에 비해서 맛은 그냥 평범해요 돈 아까움", "label": 0}
] * 100) 

# [데이터셋 B] 실제 모델이 감성 분석을 수행해야 하는 전체 크롤링 데이터
crawled_data = pd.DataFrame([
    {"review_id": 1, "store_id": 101, "content": "매장이 넓고 쾌적해서 회식하기 좋습니다 짜글이 맛있어요"},
    {"review_id": 2, "store_id": 102, "content": "위생 상태가 좀 눈에 밟히네요 맛은 있는데 아쉽습니다"},
    {"review_id": 3, "store_id": 103, "content": "인테리어가 이쁘고 사진 찍기 좋은 곳 인스타 감성 맛집"},
    {"review_id": 4, "store_id": 104, "content": "다시는 안 올래요 고기도 덜 익혀 나오고 서빙도 느림"},
])

# 모델 설정
model_name = "beomi/kcbert-base"
MAX_LEN = 64
BATCH_SIZE = 32
LEARNING_RATE = 2e-5
EPOCHS = 3  

# gpu 설정
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            # 필요한 만큼만 메모리를 사용하도록 설정
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"[설정] GPU {len(gpus)}개를 사용합니다.")
    except RuntimeError as e:
        print(f"[경고] GPU 설정 중 오류 발생: {e}")
else:
    print("[설정] GPU를 찾을 수 없습니다. CPU를 사용합니다 (속도가 느릴 수 있습니다).")

# 토크나이저
tokenizer = BertTokenizer.from_pretrained(model_name, trust_remote_code=True)

# 훈련/검증 데이터셋 분리 (8:2)
train_texts, test_texts, train_labels, test_labels = train_test_split(
    labeled_data['content'].values, 
    labeled_data['label'].values, 
    test_size=0.2, 
    random_state=42
)

def bert_tokenize(texts, tokenizer, max_len):
    """
    텍스트 리스트를 BERT 모델 입력 형식으로 변환하는 함수입니다.
    """
    # tokenizer가 리스트를 한 번에 처리해줍니다.
    encodings = tokenizer(
        texts.tolist(),           # 텍스트 리스트
        truncation=True,          # max_len보다 길면 자름
        padding='max_length',     # max_len보다 짧으면 0으로 채움
        max_length=max_len,       # 최대 길이 설정
        return_token_type_ids=True,  # KcBERT 구동을 위해 True로 변경
        return_tensors='tf'       # TensorFlow 텐서 형식으로 반환
    )
    return encodings

print("[토크나이징] 학습 및 검증 데이터를 변환 중입니다...")
train_encodings = bert_tokenize(train_texts, tokenizer, MAX_LEN)
test_encodings = bert_tokenize(test_texts, tokenizer, MAX_LEN)

# TensorFlow Dataset 생성
train_dataset = tf.data.Dataset.from_tensor_slices((
    {
        "input_ids": train_encodings["input_ids"],
        "token_type_ids": train_encodings["token_type_ids"],
        "attention_mask": train_encodings["attention_mask"]
    },
    train_labels
)).shuffle(100).batch(BATCH_SIZE)

test_dataset = tf.data.Dataset.from_tensor_slices((
    {
        "input_ids": test_encodings["input_ids"],
        "token_type_ids": test_encodings["token_type_ids"],
        "attention_mask": test_encodings["attention_mask"]
    },
    test_labels
)).batch(BATCH_SIZE)

# 모델 로드 (PyTorch에서 TensorFlow로 변환)
model = TFBertForSequenceClassification.from_pretrained(model_name, from_pt=True, num_labels=2)

# 컴파일 (최적화 도구 및 손실 함수 설정)
optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
model.compile(optimizer=optimizer, 
              loss=loss, 
              metrics=['accuracy'])

# 모델 학습
print("\n--- [학습 시작]맛집 데이터 기반 학습을 시작합니다 ---")
model.fit(train_dataset, epochs=EPOCHS, validation_data=test_dataset)
print("--- 모델 학습 완료 ---\n")

# 실제 크롤링 데이터에 대해 감성 분석 수행
def predict_sentiment(text):
    # 토크나이징
    encodings = tokenizer(
        [text],
        truncation=True,
        padding='max_length',
        max_length=MAX_LEN,
        return_token_type_ids=True,
        return_tensors='tf'
    )
    # 예측
    prediction = model.predict({
        "input_ids": encodings["input_ids"],
        "token_type_ids": encodings["token_type_ids"],
        "attention_mask": encodings["attention_mask"]
    }, verbose=0)

    # prediction.logits에서 값 추출 후 Softmax 연산을 통해 0~1 사이 확률로 변환
    logits = prediction.logits
    probabilities = tf.nn.softmax(logits, axis=-1).numpy()[0]

    # 임시 디버깅을 위해 확률 분포 출력 (값의 치우침을 모니터링하기 위함), 모델이 잘 학습되었다면 삭제 가능
    print(f"[디버깅] 부정이해 확률: {probabilities[0]:.4f} | 긍정이해 확률: {probabilities[1]:.4f}")

    # 인덱스 1번인 '긍정 확률' 값만 추출하여 반환
    positive_score = probabilities[1]
    return positive_score

# 크롤링 데이터에 감성 분석 적용
print("[감성 분석] 크롤링 데이터에 감성 분석을 적용 중입니다...")
analysis_results = []
for row in crawled_data.itertuples():
    # 긍정 확률 점수 획득 (0.0 ~ 1.0)
    pos_rate = predict_sentiment(row.content)
    
    # 0.5 기준 Review 테이블용 플래그 분기
    sentiment_flag = "P" if pos_rate >= 0.5 else "N"
    
    analysis_results.append({
        "review_id": row.review_id,
        "store_id": row.store_id,
        "content": row.content,
        "sentiment": sentiment_flag        
    })

# 결과 출력
final_df = pd.DataFrame(analysis_results)
print("\n=== [최종 감성 분석 결과] ===")
print(final_df[['store_id', 'content', 'sentiment']])

# 실제로는 final_df의 'sentiment' 컬럼을 Review 테이블의 'sentiment' 컬럼에 업데이트하는 작업이 필요합니다. 예시에서는 출력으로 대체하였습니다.