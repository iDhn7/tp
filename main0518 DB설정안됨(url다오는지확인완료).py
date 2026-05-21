from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

region = ["전북대","한옥마을","객사","신시가지"]
for i in region:
    url = f"https://map.naver.com/p/search/전주%20{i}%20맛집"
    print(url)
    print(i,"지역의 맛집 정보를 크롤링합니다")

    # 가게 이름, 상세 페이지 링크 크롤링하고 일련번호 따는 코드
    options = webdriver.ChromeOptions()
    # options.add_argument('headless') # 브라우저 창을 띄우지 않고 실행하려면 주석해제
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # iframe 전환
    wait.until(EC.frame_to_be_available_and_switch_to_it("searchIframe"))
    # 클래스 이름에 'mBN2s'가 포함되어 있고, 텍스트가 정확히 '숫자(1-5)'인 'a' 태그 찾기 네이버엔 1-5까지 숫자 밖에 없기떄문에 하드코딩
    for idxx in range (1,6):
        xpath_selector = f"//a[contains(@class, 'mBN2s') and text()='{idxx}']"
        target_link = driver.find_element(By.XPATH, xpath_selector)
        # 클릭
        target_link.click()

        time.sleep(8) # 결과를 확인하기 위한 대기

        # 스크롤 설정값
        scroll_pause_time = 3.0  # 스크롤 간 대기 시간
        load_wait_time = 5.0     # 마지막 도달 후 대기 시간

        # 1. 스크롤 가능한 컨테이너 찾기
        scroll_container = driver.find_element(By.ID, "_pcmap_list_scroll_container")

        # 2. 초기 높이 저장
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)

        while True:
            # 3. 컨테이너 내부를 끝까지 스크롤
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            time.sleep(scroll_pause_time)

            # 4. 새로운 높이 측정
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            
            # 5. 높이가 변하지 않았으면 종료 (혹시 모를 로딩을 위해 한 번 더 확인)
            if new_height == last_height:
                time.sleep(load_wait_time)
                new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                if new_height == last_height:
                    print("모든 항목 로드 완료")
                    break
            
            last_height = new_height

        list_items = driver.find_elements(By.CSS_SELECTOR, ".UEzoS.rTjJo")
        item_count = len(list_items)
        print(f"찾은 리스트 아이템 개수: {item_count}개")

        # min(40, item_count)를 사용하면 if 조건문 분기가 아예 필요 없어집니다.
        for idx in range(0, min(40, item_count)):
            # iframe을 새로 바꿨기 때문에, 현재 화면(searchIframe) 기준으로 요소를 매번 새로 찾아야 합니다.
            # iframe 세션 만료로 인해 인덱스 확인불가 상황이 자꾸지속됨
            current_items = driver.find_elements(By.CSS_SELECTOR, ".UEzoS.rTjJo")
            # 이제 인덱스 범위를 바로위에서 확인하고 진행
            current_items[idx].click()
            time.sleep(3)       
            
            driver.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it("searchIframe"))

        print("지정한 범위 수집 완료, 다음 작업 바로 시작!")

        
        # list_items = driver.find_elements(By.CSS_SELECTOR, ".UEzoS.rTjJo")
        # # 개수 확인
        # item_count = len(list_items)
        # print(f"찾은 리스트 아이템 개수: {item_count}개")
        
        # for idx in range(0, 40):
        #     # 데이터 개수 확인하고 많을시 정지 맨마지막 페이지 같은경우 39개가 안됨

        #     # 상세 페이지 링크 추출, href 속성이 #으로 되어 있어서, 클릭 후 url 추출하는 방식으로 진행해야 할 듯
        #     list_items[idx].click()
        #     time.sleep(3)       
        #     driver.switch_to.default_content()
        #     wait.until(EC.frame_to_be_available_and_switch_to_it("searchIframe"))
        #     if idx > item_count: 
        #         print("데이터보다 많을시 다음 작업바로시작")
        #         break 



       # 직접 확인하지않으면 데이터 로드 되지않아 개수 확인용
        list_itemxs = driver.find_elements(By.CSS_SELECTOR, ".UEzoS.rTjJo")
        item_countx = len(list_itemxs)
        
        print(f"찾은 리스트 아이템 개수: {item_countx}개")

        # sys.exit()
        
        # 여러 요소 가져오기
        
        store_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.TYaxT")))        
        for idxx in range(item_countx):

            
            # 가게 이름 추출
            store_names = store_elements[idxx].text.strip()

            # 상세 페이지 링크 추출, href 속성이 #으로 되어 있어서, 클릭 후 url 추출하는 방식으로 진행해야 할 듯
            store_elements[idxx].click()
            time.sleep(3)
            target_url = driver.current_url
            if i == "전북대":
                area = "A"
            elif i == "신시가지":
                area = "B"
            else:
                area = "C"
            store_code = target_url.split("place/")[1].split("?")[0]
            # 크롤링한 데이터를 임시 리스트에 저장하는 코드 (후에 db에 저장할 때 사용)
            data = {
                "store_name": store_names,
                "target_url": target_url ,
                "store_code": store_code,
                "area" : area 
                
            }
            print(data)

            # 업체 상세 정보 url을 다음처럼 만들어서 각각 크롤링하는 코드 작성
            # 메뉴는 url 형식이 달라서 직접 클릭을 한 후에 데이터를 크롤링하는 방식으로 진행해야 할 듯
            review_url = f"https://pcmap.place.naver.com/restaurant/{store_code}/review"
            info_url = f"https://pcmap.place.naver.com/restaurant/{store_code}/information"
            photo_url = f"https://pcmap.place.naver.com/restaurant/{store_code}/photo?filterType=업체"
        
            # 다시 iframe으로 돌아오기
            driver.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it("searchIframe"))


    #임시 리스트에 있는 데이터를 db에 저장하는(insert)코드 
    
    
    
    driver.quit()