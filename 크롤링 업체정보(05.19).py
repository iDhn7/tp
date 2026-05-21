from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import sys
from DBManager import DBManager
import service.Crawling as crwal

# db에 저장된 업체 코드 리스트 불러오는 코드 작성
codes = 
# ,"1598840565","1963358828"] # 예시로 한 것, 실제로는 db에서 불러와야 함

options = webdriver.ChromeOptions()


 # options.add_argument('headless') # 브라우저 창을 띄우지 않고 실행하려면 주석해제


driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
# https://pcmap.place.naver.com/restaurant/17040255/information
# https://pcmap.place.naver.com/restaurant/1598840565/information
# https://pcmap.place.naver.com/restaurant/1963358828/information
for store_code in codes:
    # 리뷰 수집하는 코드 작성 
    # 방문자 리뷰 주소: driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/review/visitor?reviewSort=recent")
    # 블로그 리뷰 주소: driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/review/ugc?reviewSort=recent&type=list")
    # 리뷰를 25년도 1월부터 현재까지 수집하는 방식으로 작성(리뷰 작성일이 25년도 1월보다 이전이면 수집 종료하는 식으로)
    # 방문자 리뷰 먼저 수집하고, 그 다음에 블로그 리뷰 수집하는 방식으로 작성
    # 리뷰는 10개 단위로 나오고 그 뒤에 리뷰는 더보기 버튼을 클릭해야함 


# url = "원하는_웹페이지_주소"
# response = requests.get(url)

# # 1. requests로 가져온 HTML 텍스트를 BeautifulSoup으로 파싱(분석)할 준비를 합니다.
# soup = BeautifulSoup(response.text, 'html.parser')

# # 2. 'GHAhO' 클래스를 가진 첫 번째 span 태그 찾기
# # ⚠️ 주의: 파이썬에서 class는 예약어이기 때문에, BeautifulSoup에서는 class_ 뒤에 언더바(_)를 붙여야 합니다.
# target = soup.find('span', class_='GHAhO')

# # 3. 결과 출력하기
# if target:
#     print(target.text.strip())  # .text로 글자만 가져오고, .strip()으로 앞뒤 공백 제거
# else:
#     print("해당 태그를 찾지 못했습니다.")






    # 업체 정보(업체소개, 편의시설) 수집하는 코드 작성
    # 이름,업체소개,편의시설,주차
    driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/information")
    time.sleep(2)
    
    
    # url = (f"https://pcmap.place.naver.com/restaurant/{store_code}/information")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)

    # 'GHAhO' 클래스를 가진 첫 번째 span 태그 찾기
    store_name = soup.find('span', class_='GHAhO')

    if store_name:
        print(store_name.text.strip())  # .text로 글자만 가져오고, .strip()으로 앞뒤 공백 제거
    else:
        print("해당 태그를 찾지 못했습니다.")
    
    store_intro=soup.select_one('div.pvuWY')

    if store_intro:
    # recursive=False를 주면 내부 자식 태그 안의 글자는 제외하고 
    # 해당 div의 바로 직계 텍스트만 가져옵니다.
        store_intro_text = store_intro.find(string=True, recursive=False)
        
        if store_intro_text:
            print(store_intro_text.strip()) 
        else:
            store_intro_text = "소개글 없음"
            print(store_intro_text)
    else:
        store_intro_text = "소개글 없음"
        print(store_intro_text)
    

    # 1. 'jIxAu' 클래스를 가진 li 태그 안의 's8NBf' 클래스를 가진 div 태그를 모두 찾습니다.
    # CSS 선택자로 'li.jIxAu div.s8NBf'라고 쓰면 정확하게 매칭됩니다.
    store_amenities_tags = soup.select('li.jIxAu div.s8NBf')

    # 2. 찾은 태그들에서 텍스트만 뽑아서 공백을 제거하고 리스트로 만듭니다.
    # (빈 텍스트가 있다면 걸러내는 조건도 추가)
    store_amenities = [tag.text.strip() for tag in store_amenities_tags if tag.text.strip()]

    # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_amenities:
        # 리스트 안의 요소들을 쉼표(,)로 연결해서 하나의 문자열로 만듭니다.
        store_amenities_str = ", ".join(store_amenities)
        print(f"편의시설: {store_amenities_str}")
    else:
        store_amenities_str = "편의시설 정보 없음"
        print(store_amenities_str)

    # 주차 관련
    # store_parking = soup.select 는 다중선택, soup.select_one 은 하나만선택
    store_parking = soup.select_one('div.C9Arw div.pu5zX')
    if store_parking:
        print(store_parking.text.strip())  # .text로 글자만 가져오고, .strip()으로 앞뒤 공백 제거
    else:
        print("주차 정보 없음")
    
    data_info = {print(f" {store_name.text.strip()},{store_intro_text.strip()},{store_amenities_str},{store_parking}")}
    
    time.sleep(2)
        
