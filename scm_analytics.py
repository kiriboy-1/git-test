from sqlalchemy import create_engine, text
import pandas as pd
import datetime

# 1. DB 연결
engine = create_engine("mysql+pymysql://dongdong:20250517@192.168.14.47:3306/ai_re")

# 2. 오늘 날짜
today = datetime.datetime.now().strftime('%Y-%m-%d')

# 3. cart 테이블에서 제품별 판매량 집계
query = """
    SELECT productname, COUNT(*) AS sales_count
    FROM cart
    GROUP BY productname
"""
df = pd.read_sql(text(query), engine)

# 4. 모든 제품의 재고량을 100으로 설정
df["base_stock"] = 100

# 5. 재고 회전율 계산: 판매량 / 재고
df["turnover_ratio"] = df["sales_count"] / df["base_stock"]

# 6. 날짜 컬럼 추가
df["partition_date"] = today

# 7. 결과 출력
print("✅ SCM KPI 재고 회전율 결과:")
print(df.head())

# (선택) 결과를 CSV로 저장
# df.to_csv("scm_kpi_result.csv", index=False
