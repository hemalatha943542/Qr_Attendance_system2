import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime
import qrcode
from io import BytesIO
import base64

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Auxilium College - QR Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1b35 0%, #1a2a4a 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e0e8ff !important;
    }

    /* Main background */
    .main .block-container {
        background: #0d1b2e;
        padding-top: 2rem;
    }

    /* Cards */
    .card {
        background: #1a2a4a;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #2d4070;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a2a4a, #243560);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #2d4070;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #f0c040;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #8aa0cc;
        margin-top: 0.2rem;
    }

    /* Success/Error banners */
    .success-banner {
        background: #1a3a2a;
        border-left: 4px solid #2ecc71;
        border-radius: 8px;
        padding: 1rem;
        color: #2ecc71;
        margin: 1rem 0;
    }

    .error-banner {
        background: #3a1a1a;
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        padding: 1rem;
        color: #e74c3c;
        margin: 1rem 0;
    }

    /* Page title */
    h1, h2, h3 {
        color: #e0e8ff !important;
    }

    /* Streamlit elements override */
    .stButton > button {
        background: linear-gradient(135deg, #2d5af0, #1a3acc);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #3d6aff, #2a4adc);
        transform: translateY(-1px);
    }

    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: #243560 !important;
        color: #e0e8ff !important;
        border: 1px solid #2d4070 !important;
        border-radius: 8px !important;
    }

    .stDataFrame {
        background: #1a2a4a;
        border-radius: 8px;
    }

    /* Scanner area */
    .scanner-container {
        background: #1a2a4a;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        border: 2px dashed #2d5af0;
    }

    .scanner-status {
        background: #243560;
        border-radius: 8px;
        padding: 0.8rem;
        color: #8aa0cc;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Data Helpers ──────────────────────────────────────────────────────────────
DATA_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"

def load_students():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_students(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_attendance(data):
    with open(ATTENDANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def mark_attendance(roll_no):
    students = load_students()
    if roll_no not in students:
        return False, f"Roll No {roll_no} not found!"
    attendance = load_attendance()
    today = str(date.today())
    if today not in attendance:
        attendance[today] = {}
    if roll_no in attendance[today]:
        return False, f"Already marked Present for {students[roll_no]['name']}!"
    attendance[today][roll_no] = {
        "name": students[roll_no]["name"],
        "dept": students[roll_no]["dept"],
        "time": datetime.now().strftime("%H:%M:%S")
    }
    save_attendance(attendance)
    return True, f"✅ Present marked for {students[roll_no]['name']}!"

def generate_qr(roll_no):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(roll_no)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:3rem;'>🎓</div>
        <div style='font-size:1.2rem; font-weight:700; color:#f0c040;'>Auxilium College</div>
        <div style='font-size:0.8rem; color:#8aa0cc; margin-top:0.3rem;'>QR Attendance System</div>
    </div>
    <hr style='border-color:#2d4070; margin: 0.5rem 0 1.5rem;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["➕ Add Student", "👥 Students List", "📷 QR Scanner", "📊 Today Summary", "📋 Attendance Report"],
        label_visibility="collapsed"
    )

    st.markdown(f"""
    <div style='position:absolute; bottom:2rem; left:0; right:0; text-align:center;'>
        <div style='font-size:0.8rem; color:#8aa0cc;'>📅 Today: {date.today()}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Pages ─────────────────────────────────────────────────────────────────────

# ── 1. Add Student ─────────────────────────────────────────────────────────────
if page == "➕ Add Student":
    st.title("➕ Add Student")
    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Student Details")

        roll_no = st.text_input("Roll Number", placeholder="e.g. 2024CS001")
        name = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        dept = st.selectbox("Department", [
            "Computer Science", "Mathematics", "Physics",
            "Chemistry", "Commerce", "English Literature",
            "History", "Economics", "BCA", "BBA"
        ])
        year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year"])

        if st.button("💾 Add Student"):
            if not roll_no or not name:
                st.error("Please fill Roll Number and Name!")
            else:
                students = load_students()
                if roll_no in students:
                    st.error(f"Roll No {roll_no} already exists!")
                else:
                    students[roll_no] = {
                        "name": name,
                        "dept": dept,
                        "year": year,
                        "added_on": str(date.today())
                    }
                    save_students(students)
                    st.success(f"✅ {name} added successfully!")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Generate QR Code")
        st.info("After adding a student, generate their QR code here.")

        qr_roll = st.text_input("Enter Roll No for QR", placeholder="e.g. 2024CS001", key="qr_gen")
        if st.button("🔲 Generate QR"):
            students = load_students()
            if qr_roll in students:
                qr_bytes = generate_qr(qr_roll)
                st.image(qr_bytes, caption=f"QR for {students[qr_roll]['name']} ({qr_roll})", width=250)
                st.download_button(
                    "⬇️ Download QR",
                    data=qr_bytes,
                    file_name=f"QR_{qr_roll}.png",
                    mime="image/png"
                )
            else:
                st.error("Roll No not found! Please add the student first.")
        st.markdown('</div>', unsafe_allow_html=True)

# ── 2. Students List ───────────────────────────────────────────────────────────
elif page == "👥 Students List":
    st.title("👥 Students List")
    st.markdown("---")

    students = load_students()

    if not students:
        st.info("No students added yet. Go to **Add Student** to get started.")
    else:
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(students)}</div><div class="metric-label">Total Students</div></div>', unsafe_allow_html=True)
        with col2:
            depts = set(v["dept"] for v in students.values())
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(depts)}</div><div class="metric-label">Departments</div></div>', unsafe_allow_html=True)
        with col3:
            today_attendance = load_attendance().get(str(date.today()), {})
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(today_attendance)}</div><div class="metric-label">Present Today</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Search / Filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search by name or roll no", placeholder="Type to search...")
        with col2:
            dept_filter = st.selectbox("Filter by Department", ["All"] + sorted(list(depts)))

        # Build dataframe
        rows = []
        for roll, info in students.items():
            if search and search.lower() not in roll.lower() and search.lower() not in info["name"].lower():
                continue
            if dept_filter != "All" and info["dept"] != dept_filter:
                continue
            present_today = "✅ Present" if roll in today_attendance else "❌ Absent"
            rows.append({
                "Roll No": roll,
                "Name": info["name"],
                "Department": info["dept"],
                "Year": info["year"],
                "Today": present_today,
                "Added On": info.get("added_on", "N/A")
            })

        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Delete student option
            st.markdown("---")
            del_roll = st.text_input("Enter Roll No to delete student", placeholder="e.g. 2024CS001")
            if st.button("🗑️ Delete Student", type="secondary"):
                if del_roll in students:
                    del students[del_roll]
                    save_students(students)
                    st.success(f"Deleted {del_roll} successfully!")
                    st.rerun()
                else:
                    st.error("Roll No not found!")
        else:
            st.info("No students match your search.")

# ── 3. QR Scanner ─────────────────────────────────────────────────────────────
elif page == "📷 QR Scanner":
    st.title("📷 QR Scanner")
    st.markdown("---")

    st.info("📸 QR code scan பண்ணினா automatically Present mark ஆகும்!")

    # Lock/Unlock scanner
    if "scanner_locked" not in st.session_state:
        st.session_state.scanner_locked = False

    col_lock, _ = st.columns([1, 3])
    with col_lock:
        lock_label = "🔓 Unlock Scanner" if st.session_state.scanner_locked else "🔒 Lock Scanner"
        if st.button(lock_label):
            st.session_state.scanner_locked = not st.session_state.scanner_locked
            st.rerun()

    if st.session_state.scanner_locked:
        st.warning("🔒 Scanner is locked. Click Unlock to enable.")
    else:
        # ── The Fixed QR Scanner Component ──────────────────────────────────────
        # Uses postMessage instead of window.top.location.href (fixes the error)
        scanner_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #1a2a4a; font-family: 'Inter', sans-serif; color: #e0e8ff; }
  #container { padding: 1rem; text-align: center; }
  #reader { width: 100%; max-width: 400px; margin: 0 auto; border-radius: 12px; overflow: hidden; }
  #status {
    margin-top: 1rem;
    padding: 0.8rem 1rem;
    border-radius: 8px;
    background: #243560;
    font-size: 0.95rem;
    color: #8aa0cc;
  }
  #status.success { background: #1a3a2a; color: #2ecc71; border-left: 3px solid #2ecc71; }
  #status.error   { background: #3a1a1a; color: #e74c3c; border-left: 3px solid #e74c3c; }
  #status.info    { background: #1a2a4a; color: #f0c040; border-left: 3px solid #f0c040; }
  #toggle-btn {
    margin-top: 1rem;
    padding: 0.6rem 2rem;
    background: linear-gradient(135deg, #2d5af0, #1a3acc);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    font-weight: 600;
  }
</style>
</head>
<body>
<div id="container">
  <div id="reader"></div>
  <div id="status">📷 Camera starting...</div>
  <button id="toggle-btn" onclick="toggleCamera()">⏹ Stop Camera</button>
</div>

<script>
let html5QrCode = null;
let scanning = true;
let lastScanned = "";
let lastTime = 0;

function onScanSuccess(decodedText) {
  const now = Date.now();
  // Debounce: skip same QR within 3 seconds
  if (decodedText === lastScanned && now - lastTime < 3000) return;
  lastScanned = decodedText;
  lastTime = now;

  document.getElementById("status").className = "info";
  document.getElementById("status").innerText = "⏳ Processing: " + decodedText;

  // ✅ FIX: Use postMessage instead of window.top.location.href
  window.parent.postMessage({
    type: "qr_scanned",
    roll: decodedText.trim()
  }, "*");
}

function onScanError(err) {
  // Silent — camera scan errors are normal
}

function startScanner() {
  html5QrCode = new Html5Qrcode("reader");
  html5QrCode.start(
    { facingMode: "environment" },
    { fps: 10, qrbox: { width: 250, height: 250 } },
    onScanSuccess,
    onScanError
  ).then(() => {
    document.getElementById("status").className = "";
    document.getElementById("status").innerText = "✅ Camera On — Point at a QR Code";
    document.getElementById("toggle-btn").innerText = "⏹ Stop Camera";
    scanning = true;
  }).catch(err => {
    document.getElementById("status").className = "error";
    document.getElementById("status").innerText = "❌ Camera error: " + err;
  });
}

function stopScanner() {
  if (html5QrCode) {
    html5QrCode.stop().then(() => {
      document.getElementById("status").className = "error";
      document.getElementById("status").innerText = "📷 Camera stopped.";
      document.getElementById("toggle-btn").innerText = "▶ Start Camera";
      scanning = false;
    });
  }
}

function toggleCamera() {
  if (scanning) stopScanner();
  else startScanner();
}

// Listen for result confirmation from parent Streamlit
window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "attendance_result") {
    const el = document.getElementById("status");
    if (event.data.success) {
      el.className = "success";
      el.innerText = "✅ " + event.data.message;
    } else {
      el.className = "error";
      el.innerText = "❌ " + event.data.message;
    }
    // Reset after 3 seconds
    setTimeout(() => {
      el.className = "";
      el.innerText = "✅ Camera On — Point at a QR Code";
    }, 3000);
  }
});

// Auto-start
startScanner();
</script>
</body>
</html>
"""
        import streamlit.components.v1 as components

        # Receive the postMessage via Streamlit component communication
        # We embed the scanner and use a form below to handle manual entry as fallback
        components.html(scanner_html, height=500)

        st.markdown("---")
        st.subheader("📨 Scan Result Handler")
        st.caption("The scanner sends the QR data here automatically. You can also enter manually below.")

        # ── Manual / Auto Mark Attendance ─────────────────────────────────────
        col1, col2 = st.columns([3, 1])
        with col1:
            roll_input = st.text_input(
                "Roll Number (auto-filled from scan or type manually)",
                key="manual_roll",
                placeholder="e.g. 2024CS001"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            mark_btn = st.button("✅ Mark Present", use_container_width=True)

        if mark_btn:
            if roll_input:
                ok, msg = mark_attendance(roll_input.strip())
                if ok:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a Roll Number.")

        # ── Today's attendance so far ──────────────────────────────────────────
        today_att = load_attendance().get(str(date.today()), {})
        if today_att:
            st.markdown("---")
            st.subheader(f"✅ Present Today ({len(today_att)} students)")
            rows = [{"Roll No": r, "Name": v["name"], "Dept": v["dept"], "Time": v["time"]}
                    for r, v in today_att.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── 4. Today Summary ──────────────────────────────────────────────────────────
elif page == "📊 Today Summary":
    st.title("📊 Today Summary")
    st.markdown(f"**Date:** {date.today().strftime('%A, %d %B %Y')}")
    st.markdown("---")

    students = load_students()
    attendance = load_attendance()
    today_str = str(date.today())
    today_att = attendance.get(today_str, {})

    total = len(students)
    present = len(today_att)
    absent = total - present
    pct = round((present / total * 100), 1) if total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    metrics = [
        (total, "Total Students", "#f0c040"),
        (present, "Present", "#2ecc71"),
        (absent, "Absent", "#e74c3c"),
        (f"{pct}%", "Attendance %", "#2d5af0"),
    ]
    for col, (val, label, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Present list
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"✅ Present ({present})")
        if today_att:
            rows = [{"Roll No": r, "Name": v["name"], "Dept": v["dept"], "Time": v["time"]}
                    for r, v in today_att.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No attendance marked yet today.")

    with col2:
        st.subheader(f"❌ Absent ({absent})")
        absent_rows = []
        for roll, info in students.items():
            if roll not in today_att:
                absent_rows.append({"Roll No": roll, "Name": info["name"], "Dept": info["dept"]})
        if absent_rows:
            st.dataframe(pd.DataFrame(absent_rows), use_container_width=True, hide_index=True)
        else:
            st.success("All students are present! 🎉")

    # Manual mark from summary page
    st.markdown("---")
    st.subheader("✏️ Manual Mark Attendance")
    col1, col2 = st.columns([3, 1])
    with col1:
        m_roll = st.text_input("Roll Number", placeholder="e.g. 2024CS001", key="summary_roll")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Mark Present", key="summary_mark"):
            ok, msg = mark_attendance(m_roll.strip())
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# ── 5. Attendance Report ───────────────────────────────────────────────────────
elif page == "📋 Attendance Report":
    st.title("📋 Attendance Report")
    st.markdown("---")

    students = load_students()
    attendance = load_attendance()

    if not attendance:
        st.info("No attendance records yet.")
    else:
        # Date selector
        dates = sorted(attendance.keys(), reverse=True)
        selected_date = st.selectbox("Select Date", dates)

        if selected_date:
            day_att = attendance[selected_date]
            total = len(students)
            present = len(day_att)
            absent = total - present

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Present", present)
            with col2:
                st.metric("Absent", absent)
            with col3:
                pct = round(present / total * 100, 1) if total > 0 else 0
                st.metric("Attendance %", f"{pct}%")

            st.markdown("---")

            # Full table for that day
            rows = []
            for roll, info in students.items():
                att_info = day_att.get(roll)
                rows.append({
                    "Roll No": roll,
                    "Name": info["name"],
                    "Department": info["dept"],
                    "Status": "✅ Present" if att_info else "❌ Absent",
                    "Time": att_info["time"] if att_info else "-"
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download as CSV",
                data=csv,
                file_name=f"attendance_{selected_date}.csv",
                mime="text/csv"
            )

        # Overall summary across all dates
        st.markdown("---")
        st.subheader("📈 All-time Attendance Summary")
        summary_rows = []
        for roll, info in students.items():
            present_days = sum(1 for d in attendance.values() if roll in d)
            total_days = len(attendance)
            pct = round(present_days / total_days * 100, 1) if total_days > 0 else 0
            summary_rows.append({
                "Roll No": roll,
                "Name": info["name"],
                "Department": info["dept"],
                "Days Present": present_days,
                "Total Days": total_days,
                "Attendance %": f"{pct}%"
            })
        if summary_rows:
            summary_df = pd.DataFrame(summary_rows)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