#         # span "GHAhO" #업체이름
#         # div class "pvuWY" "바로나오는 div 내용 " #업체소개
#         # li class "jIxAu", div class "s8NBf" #편의시설 text
#         # div class "C9Arw","pu5zX" #주차
     

#     print(f"업체이름 : {data_info['span GHAhO']}"
#            "업체소개 : {data_info['div class "AX_W3 (변수)"']}"
#            "편의시설 :{data_info['li class "jIxAu", dic class "s8NBf"']}"
#            "주차 : {data_info['div class "C9Arw","pu5zX"']}")


#     # 홈 화면에서 정보 따오기
#     # 업체이름, 방문자 리뷰 수 ,블로그 리뷰수, 주소 , 영업시간 , 전화번호,  
    driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/home")
    time.sleep(2)

    # 1.store_name 그대로 쓰기(업체명)
    
     
    #2. 방문자 리뷰 수, 블로그 리뷰수
    store_reviews = soup.select('span.PXMot')
    # 찾은 태그들에서 텍스트만 뽑아서 공백을 제거하고 리스트로 만듭니다.
    # (빈 텍스트가 있다면 걸러내는 조건도 추가)
    store_reviews = [tag.text.strip() for tag in store_reviews if tag.text.strip()]

    # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_reviews:
        # 리스트 안의 요소들을 쉼표(,)로 연결해서 하나의 문자열로 만듭니다.
        store_reviews_str = ", ".join(store_reviews)
        print(f"리뷰수정보: {store_reviews_str}")
    else:
        store_reviews_str = "리뷰수정보없음"
        print(store_reviews_str)
    time.sleep(3)
    # 전화번호 더 상위단 클래스 필요?
    # store_phone = soup.select('span.xlx7Q')
    store_phone = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.xlx7Q")))
    
    # (빈 텍스트가 있다면 걸러내는 조건도 추가)
    # store_phone = [tag.text.strip() for tag in store_phone if tag.text.strip()]
    store_phone = store_phone.text.strip()
                                          
    # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_phone:
        print(f"전화번호: {store_phone}")
    else:
        store_phone = "전화번호없음"
        print(store_phone)
    time.sleep(3)
    # 주소 더 상위단 클래스 필요?
    # store_address = soup.select('span.pz7wy')
    # 클래스로 자르려고 했는데 안됌 이유는 확인중
    store_address = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.pz7wy")))
    # 찾은 태그들에서 텍스트만 뽑아서 공백을 제거하고 리스트로 만듭니다.
    # (빈 텍스트가 있다면 걸러내는 조건도 추가)
    # store_address = [tag.text.strip() for tag in store_address if tag.text.strip()]
    store_address = store_address.text.strip()
    # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_address:
        print(f"주소: {store_address}")
    else:
        store_address = "주소없음"
        print(store_address)
    time.sleep(3)
    # 영업시간 셀레리움 에서 선택 사용 예정
    # span class "pwY9x"(확정)
    store_time = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.pwY9x")))        
    # EC.element_to_be_clickable
    # EC.presence_of_all_elements_located
     # 영업시간 로드안됨으로 인해 클릭해서 확인
    store_time.click()
    time.sleep(3)
    # print(store_time)
    # span class "i8cJw" 이건 요일 그안에있는내용까지 싹다 긁어와야됨
    # store_text_times = soup.select('span.i8cJw')
    store_text_times = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.i8cJw")))
    # 찾은 태그들에서 텍스트만 뽑아서 공백을 제거하고 리스트로 만듭니다.
    # (빈 텍스트가 있다면 걸러내는 조건도 추가)
    store_text_times = [tag.text.strip() for tag in store_text_times if tag.text.strip()]

    # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_text_times:
        # 리스트 안의 요소들을 쉼표(,)로 연결해서 하나의 문자열로 만듭니다.
        store_times_str = ",".join(store_text_times)
        print(f"{store_times_str}")
    else:
        store_times_str = "영업시간 정보 없음"
        print(store_times_str)

    store_text_tag_times = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.H3ua4")))
    
    store_text_tag_times = [tag.text.strip() for tag in store_text_tag_times if tag.text.strip()]
        # 3. 데이터가 있을 때와 없을 때 예외 처리 후 출력
    if store_text_tag_times:
        # 리스트 안의 요소들을 쉼표(,)로 연결해서 하나의 문자열로 만듭니다.
        store_times_tag_str = ",".join(store_text_tag_times)
        print(f"{store_times_tag_str}")
    else:
        store_times_tag_str = "영업시간 정보 없음"
        print(store_times_tag_str)
    

    data_home = {print(f" {store_name.text.strip()}, {store_reviews_str}, {store_phone}, {store_address}, {store_times_str}, {store_times_tag_str}")}




