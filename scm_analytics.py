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

# 4. 기본 재고량 설정
base_stock = 100 
cart_df["base_stock"] = base_stock

# 5. 재고 회전율 계산
cart_df["turnover_ratio"] = cart_df["sales_count"] / cart_df["base_stock"]

# 6. 회전율이 낮은 제품 조정
low_turnover_mask = cart_df["turnover_ratio"] < 0.3 
cart_df.loc[low_turnover_mask, "base_stock"] = ( cart_df.loc[low_turnover_mask, "sales_count"] / 0.3 ).round(0).astype(int)

# 7. 회전율 다시 계산
cart_df["turnover_ratio"] = cart_df["sales_count"] / cart_df["base_stock"]

# 8. 날짜 컬럼 추가
cart_df["partition_date"] = today

# 9. 결과 출력
print("SCM KPI 결과:")
print(cart_df.head())
