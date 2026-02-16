import streamlit as st
import pandas as pd
import psycopg2
import time

# --- การตั้งค่าการเชื่อมต่อ (ใช้ตัวเดิมของคุณ) ---
DB_URL = "postgresql://postgres.ccudavykwzwwjavjlase:IksRDasWWFb2ni2X@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# --- ฟังก์ชันเขียนข้อมูล (สำหรับหน้า Simulator) ---
def record_transaction(amount, method):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        volume = round(amount * 0.66, 2)
        query = """INSERT INTO transactions (machine_id, amount_paid, water_volume, payment_method, payment_status) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, ('VM-001', amount, volume, method, 'Success'))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- ฟังก์ชันดึงข้อมูล (สำหรับหน้า Dashboard) ---
def get_data():
    conn = psycopg2.connect(DB_URL)
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    return df

# --- ส่วนของการสร้างหน้าเว็บ ---
st.title("🥤 Smart Vending System")

# สร้าง Tab สลับหน้า
tab1, tab2 = st.tabs(["📊 Dashboard", "🛒 Machine Simulator"])

# --- หน้า Dashboard ---
with tab1:
    st.header("Real-time Analytics")
    df = get_data()
    st.metric("Total Sales", f"{df['amount_paid'].sum()} THB")
    st.line_chart(df.set_index('datetime')['amount_paid'])

# --- หน้า Simulator (เหมือนอยู่หน้าตู้จริง) ---
with tab2:
    st.header("หน้าจอจำลองหน้าตู้กดน้ำ")
    st.info("กรุณาเลือกจำนวนเงินและวิธีชำระเงินเสมือนคุณอยู่ที่หน้าตู้")
    
    col1, col2 = st.columns(2)
    with col1:
        amount = st.selectbox("เลือกจำนวนเงิน (บาท)", [5, 10, 15, 20])
    with col2:
        method = st.radio("วิธีชำระเงิน", ["Cash", "QR_Code"])

    if st.button("💰 ยืนยันการชำระเงิน (ซื้อสินค้า)"):
        with st.spinner('กำลังประมวลผล...'):
            success = record_transaction(amount, method)
            if success:
                st.success(f"ชำระเงินสำเร็จ! จ่ายน้ำ {round(amount * 0.66, 2)} ลิตร")
                st.balloons() # ใส่ Effect ฉลองหน่อย
                time.sleep(2)
                st.rerun() # รีเฟรชหน้าเพื่ออัปเดตข้อมูล
