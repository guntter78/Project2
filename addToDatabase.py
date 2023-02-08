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
timeNow = datetime.datetime.now()
hourLater = timeNow
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

    if temp >= 75:
        msg = EmailMessage()
        msg.set_content("Humidity alarm!")
        msg['Subject'] = "The humidity on sensor {id} is equal or above 75%"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email)
    
    if timeNow == hourLater:
        cur.execute(f"INSERT INTO temp (sensor_id, temp) VALUES ({id}, {temp})")
        hourLater = timeNow + datetime.timedelta(hours=1)

    cur.execute(f"INSERT INTO humidity (sensor_id, humidity) VALUES ({id}, {hum})")
    print(f"{cur.rowcount}, details inserted")
    conn.commit()
    timeNow = datetime.datetime.now()
    #sleep(60)
