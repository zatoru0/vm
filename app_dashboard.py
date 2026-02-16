import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
import pytz  # สำหรับจัดการเวลาประเทศไทย

# --- 1. ตั้งค่าการเชื่อมต่อ ---
DB_URL = "postgresql://postgres.ccudavykwzwwjavjlase:IksRDasWWFb2ni2X@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_data():
    try:
        conn = psycopg2.connect(DB_URL)
        query = """
            SELECT 
                datetime AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Bangkok' as datetime, 
                amount_paid, payment_method, payment_status 
            FROM transactions 
            ORDER BY datetime DESC
        """
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
        # บันทึกเวลาปัจจุบันโดยระบุเป็น UTC (เพื่อให้ AT TIME ZONE ใน get_data ทำงานถูกต้อง)
        now_utc = datetime.now(pytz.utc)
        query = """INSERT INTO transactions (machine_id, amount_paid, water_volume, payment_method, payment_status, datetime)  
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, ('VM-001', amount, volume, method, 'Success', now_utc))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def clear_all_data():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการลบข้อมูล: {e}")
        return False

# --- 3. ฟังก์ชัน Login สำหรับแอดมิน ---
def check_admin_login():
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.markdown("### Admin Only")
        password = st.text_input("กรุณาใส่รหัสผ่านแอดมิน", type="password")
        if st.button("ตกลง"):
            if password == "1234":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
        return False
    return True

# --- 4. ออกแบบหน้าเว็บ ---
st.set_page_config(page_title="Vending IoT System", layout="wide")

# CSS เพื่อจัดให้รูปภาพอยู่ตรงกลางคอลัมน์
st.markdown("""
    <style>
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛒 หน้าตู้กดน้ำ (Buy Now)", "Admin"])

# --- TAB 1: หน้าตู้กดน้ำ ---
with tab1:
    st.title("Vending Machine")
    st.info("กรุณาเลือกรายการสินค้าที่คุณต้องการ")
    
    # ข้อมูลสินค้าที่ตรงกับรูปภาพล่าสุดของคุณ
    products = [
        {"name": "Water", "price": 5, "img": "https://cdn-icons-png.flaticon.com/128/824/824239.png"},
        {"name": "Coffee", "price": 10, "img": "https://cdn-icons-png.flaticon.com/128/1047/1047503.png"},
        {"name": "Juice", "price": 15, "img": "https://cdn-icons-png.flaticon.com/128/3361/3361456.png"},
        {"name": "Beer", "price": 20, "img": "https://cdn-icons-png.flaticon.com/128/6006/6006556.png"},
    ]
    
    cols = st.columns(4)
    for i, p in enumerate(products):
        with cols[i]:
            st.image(p['img'], width=100)
            if st.button(f"{p['name']}\n\n{p['price']} บาท", key=f"p_{i}", use_container_width=True):
                st.session_state.selected_price = p['price']
                st.session_state.selected_name = p['name']
    
    st.markdown("---")
    if 'selected_price' in st.session_state:
        st.success(f"คุณเลือก: **{st.session_state.selected_name}** ราคา **{st.session_state.selected_price} บาท**")
        method = st.radio("เลือกวิธีจ่ายเงิน", ["Cash", "QR_Code"], horizontal=True)
        
        if st.button("ยืนยันการซื้อ", type="primary", use_container_width=True):
            if save_transaction(st.session_state.selected_price, method):
                st.toast(f"ขอบคุณครับ! จ่าย {st.session_state.selected_name} เรียบร้อย")
                del st.session_state.selected_price
    else:
        st.write("เลือกรายการด้านบนเพื่อเริ่มสั่งซื้อ")

# --- TAB 2: ระบบจัดการหลังบ้าน ---
with tab2:
    if check_admin_login():
        col_title, col_logout = st.columns([4, 1])
        with col_title:
            st.title("📋 รายการการขายล่าสุด")
        with col_logout:
            if st.button("ออกจากระบบ"):
                st.session_state.admin_logged_in = False
                st.rerun()

        df = get_data()
        
        if not df.empty:
            m1, m2 = st.columns(2)
            m1.metric("รายได้ทั้งหมด", f"฿ {df['amount_paid'].sum():,.2f}")
            m2.metric("จำนวนรายการ", f"{len(df)} ออเดอร์")
            
            if st.button("🗑️ ล้างประวัติทั้งหมด", type="secondary"):
                st.session_state.confirm_delete = True
                
            if st.session_state.get('confirm_delete'):
                st.warning("⚠️ ยืนยันการลบประวัติถาวร?")
                c1, c2 = st.columns(2)
                if c1.button("ยืนยัน", type="primary"):
                    if clear_all_data():
                        st.session_state.confirm_delete = False
                        st.rerun()
                if c2.button("ยกเลิก"):
                    st.session_state.confirm_delete = False
                    st.rerun()

            df_display = df.copy()
            df_display.columns = ['วัน-เวลา (ไทย)', 'ยอดเงิน', 'วิธีจ่าย', 'สถานะ']
            st.dataframe(df_display, use_container_width=True, height=450)
        else:
            st.info("ไม่มีข้อมูลการขาย")

