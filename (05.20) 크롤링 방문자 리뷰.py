from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
import sys
from datetime import datetime


# db에 저장된 업체 코드 리스트 불러오는 코드 작성
codes = ["17040255"]
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

    driver.get(f"https://pcmap.place.naver.com/restaurant/{store_code}/review/visitor?reviewSort=recent")
    time.sleep(2)


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
    
    # 최신순으로 변경 선택 로직 들어가야됨
    # 태그 div class "place_option_area mlywZ" 의 a태그의 role="option" class="place_btn_option" 눌러야됨
    new_list = "div.place_option_area.mlywZ a.place_btn_option[role='option']"

    # 최신순으로 누르기
    new_list_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, new_list)))
    new_list_button.click()
    time.sleep(2)


    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 1. 모든 li 요소를 가져옵니다.
    li_elements = soup.select('li.place_apply_pui.EjjAW')

    # 2. 각 li 요소를 순회하며 원하는 텍스트 추출
    for idx, li in enumerate(li_elements, 1):
        # li 내부의 특정 경로를 지정하되, 마지막 span.pui__blind 중 2번째(nth-of-type(2))를 선택합니다.
        target_span = li.select_one('div.pui__QztK4Q > div.Vk05k > div.pui__QKE5Pr > span.pui__gfuUIT > span.pui__blind:nth-of-type(2)')
    
        if target_span:
            print(f"[{idx}] 추출된 텍스트: {target_span.get_text(strip=True)}")
        else:
            print(f"[{idx}] 두 번째 pui__blind 요소를 찾지 못했습니다.")
        time.sleep(2)
    

    # --- [설정] 기준 날짜 정의 ---
    CUTOFF_DATE = datetime(2025, 5, 1)

    def parse_date_str(date_str):
        # '2026년 4월 11일 토요일' 형태의 문자열을 datetime 객체로 변환 
        try:
            # 공백으로 나눈 뒤 년, 월, 일 부분만 합침 (예: "2026년", "4월", "11일")
            parts = date_str.split(" ")
            clean_str = parts[0] + parts[1] + parts[2]
            return datetime.strptime(clean_str, "%Y년%m월%d일")
        except Exception:
            return None

    def check_should_stop(html_source):

        #현재 페이지의 HTML을 분석하여 
        #펼쳐보기 버튼을 '그만 누를지(True)' 아니면 '더 누를지(False)' 결정합니다.
        
        soup = BeautifulSoup(html_source, "html.parser")
        li_elements = soup.select('li.place_apply_pui.EjjAW')
    
        for idxx, li in enumerate(li_elements, 1):
            target_span = li.select_one('div.pui__QztK4Q > div.Vk05k > div.pui__QKE5Pr > span.pui__gfuUIT > span.pui__blind:nth-of-type(2)')
        
            if target_span:
                date_text = target_span.get_text(strip=True)
                date_obj = parse_date_str(date_text)
            
                # 조회된 날짜가 기준 날짜(2025년 5월 1일)보다 이전인지 비교
                if date_obj and date_obj < CUTOFF_DATE:
                    print(f"[{idxx}] {date_text}  기준 날짜 이전 펼쳐내기를 중단합니다.")
                    return True  # 멈춤
                
                print(f"[{idxx}] {date_text}    기준 날짜 이후이므로 통과 (계속 진행)")
            
        return False  # 기준 미만 날짜가 없으니 계속 더보기 눌러도 됨!
    while True:
        # 1. [조회 및 결정] 현재 화면 HTML을 분석해서 더보기를 멈출지 판단합니다.
        if check_should_stop(driver.page_source):
            print(">> 조건을 만족하여 루프를 종료합니다. 버튼을 더 이상 누르지 않습니다.")
            break # while 루프 탈출 (클릭하지 않음)
        
        # 2. [버튼 누르기 위치] 과거 날짜가 없다면 아래로 내려와서 버튼을 누릅니다.
        try:
            
            more_button = driver.find_element(By.CSS_SELECTOR, "span.TeItc") 
        
            if more_button.is_displayed():
            
                more_button.click() #  클릭
            
                time.sleep(2) # 버튼 클릭 후 새 데이터가 아래에 추가로 로딩될 때까지 기다림
            else:
                print(">> 더보기 버튼이 화면에 보이지 않아 종료합니다.")
                break
        except Exception as e:
            print(">> 더보기 버튼을 찾을 수 없거나 끝에 도달하여 종료합니다.")
            break

        
        
        print("펼쳐내기 종료")
        review_date = driver.find_elements(By.CSS_SELECTOR, "span.pui__NMi-Dp")
        review_counts = len(review_date)
        
        print(f"찾은 리스트 아이템 개수: {review_counts}개")

    # 반복 횟수로 진행하려 했으나 더보기의 개수나 맛있어요 카테고리 + 버튼이 각각 다름으로 인해 li class를 통째로 하여 진행    
    # 1. li 태그를 기준으로 전체 카테고리 상자 개수를 구합니다.
    items = driver.find_elements(By.CSS_SELECTOR, "li.place_apply_pui.EjjAW")
    total_items = len(items)
    print(f"총 {total_items}개의 카테고리 리스트(li)를 찾았습니다.")

    # 2. 개수만큼 반복합니다.
    for idr in range(total_items):
        try:
            # 동적 로딩 대응: 루프가 돌 때마다 li 목록을 매번 새로 가져옵니다. 세션 만료 떄문인듯?
            items = driver.find_elements(By.CSS_SELECTOR, "li.place_apply_pui.EjjAW")
            current_item = items[idr]
            
            # 현재 검사 중인 li 상자 자체를 화면 중앙으로 이동시킵니다.-가시성 확인용
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_item)
            time.sleep(0.5)
            
            # 전체 화면이 아니라, '현재 li 상자 안에서만' 각각의 버튼을 찾습니다. - 반복할시 변화되서 중간에 막힘 카테고리 선택쪽에서 막힘
            more_buttons = current_item.find_elements(By.CSS_SELECTOR, ".pui__GStJHb.pui__wFzIYl")
            plus_buttons = current_item.find_elements(By.CSS_SELECTOR, ".pui__GStJHb.pui__jhpEyP.pui__ggzZJ8")
        
            # 해당 li 안에 버튼이 존재하는지 체크 (없으면 None)
            target_button = more_buttons[0] if len(more_buttons) > 0 else None
            target_plus_button = plus_buttons[0] if len(plus_buttons) > 0 else None
            
            # 텍스트 읽어오기
            button_text = target_button.text if target_button else ""
        
            # ------------------ [조건 분기 시작] ------------------
        
            # [조건 1] 이 li 상자 안에 더보기 버튼이 있고, 글자도 '더보기'가 맞다면?
            if target_button and "더보기" in button_text:
                target_button.click()  # 일반 클릭 진행
                print(f"[{idr + 1}/{total_items}] 해당 li의 '더보기' 버튼 클릭 완료") # for문은 0부터 시작
                time.sleep(2)  # 내용이 열리는 대기 시간
        
            # [조건 2] '더보기' 글자가 없을 때만 이쪽 else로 들어옵니다.
            else:
                # 이 li 상자 안에 플러스 버튼이 존재한다면 바로 클릭!
                if target_plus_button:
                    target_plus_button.click()  # 일반 클릭 진행
                    print(f"[{idr + 1}/{total_items}] 해당 li의 '플러스' 버튼 클릭 완료") # for문은 0부터 시작
                    time.sleep(2)  # 내용이 열리는 대기 시간
                
                # [조건 3] 둘 다 해당하지 않는 경우 패스
                else:
                    print(f"[{idr + 1}/{total_items}] 누를 버튼이 없는 구역이라 패스합니다.")
                
        # ----------------------------------------------------
        except Exception as e:
            # 클릭 실패나 에러가 나도 프로그램을 멈추지 않고 다음 li로 넘어갑니다.
            print(f"[{idr + 1}/{total_items}] 처리 중 실패 (에러 무시 후 다음 진행): {e}")

    for idxxx in range(review_counts):
        # span "pui__NMi-Dp"   아이디 
        reviewer_id_tag = review_date[idxxx]
        if reviewer_id_tag:
            reviewer_id = reviewer_id_tag.text.strip()
            print(f"{idxxx + 1}번째\n 이름 : {reviewer_id}")  # 출력결과: 댓글쓴이
        else:
            print("댓글쓴이를 찾지 못했습니다.")
 
        review_contents = driver.find_elements(By.CSS_SELECTOR, ".pui__vn15t2")
        
        if review_contents:
            content_text = review_contents[idxxx].get_attribute("textContent")
            print(content_text)  # 출력결과: 댓글내용
        else:
            print("댓글내용을 찾지 못했습니다.")
        time.sleep(2)
    
        # 댓글 카테고리
        review_categorys = driver.find_elements(By.CSS_SELECTOR, "div.pui__HLNvmI")
        
        if review_categorys:
            review_category = review_categorys[idxxx].text.replace("요", "요, ").rstrip(", ")
            print(review_category)  # 출력결과: 댓글카테고리
        else:
            print("댓글카테고리를 찾지 못했습니다.")

        # 방문 날짜

        if target_span:
            print(f" 방문날짜 : {target_span.get_text(strip=True)}")
        else:
            print(f"[{idxxx}] 두 번째 pui__blind 요소를 찾지 못했습니다.")
        time.sleep(2)



    

    print(f"업체 이름:{store_name},업체코드:{store_code},마무리 확인용")

     


driver.quit()