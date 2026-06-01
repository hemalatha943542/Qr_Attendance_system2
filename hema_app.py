import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
from datetime import date

# Database
conn = sqlite3.connect("attendance.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll_no TEXT UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    att_date TEXT,
    status TEXT
)
""")

conn.commit()

# QR Generator
def generate_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

st.set_page_config(page_title="QR Attendance", layout="wide")

st.title("📚 QR Attendance System")

menu = st.sidebar.radio(
    "Menu",
    ["Add Student", "Students", "Mark Attendance", "Report"]
)

# Add Student
if menu == "Add Student":

    st.subheader("➕ Add Student")

    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")

    if st.button("Save Student"):

        try:
            c.execute(
                "INSERT INTO students(name,roll_no) VALUES(?,?)",
                (name, roll)
            )
            conn.commit()

            st.success("Student Added Successfully")

        except:
            st.error("Roll Number Already Exists")

# Students List
elif menu == "Students":

    st.subheader("👨‍🎓 Students List")

    df = pd.read_sql(
        "SELECT * FROM students",
        conn
    )

    st.dataframe(df)

    if not df.empty:

        st.subheader("QR Codes")

        for _, row in df.iterrows():

            st.write(
                f"**{row['name']} - {row['roll_no']}**"
            )

            qr_img = generate_qr(row["roll_no"])

            st.image(qr_img, width=150)

# Mark Attendance
elif menu == "Mark Attendance":

    st.subheader("✅ Mark Attendance")

    roll = st.text_input(
        "Enter / Scan Roll Number"
    )

    if st.button("Mark Present"):

        today = str(date.today())

        c.execute("""
        SELECT * FROM attendance
        WHERE roll_no=? AND att_date=?
        """, (roll, today))

        existing = c.fetchone()

        if existing:

            st.warning(
                "Attendance Already Marked Today"
            )

        else:

            c.execute("""
            INSERT INTO attendance
            (roll_no,att_date,status)
            VALUES(?,?,?)
            """,
            (roll, today, "Present"))

            conn.commit()

            st.success(
                f"{roll} Marked Present"
            )

# Report
elif menu == "Report":

    st.subheader("📊 Attendance Report")

    report_date = st.date_input(
        "Select Date",
        date.today()
    )

    query = """
    SELECT *
    FROM attendance
    WHERE att_date=?
    """

    df = pd.read_sql(
        query,
        conn,
        params=(str(report_date),)
    )

    st.dataframe(df)

    csv = df.to_csv(index=False)

    st.download_button(
        "⬇ Download CSV",
        csv,
        "attendance.csv",
        "text/csv"
    )