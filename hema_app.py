import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
from datetime import date
import streamlit.components.v1 as components

st.set_page_config(
    page_title="QR Attendance System",
    layout="wide"
)

# ---------------- CSS ----------------

st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#87CEEB,#FFD1DC);
}

/* Sidebar */
section[data-testid="stSidebar"]{
background:#1f2937;
}

/* Sidebar text */
section[data-testid="stSidebar"] *{
color:white !important;
}

/* Radio menu labels */
.stRadio label{
color:white !important;
font-weight:bold;
}

/* Main headings */
h1,h2,h3{
color:#ffffff !important;
font-weight:bold;
}

/* Input labels */
label{
color:#ffffff !important;
font-weight:bold;
}

/* Text inputs */
.stTextInput input{
background:#232736;
color:white !important;
border-radius:10px;
}

/* Button */
.stButton button{
background:#1e90ff;
color:white;
border:none;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------

conn = sqlite3.connect(
    "attendance.db",
    check_same_thread=False
)

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

# ---------------- FUNCTIONS ----------------

def generate_qr(data):
    qr = qrcode.make(data)

    buf = BytesIO()

    qr.save(
        buf,
        format="PNG"
    )

    return buf.getvalue()

# ---------------- AUTO QR SCAN ATTENDANCE ----------------

scan_roll = st.query_params.get(
    "scan_roll",
    ""
)

if scan_roll:

    today = str(date.today())

    c.execute("""
    SELECT *
    FROM attendance
    WHERE roll_no=?
    AND att_date=?
    """,
    (
        scan_roll,
        today
    ))

    existing = c.fetchone()

    if not existing:

        c.execute("""
        INSERT INTO attendance
        (roll_no,att_date,status)
        VALUES(?,?,?)
        """,
        (
            scan_roll,
            today,
            "Present"
        ))

        conn.commit()

# ---------------- TITLE ----------------

st.title("📚 QR Attendance System")

# ---------------- MENU ----------------

menu = st.sidebar.radio(
    "Menu",
    [
        "Add Student",
        "Students",
        "QR Scanner",
        "Mark Attendance",
        "Report"
    ]
)

# ---------------- ADD STUDENT ----------------

if menu == "Add Student":

    st.subheader("➕ Add Student")

    name = st.text_input(
        "Student Name"
    )

    roll = st.text_input(
        "Roll Number"
    )

    if st.button(
        "Save Student"
    ):

        try:

            c.execute(
                """
                INSERT INTO students
                (name,roll_no)
                VALUES(?,?)
                """,
                (
                    name,
                    roll
                )
            )

            conn.commit()

            st.success(
                "Student Added Successfully"
            )

        except:

            st.error(
                "Roll Number Already Exists"
            )

# ---------------- STUDENTS ----------------

elif menu == "Students":

    st.subheader(
        "👨‍🎓 Students List"
    )

    df = pd.read_sql(
        "SELECT * FROM students",
        conn
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    if not df.empty:

        st.subheader(
            "📱 QR Codes"
        )

        for _, row in df.iterrows():

            st.markdown(
                f"### {row['name']} - {row['roll_no']}"
            )

            qr_img = generate_qr(
                row["roll_no"]
            )

            st.image(
                qr_img,
                width=200
            )

            st.download_button(
                "⬇ Download QR",
                qr_img,
                file_name=f"{row['roll_no']}.png",
                mime="image/png",
                key=row["roll_no"]
            )

# ---------------- QR SCANNER ----------------

elif menu == "QR Scanner":

    st.subheader("📷 QR Attendance Scanner")

    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://unpkg.com/html5-qrcode"></script>
    </head>
    <body>

    <div id="reader" style="width:100%;"></div>

    <script>

    function onScanSuccess(decodedText) {

        const currentUrl = window.parent.location.href.split("?")[0];

        window.parent.location.href =
        currentUrl + "?scan_roll=" +
        encodeURIComponent(decodedText);
    }

    let scanner = new Html5QrcodeScanner(
        "reader",
        {
            fps:10,
            qrbox:250
        }
    );

    scanner.render(onScanSuccess);

    </script>

    </body>
    </html>
    """, height=700)
# ---------------- MARK ATTENDANCE ----------------

elif menu == "Mark Attendance":

    st.subheader(
        "✅ Mark Attendance"
    )

    roll = st.text_input(
        "Enter Roll Number"
    )

    if st.button(
        "Mark Present"
    ):

        today = str(
            date.today()
        )

        c.execute("""
        SELECT *
        FROM attendance
        WHERE roll_no=?
        AND att_date=?
        """,
        (
            roll,
            today
        ))

        existing = c.fetchone()

        if existing:

            st.warning(
                "Already Marked Today"
            )

        else:

            c.execute("""
            INSERT INTO attendance
            (
            roll_no,
            att_date,
            status
            )
            VALUES(?,?,?)
            """,
            (
                roll,
                today,
                "Present"
            ))

            conn.commit()

            st.success(
                f"{roll} Present"
            )

# ---------------- REPORT ----------------

elif menu == "Report":

    st.subheader(
        "📊 Attendance Report"
    )

    report_date = st.date_input(
        "Select Date",
        date.today()
    )

    df = pd.read_sql(
        """
        SELECT *
        FROM attendance
        WHERE att_date=?
        """,
        conn,
        params=(
            str(report_date),
        )
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(
        index=False
    )

    st.download_button(
        "⬇ Download CSV",
        csv,
        "attendance.csv",
        "text/csv"
    )
