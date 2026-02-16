import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# การตั้งค่าหน้าเว็บ
st.set_page_config(page_title="VM", layout="wide")

# ฟังก์ชันเชื่อมต่อ Database
def get_data():
    # จำลองข้อมูลแทนการเชื่อมต่อ PostgreSQL
    data = {
        'datetime': [datetime.now() - timedelta(hours=i) for i in range(20)],
        'amount_paid': [5, 10, 15, 10, 20, 5, 10, 15, 10, 5, 10, 20, 15, 10, 5, 10, 10, 5, 20, 10],
        'water_volume': [3.3, 6.6, 9.9, 6.6, 13.2, 3.3, 6.6, 9.9, 6.6, 3.3, 6.6, 13.2, 9.9, 6.6, 3.3, 6.6, 6.6, 3.3, 13.2, 6.6],
        'payment_method': ['Cash', 'QR_Code', 'Cash', 'Cash', 'QR_Code', 'Cash', 'QR_Code', 'Cash', 'Cash', 'QR_Code', 
                          'Cash', 'QR_Code', 'Cash', 'Cash', 'QR_Code', 'Cash', 'QR_Code', 'Cash', 'Cash', 'QR_Code']
    }
    df = pd.DataFrame(data)
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
