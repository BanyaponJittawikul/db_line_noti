import requests
from requests import PreparedRequest
import mysql.connector



# ทำ line notify

def lineNotify(message):
    payload = {'message':message}
    return _lineNotify(payload)

def _lineNotify(payload,file=None):
    #import requests
    url = '' #ใช้ url ของ webhook
    token = "" #ใช้ token ที่ได้จาก webhook
    headers = {'Authorization':'Bearer '+token}
    return requests.post(url, headers=headers , data = payload, files=file)


#ทำ connect ไปที่ database

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="test"
)

cur = conn.cursor()

from datetime import datetime


thai_months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 
               'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']

def convert_to_thai_date(date_obj):
    """Convert date to 'day/month/year' format with Thai month names."""
    day = date_obj.day
    month = thai_months[date_obj.month - 1]  # เปลี่ยนเป็นเดือนไทย
    year = date_obj.year + 543  # เปลี่ยนเป็น พ.ศ.
    return f"{day} {month} {year}"


cur.execute("SELECT `meta_key`, `meta_value`, `post_id` FROM `wp_postmeta` WHERE `meta_key` IN ('po_no', 'due_date', 'po_status')")

result = cur.fetchall()

meta_data = {}


for row in result:
    meta_key, meta_value, post_id = row  
    
    if post_id not in meta_data:
        meta_data[post_id] = {}
    
    meta_data[post_id][meta_key] = meta_value  


today = datetime.today().date()


for post_id, data in meta_data.items():
    po_no = data.get('po_no')
    due_date_str = data.get('due_date')
    po_status = data.get('po_status')
    
    if po_no and due_date_str and po_status:  
        
        
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid due_date format for post_id {post_id}. Skipping.")
            continue

        
        if due_date <= today and po_status != 'ได้รับสินค้าแล้ว':
            
            thai_due_date = convert_to_thai_date(due_date)
            
            
            text = f"\nPO Number: {po_no}\nDue Date: {thai_due_date}\nPO Status: {po_status}\n"

            #ส่งข้อมูลไป line notify
            lineNotify(text)
        #else:
        #    print(f"Conditions not met for post_id {post_id}. No message sent.")
