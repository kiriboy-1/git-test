from sqlalchemy import create_engine, text
import pandas as pd
import datetime
import traceback

def run_scm_kpi():
    try:
        # 1. DB 연결
        engine = create_engine("mysql+pymysql://dongdong:20250517@192.168.14.47:3306/ai_re")

        # 2. 오늘 날짜
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        # 3. 판매량 데이터 불러오기
        cart_query = """
            SELECT productname, COUNT(*) AS 판매량
            FROM cart
            GROUP BY productname
        """
        cart_df = pd.read_sql(text(cart_query), engine)

        # 4. 기준 재고량 설정 (초기값 100)
        cart_df["기준재고"] = 100

        # 5. 재고 회전율 계산
        cart_df["재고회전율"] = cart_df["판매량"] / cart_df["기준재고"]
        cart_df["partition_date"] = today

        # 6. 재고회전율이 낮은 제품 재고 자동 보정
        low_turnover_mask = cart_df["재고회전율"] < 0.3
        cart_df.loc[low_turnover_mask, "기준재고"] = cart_df.loc[low_turnover_mask, "판매량"] / 0.3
        cart_df["재고회전율"] = cart_df["판매량"] / cart_df["기준재고"]

        # 7. 테이블 생성
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scm_metrics (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    productname VARCHAR(255),
                    판매량 INT,
                    기준재고 FLOAT,
                    재고회전율 FLOAT,
                    partition_date DATE
                )
            """))

        # 8. 결과 저장
        cart_df.to_sql("scm_metrics", con=engine, if_exists="append", index=False)

        print("✅ SCM KPI 저장 완료")
        print(cart_df.head())

    except Exception as e:
        print("❌ 에러 발생:")
        traceback.print_exc()

if __name__ == "__main__":
    run_scm_kpi()
