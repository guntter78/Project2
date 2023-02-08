import serial
import struct
import datetime
import pymysql
import smtplib
import ssl
from email.message import EmailMessage
from time import sleep

#setup variables
ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)

# Database connection + default queries
conn = pymysql.connect(host="localhost", user="smilexdbadmin1", password="gras123!", database="smilex")
cur = conn.cursor()

#email vars
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "smilexzend@gmail.com"  # Enter your address
receiver_email = "smilexadm@gmail.com"  # Enter receiver address
password = "tmlibvculqlzfodz"

while True:
    raw_data = ser.read(12) # Assume the size of the struct is 12 bytes
    my_data = bytes(raw_data)
    my_data_struct = struct.unpack('<3i', my_data)

    id = my_data_struct[0]
    temp = my_data_struct[1]
    hum = my_data_struct[2]
    print(f"ID:{id}\nTemp: {temp}\nHum: {hum}")

    cur.execute(f"select * from temp where sensor_id = {id} order by created_at desc limit 1")
    hourPast = cur.fetchall()[0][3]

    if hum >= 75:
        msg = EmailMessage()
        msg.set_content("Remember, remember, the humidity on the sensor. \nPercentage, too high and wet. I see no reason\nWhy humidity season\nShould ever be upset.")
        msg['Subject'] = f"The humidity on sensor {id} is equal or above 75%"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email)
    
    timeNow = datetime.datetime.now()
    if timeNow.strftime("%H") > hourPast.strftime("%H"):
        cur.execute(f"INSERT INTO temp (sensor_id, temp) VALUES ({id}, {temp})")


    cur.execute(f"INSERT INTO humidity (sensor_id, humidity) VALUES ({id}, {hum})")
    print(f"{cur.rowcount}, details inserted")
    conn.commit()
    #sleep(60)
