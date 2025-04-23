from sqlalchemy import create_engine, text
import pandas as pd
import datetime
import traceback

# 1. DB 연결
engine = create_engine("mysql+pymysql://dongdong:20250517@192.168.14.47:3306/ai_re")

# 2. 오늘 날짜 지정
today = datetime.datetime.now().strftime('%Y-%m-%d')

# 3. 판매량 데이터 가져오기
cart_query = """ SELECT productname, COUNT(*) AS sales_count FROM cart GROUP BY productname """
cart_df = pd.read_sql(text(cart_query), engine)

# 4. 기본 재고량 설정 (모든 제품 동일하게 100)
base_stock = 100
cart_df["base_stock"] = base_stock

# 5. 초기 재고 회전율 계산
cart_df["turnover_ratio"] = cart_df["sales_count"] / cart_df["base_stock"]

# 6. 회전율 0.3 이하 제품에 대해 재고량 재조정
low_turnover_mask = cart_df["turnover_ratio"] < 0.3
cart_df.loc[low_turnover_mask, "base_stock"] = ( cart_df.loc[low_turnover_mask, "sales_count"] / 0.3 ).round(0).astype(int)

# 7. 재조정된 기준으로 회전율 재계산
cart_df["turnover_ratio"] = cart_df["sales_count"] / cart_df["base_stock"]

# 8. 날짜 추가
cart_df["partition_date"] = today

# 9. 테이블 없으면 생성
with engine.connect() as conn: conn.execute(text(""" CREATE TABLE IF NOT EXISTS scm_metrics ( id INT PRIMARY KEY AUTO_INCREMENT, productname VARCHAR(255), sales_count INT, base_stock INT, turnover_ratio FLOAT, partition_date DATE ) """))

# 10. 테이블에 결과 저장
cart_df.to_sql("scm_metrics", con=engine, if_exists="append", index=False)

# 11. 결과 출력
print("✅ SCM KPI 통계 저장 완료") 
print(cart_df.head())
