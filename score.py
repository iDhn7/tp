import pandas as pd
from datetime import datetime, timedelta


# 모델을 통해 학습이 끝난 데이터를 불러오는 코드(실제 db에서 불러와야함)


def calculate_store_scores(store_id, reviews_df, facility_count):
    """
    특정 매장의 맛, 최근성, 편의성을 가중치(60:25:15)로 연산하여 5점 만점 총점을 구하고,
    계절 적합성 점수는 별도로 산출하는 함수입니다.
    """
    total_review_count = len(reviews_df)
    
    # 리뷰가 아예 없는 신생 매장의 경우 기본값 처리
    if total_review_count == 0:
        return {
            "store_id": store_id,
            "taste_score": 0,
            "recency_score": 0,
            "convenience_score": 0,
            "total_star": 0.0,
            "spring_score": 0, "summer_score": 0, "autumn_score": 0, "winter_score": 0
        }

    # 맛 점수 (100점 만점) -> 가중치 60%
    taste_keywords = ['맛', '국물', '고기', '음식', '양념', '소스','디저트']
    taste_reviews = reviews_df[reviews_df['content'].str.contains('|'.join(taste_keywords), na=False)]
    
    if len(taste_reviews) > 0:
        # 맛 관련 리뷰 중 긍정('P') 비율
        taste_pos_reviews = taste_reviews[taste_reviews['sentiment'] == 'P']
        taste_score = (len(taste_pos_reviews) / len(taste_reviews)) * 100
    else:
        taste_score = 50.0  # 관련 키워드가 없으면 평균값 부여

    # 최근성 점수 (100점 만점) -> 가중치 25%
    three_months_ago = datetime.now() - timedelta(days=90)
    recent_reviews = reviews_df[reviews_df['created_at'] >= three_months_ago]
    recency_score = (len(recent_reviews) / total_review_count) * 100

    # 편의성 점수 (100점 만점) -> 가중치 15%
    # 항목이 5개 이상이면 만점(100), 그 이하는 개당 20점 차등 감소
    if facility_count >= 5:
        convenience_score = 100
    else:
        convenience_score = facility_count * 20


    # 최종 총점 환산 (5점 만점)

    weighted_total = (taste_score * 0.60) + (recency_score * 0.25) + (convenience_score * 0.15)
    total_star_score = round((weighted_total / 100) * 5, 2)


    # 4계절 적합성 점수 각각 산출 (100점 만점)
    # 기재된 리뷰의 작성 월(Month)을 기준으로 분류 (3~5월: 봄, 6~8월: 여름, 9~11월: 가을, 12~2월: 겨울)
    reviews_df['month'] = reviews_df['created_at'].dt.month
    
    spring_count = len(reviews_df[reviews_df['month'].isin([3, 4, 5])])
    summer_count = len(reviews_df[reviews_df['month'].isin([6, 7, 8])])
    autumn_count = len(reviews_df[reviews_df['month'].isin([9, 10, 11])])
    winter_count = len(reviews_df[reviews_df['month'].isin([12, 1, 2])])

    # 각각의 계절 점수 계산
    spring_score = round((spring_count / total_review_count) * 100, 1)
    summer_score = round((summer_count / total_review_count) * 100, 1)
    autumn_score = round((autumn_count / total_review_count) * 100, 1)
    winter_score = round((winter_count / total_review_count) * 100, 1)

    return {
        "store_id": store_id,
        "taste_score": round(taste_score, 1),
        "recency_score": round(recency_score, 1),
        "convenience_score": convenience_score,
        "total_star": total_star_score,         # 5점 만점 총점
        "season_scores": {
            "spring": spring_score,
            "summer": summer_score,
            "autumn": autumn_score,
            "winter": winter_score
        }
    }