import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta  # <--- บรรทัดนี้สำคัญมาก ห้ามขาด!
import plotly.express as px
# การตั้งค่าหน้าเว็บ
st.set_page_config(page_title="VM", layout="wide")

# ฟังก์ชันเชื่อมต่อ Database
def get_data():
    # ใช้ Connection String เดียวกับด้านบน
    db_url = "postgresql://postgres.ccudavykwzwwjavjlase:IksRDasWWFb2ni2X@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
    conn = psycopg2.connect(db_url)
    query = "SELECT * FROM transactions"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ส่วนหัวของ Dashboard
st.title("Vending Machine")
st.markdown("---")

try:
    df = get_data()

    # --- ส่วนที่ 1: สรุปตัวเลขสำคัญ (Metrics) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales (THB)", f"{df['amount_paid'].sum():,.2f}")
    with col2:
        st.metric("Total Transactions", len(df))
    with col3:
        st.metric("Total Water Sold (Liters)", f"{df['water_volume'].sum():,.2f}")

    st.markdown("---")

    # --- ส่วนที่ 2: กราฟวิเคราะห์ข้อมูล ---
    left_column, right_column = st.columns(2)

    # กราฟยอดขายตามวิธีชำระเงิน
    with left_column:
        st.subheader("Payment Method Split")
        fig_payment = px.pie(df, names='payment_method', values='amount_paid', hole=0.4)
        st.plotly_chart(fig_payment, use_container_width=True)

    # กราฟแนวโน้มยอดขายตามเวลา
    with right_column:
        st.subheader("Sales Trend")
        df['datetime'] = pd.to_datetime(df['datetime'])
        sales_trend = df.groupby(df['datetime'].dt.date)['amount_paid'].sum().reset_index()
        fig_trend = px.line(sales_trend, x='datetime', y='amount_paid', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- ส่วนที่ 3: ตารางข้อมูลล่าสุด ---
    st.subheader("Recent Transactions")
    st.dataframe(df.sort_values(by='datetime', ascending=False).head(10), use_container_width=True)

except Exception as e:

    st.error(f"Error connecting to database: {e}")




