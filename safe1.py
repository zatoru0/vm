import psycopg2
from datetime import datetime

def record_transaction(machine_id, amount, volume, method):
    connection = None
    try:
        # 1. เชื่อมต่อกับ Database
        connection = psycopg2.connect(
            user="postgres",
            password="210443", # เปลี่ยนเป็นรหัสผ่านของคุณ
            host="localhost",
            port="5432",
            database="postgres"
        )
        cursor = connection.cursor()

        # 2. เตรียมคำสั่ง SQL สำหรับ Insert
        insert_query = """ 
        INSERT INTO transactions (machine_id, amount_paid, water_volume, payment_method, payment_status) 
        VALUES (%s, %s, %s, %s, %s) 
        """
        
        # ข้อมูลที่จะบันทึก (จำลองว่าจ่ายสำเร็จแล้ว)
        record_to_insert = (machine_id, amount, volume, method, 'Success')

        # 3. ประมวลผล
        cursor.execute(insert_query, record_to_insert)
        connection.commit() # ยืนยันการบันทึกข้อมูล
        
        print(f"✅ บันทึกรายการสำเร็จ: ตู้ {machine_id} ยอดเงิน {amount} บาท")

    except (Exception, psycopg2.Error) as error:
        print(f"❌ เกิดข้อผิดพลาด: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

# --- ทดลองเรียกใช้งาน (จำลองสถานะจากตู้) ---
# สมมติลูกค้าหยอดเหรียญ 10 บาท ได้น้ำ 6.5 ลิตร ที่ตู้ VM-001
record_transaction('VM-001', 10.00, 6.500, 'Cash')