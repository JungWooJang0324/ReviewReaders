from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Selenium 설정
service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')

# Musinsa 상품 페이지 URL
url = "https://www.musinsa.com/review/goods/1551840"

# Selenium으로 크롤링 시작
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)

try:
    # 페이지 열기
    driver.get(url)
    time.sleep(3)

    # 스냅 후기 데이터 추출을 위한 초기화
    snap_user_lst = []
    snap_date_lst = []
    snap_star_lst = []
    snap_desc_lst = []

    # 스크롤 반복 제한
    scroll_limit = 5
    scroll_count = 0

    while scroll_count < scroll_limit:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 로딩 대기
        
        # 데이터 추출
        snap_users = driver.find_elements(By.CSS_SELECTOR, '.text-body_13px_med.text-black.font-pretendard')
        snap_dates = driver.find_elements(By.CSS_SELECTOR, '.text-body_13px_reg.text-gray-500.font-pretendard')
        snap_stars = driver.find_elements(By.CSS_SELECTOR, '.text-body_13px_semi.font-pretendard')
        snap_descriptions = driver.find_elements(By.CSS_SELECTOR, '.TruncateContent__ContentContainer-sc-5tx4vi-1.dlzlgl')

        # 데이터 리스트에 추가
        for user, date, star, desc in zip(snap_users, snap_dates, snap_stars, snap_descriptions):
            snap_user_lst.append(user.text)
            snap_date_lst.append(date.text)
            snap_star_lst.append(star.text)
            snap_desc_lst.append(desc.text.replace('\n', ' '))
        
        # 스크롤 카운트 증가
        scroll_count += 1

        # 중간 데이터 저장
        snap_data_partial = pd.DataFrame(
            zip(snap_user_lst, snap_date_lst, snap_star_lst, snap_desc_lst),
            columns=['사용자 ID', '작성 날짜', '평점', '설명']
        )
        snap_data_partial.to_csv("musinsa_snap_reviews_partial.csv", index=False, encoding='utf-8-sig')

    # 최종 데이터 저장
    snap_data = pd.DataFrame(
        zip(snap_user_lst, snap_date_lst, snap_star_lst, snap_desc_lst),
        columns=['사용자 ID', '작성 날짜', '평점', '설명']
    )
    snap_data.to_csv("musinsa_snap_reviews.csv", index=False, encoding='utf-8-sig')

    print(f"크롤링 완료! 스냅 후기가 musinsa_snap_reviews.csv에 저장되었습니다.")

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    driver.quit()
