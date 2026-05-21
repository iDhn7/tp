from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

# db에 저장된 업체 코드 리스트 불러오는 코드 작성
codes = ["1496549723"]
# 17040255,"1647184627","2088731895","1496549723"] # 예시로 한 것, 실제로는 db에서 불러와야 함

options = webdriver.ChromeOptions()
 # options.add_argument('headless') # 브라우저 창을 띄우지 않고 실행하려면 주석해제
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)
# https://pcmap.place.naver.com/restaurant/1496549723/information
for store_code in codes:
    # 리뷰 수집하는 코드 작성 
    # 방문자 리뷰 주소: driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/review/visitor?reviewSort=recent")
    # 블로그 리뷰 주소: driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/review/ugc?reviewSort=recent&type=list")



    # 메뉴 정보 수집하는 코드 작성 (메뉴는 url형식이 달라서 home으로 접속한 뒤 메뉴 탭을 직접 클릭해서 데이터를 크롤링하는 방식)
    driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/home")
    # 상위 탭으로 찾을려고 했지만 상위 태그가 클래스명이 바뀜 하위 클래스명 동일로 하위 클래스명 사용
    # 모든 하위 클래스 수집후 텍스트 확인 텍스트에서 메뉴라고 불리는 클래스 선택 클릭한뒤 url 수집 예정
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)

    # 'GHAhO' 클래스를 가진 첫 번째 span 태그 찾기
    store_name_tag = soup.find('span', class_='GHAhO')
    # store_name = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.GHAhO")))
    if store_name_tag:
        store_name = store_name_tag.text.strip()
        print(store_name)  # 출력결과: 업체이름
    else:
        print("가게 이름을 찾지 못했습니다.")
    
    try:
    # 1. 텍스트가 정확히 '메뉴'인 span 태그를 찾은 뒤, 바로 위에 있는 부모 a 태그(..)를 선택합니다.
        menu_link_element = driver.find_element(By.XPATH, "//span[text()='메뉴']/..")
    
    # 2. 부모 a 태그에서 href 속성(URL)을 추출합니다.
        menu_url = menu_link_element.get_attribute("href")
        print(f"{menu_url}")
        match = re.search(r"bizes/(.*?)\?", menu_url)
        print(f"메뉴 일련번호: {match.group(1)}")

    except Exception as e:
        print("메뉴 탭을 찾지 못했습니다. 구조를 다시 확인해주세요.")
            


# 만약에 수집이 안되는 데이터가 있다면, 따로 해당 업체를 저장하는 코드 작성(try except문 활용하여 수집이 안되는 데이터가 있는 업체는 별도의 리스트로 저장하는 방식)

# 업체 1곳 끝날때 마다 중간 저장하는 코드 작성 -> url 테이블의 is_done 컬럼을 Y로 업데이트 하는 방식으로 같이 작성

# 수집한 데이터를 임시 리스트에 저장하는 코드 작성

# 임시 리스트에 있는 데이터를 일괄적으로 raw table에 저장하는 코드 작성 (리뷰는 리뷰 테이블, 업체 관련 정보는 store 테이블에 일괄 저장)

driver.quit()