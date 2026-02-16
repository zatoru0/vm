# -*- coding: utf-8 -*-
import psycopg2
import random
import time

def simulate_vending(n_times):
    connection = None
    try:
        # เชื่อมต่อ (ตรวจสอบรหัสผ่านและชื่อ DB ให้ถูกต้อง)
        connection = psycopg2.connect(
            user="postgres", 
            password="210443", 
            host="localhost", 
            database="postgres" # ใช้ postgres ตามที่เช็คใน pgAdmin ล่าสุด
        )
        cursor = connection.cursor()
        
        methods = ['Cash', 'QR_Code']
        print(f"เริ่มการจำลองการขาย {n_times} รายการ...")

        for i in range(n_times):
            amount = random.choice([5, 10, 15, 20])
            volume = round(amount * 0.66, 2)
            method = random.choice(methods)
            
            query = """INSERT INTO transactions (machine_id, amount_paid, water_volume, payment_method, payment_status) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, ('VM-001', amount, volume, method, 'Success'))
            
            print(f"รายการที่ {i+1}: ตู้ VM-001 ขายได้ {amount} บาท ({method})")
            time.sleep(1) # รอ 1 วินาทีต่อรายการ

        connection.commit()
        print("✅ จำลองเสร็จสมบูรณ์!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# เริ่มจำลอง 10 รายการ
simulate_vending(10)