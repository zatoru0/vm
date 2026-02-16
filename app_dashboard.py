import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# --- 1. ตั้งค่าการเชื่อมต่อ ---
DB_URL = "postgresql://postgres.ccudavykwzwwjavjlase:IksRDasWWFb2ni2X@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_data():
    try:
        conn = psycopg2.connect(DB_URL)
        query = "SELECT datetime, amount_paid, water_volume, payment_method, payment_status FROM transactions ORDER BY datetime DESC"
        df = pd.read_sql(query, conn)
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

# --- ฟังก์ชันใหม่: ล้างข้อมูลทั้งหมด ---
def clear_all_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        # ลบข้อมูลและรีเซ็ต ID กลับไปเริ่มที่ 1
        cursor.execute("TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
        return False

# --- 3. ออกแบบหน้าเว็บ ---
st.set_page_config(page_title="Vending IoT System", layout="wide")

tab1, tab2 = st.tabs(["📋 รายการคำสั่งซื้อ", "🛒 หน้าตู้กดน้ำ"])

# --- TAB 1: รายการคำสั่งซื้อ ---
with tab1:
    st.title("📋 ประวัติการสั่งซื้อล่าสุด")
    df = get_data()
    
    # ส่วนหัวและปุ่มล้างข้อมูล
    col_head, col_btn = st.columns([4, 1])
    with col_btn:
        # ใช้ปุ่มล้างข้อมูลแบบมีกดยืนยัน (Confirmation)
        if st.button("🗑️ ล้างประวัติทั้งหมด", type="secondary"):
            st.session_state.confirm_delete = True
            
        if st.session_state.get('confirm_delete'):
            st.warning("คุณแน่ใจใช่ไหมที่จะลบข้อมูลทั้งหมด?")
            c1, c2 = st.columns(2)
            if c1.button("ใช่, ลบเลย", type="primary"):
                if clear_all_data():
                    st.success("ล้างข้อมูลสำเร็จ!")
                    st.session_state.confirm_delete = False
                    st.rerun()
            if c2.button("ยกเลิก"):
                st.session_state.confirm_delete = False
                st.rerun()

    if not df.empty:
        col1, col2 = st.columns(2)
        col1.metric("ยอดรวมรายได้ทั้งหมด", f"฿ {df['amount_paid'].sum():,.2f}")
        col2.metric("จำนวนคำสั่งซื้อทั้งหมด", f"{len(df)} รายการ")
        
        st.markdown("---")
        df_display = df.copy()
        df_display.columns = ['วัน-เวลาที่สั่งซื้อ', 'ราคา (บาท)', 'ปริมาณน้ำ (ลิตร)', 'วิธีชำระเงิน', 'สถานะ']
        st.dataframe(df_display, use_container_width=True, height=500)
    else:
        st.info("ยังไม่มีรายการคำสั่งซื้อในขณะนี้")

# --- TAB 2: SIMULATOR (เหมือนเดิม) ---
with tab2:
    st.title("🥤 ตู้กดน้ำดื่ม (Simulator)")
    products = [
        {"price": 5, "label": "น้ำดื่มขนาดเล็ก"},
        {"price": 10, "label": "น้ำดื่มขนาดกลาง"},
        {"price": 15, "label": "น้ำดื่มขนาดใหญ่"},
        {"price": 20, "label": "น้ำดื่มจุใจ"}
    ]
    
    cols = st.columns(4)
    for i, p in enumerate(products):
        with cols[i]:
            if st.button(f"💧 {p['label']}\n\n{p['price']} บาท", key=f"p_{i}", use_container_width=True):
                st.session_state.selected_price = p['price']
    
    if 'selected_price' in st.session_state:
        st.markdown(f"### 💰 จำนวนเงินที่ต้องชำระ: **{st.session_state.selected_price} บาท**")
        method = st.radio("เลือกวิธีจ่ายเงิน", ["Cash", "QR_Code"], horizontal=True)
        
        if st.button("ยืนยันการสั่งซื้อ ✅", type="primary", use_container_width=True):
            if save_transaction(st.session_state.selected_price, method):
                st.success("สั่งซื้อสำเร็จ!")
                del st.session_state.selected_price
                st.rerun()
