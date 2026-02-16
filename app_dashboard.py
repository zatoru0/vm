import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime

# --- 1. ตั้งค่าการเชื่อมต่อ (ใช้ข้อมูลเดิมของคุณ) ---
DB_URL = "postgresql://postgres.ccudavykwzwwjavjlase:IksRDasWWFb2ni2X@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_data():
    try:
        conn = psycopg2.connect(DB_URL)
        df = pd.read_sql("SELECT * FROM transactions ORDER BY datetime DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def save_transaction(amount, method):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        volume = round(amount * 0.66, 2)
        query = "INSERT INTO transactions (machine_id, amount_paid, water_volume, payment_method, payment_status) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, ('VM-001', amount, volume, method, 'Success'))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# --- 3. ออกแบบหน้าเว็บ ---
st.set_page_config(page_title="Vending IoT System", layout="wide")

# สร้าง Tabs สำหรับสลับหน้า
tab1, tab2 = st.tabs(["📊 Dashboard Analytics", "🛒 Water Simulator"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.title("📈 Dashboard Performance")
    df = get_data()
    
    if not df.empty:
        # ส่วน Metrics (เลียนแบบภาพ 181151)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Income", f"฿ {df['amount_paid'].sum():,.2f}", "+12%")
        m2.metric("Orders", len(df), "+5%")
        m3.metric("Water Sold (L)", f"{df['water_volume'].sum():,.2f} L")
        
        st.markdown("---")
        
        # กราฟยอดขาย
        fig = px.line(df.groupby('datetime')['amount_paid'].sum().reset_index(), 
                     x='datetime', y='amount_paid', title="Sales Trend",
                     template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ยังไม่มีข้อมูลการขาย")

# --- TAB 2: SIMULATOR (เลียนแบบภาพ 181131) ---
with tab2:
    st.title("🥤 เลือกซื้อน้ำดื่ม")
    st.subheader("สัมผัสหน้าจอเพื่อเลือกรายการ")
    
    # จำลองรายการสินค้า
    products = [
        {"name": "น้ำดื่ม 5 บาท", "price": 5, "img": "https://cdn-icons-png.flaticon.com/512/3100/3100566.png"},
        {"name": "น้ำดื่ม 10 บาท", "price": 10, "img": "https://cdn-icons-png.flaticon.com/512/3100/3100566.png"},
        {"name": "น้ำดื่ม 15 บาท", "price": 15, "img": "https://cdn-icons-png.flaticon.com/512/3100/3100566.png"},
        {"name": "น้ำดื่ม 20 บาท", "price": 20, "img": "https://cdn-icons-png.flaticon.com/512/3100/3100566.png"},
    ]
    
    # แสดงรูปสินค้าเป็นคอลัมน์
    cols = st.columns(4)
    for i, p in enumerate(products):
        with cols[i]:
            st.image(p['img'], width=100)
            st.write(f"**{p['name']}**")
            if st.button(f"เลือก {p['price']}.-", key=f"btn_{i}"):
                st.session_state.selected_price = p['price']
    
    st.markdown("---")
    
    # เลือกวิธีชำระเงินและกดยืนยัน
    if 'selected_price' in st.session_state:
        st.info(f"คุณเลือก: {st.session_state.selected_price} บาท")
        pay_method = st.radio("เลือกวิธีชำระเงิน", ["Cash", "QR_Code"], horizontal=True)
        
        if st.button("✅ ยืนยันการซื้อ", type="primary"):
            if save_transaction(st.session_state.selected_price, pay_method):
                st.success("ขอบคุณที่ใช้บริการ! กำลังจ่ายน้ำ...")
                st.balloons()
                del st.session_state.selected_price # ล้างค่าหลังซื้อเสร็จ
                st.rerun()