#         # span "GHAhO" #업체이름
#         # span class "PXMot" #방문자 리뷰 수, 블로그 리뷰수(클래스 안에 각각 있음 방문자 리뷰(숫자), 블로그 리뷰(숫자))
#         # span class "pz7wy" #주소
#         # #영업시간 셀레리움 써서 따서 써야됨 확인불가-클릭해서 보기전까지 못보게 막아둠 추후 고민
#         # span class "xlx7Q" #전화번호
        
#     }

#     print(f"업체이름 : {data_home['span GHAhO']}"
#            "방문자 리뷰 수,블로그 리뷰 수 : {data_home['span class "PXMot"']}"
#            "주소 : {data_home['span class "pz7wy"']}"
#            "영업시간 : {data_home['span class "xlx7Q"']}")


#     # 업체 대표 사진 수집하는 코드 작성
#     driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/photo?filterType=업체")

#     # 메뉴 정보 수집하는 코드 작성 (메뉴는 url형식이 달라서 home으로 접속한 뒤 메뉴 탭을 직접 클릭해서 데이터를 크롤링하는 방식)
#     driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/home")

# # 만약에 수집이 안되는 데이터가 있다면, 따로 해당 업체를 저장하는 코드 작성(try except문 활용하여 수집이 안되는 데이터가 있는 업체는 별도의 리스트로 저장하는 방식)

# # 업체 1곳 끝날때 마다 중간 저장하는 코드 작성 -> url 테이블의 is_done 컬럼을 Y로 업데이트 하는 방식으로 같이 작성

# # 수집한 데이터를 임시 리스트에 저장하는 코드 작성

# # 임시 리스트에 있는 데이터를 일괄적으로 raw table에 저장하는 코드 작성 (리뷰는 리뷰 테이블, 업체 관련 정보는 store 테이블에 일괄 저장)





#  service폴더의 Crawling.py 를 실행
# Crawling.py: DBManager객체 생성( DB접속,쿼리 실행, DB닫기)  ,쿼리문 함수 정의 
#  1.  crawl.py의 insert함수 실행 

   crawl.insert(AREA, STORE_CODE, NAVER_URL)








driver.quit()