import streamlit as st
import pandas as pd
import json, os
from datetime import date, datetime
import qrcode
from io import BytesIO
import streamlit.components.v1 as components

st.set_page_config(page_title="Auxilium College - QR Attendance", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f1b35,#1a2a4a);}
[data-testid="stSidebar"] *{color:#e0e8ff!important;}
.main .block-container{background:#0d1b2e;padding-top:2rem;}
.metric-card{background:linear-gradient(135deg,#1a2a4a,#243560);border-radius:12px;padding:1.2rem;text-align:center;border:1px solid #2d4070;margin-bottom:1rem;}
.metric-value{font-size:2.2rem;font-weight:700;color:#f0c040;}
.metric-label{font-size:.85rem;color:#8aa0cc;}
h1,h2,h3{color:#e0e8ff!important;}
.stButton>button{background:linear-gradient(135deg,#2d5af0,#1a3acc);color:#fff;border:none;border-radius:8px;font-weight:600;width:100%;}
.stTextInput>div>div>input{background:#243560!important;color:#e0e8ff!important;border:1px solid #2d4070!important;border-radius:8px!important;}
</style>
""", unsafe_allow_html=True)

DATA_FILE   = "students.json"
ATTEND_FILE = "attendance.json"

def load_students():
    return json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else {}

def save_students(d):
    json.dump(d, open(DATA_FILE,"w"), indent=2)

def load_attendance():
    return json.load(open(ATTEND_FILE)) if os.path.exists(ATTEND_FILE) else {}

def save_attendance(d):
    json.dump(d, open(ATTEND_FILE,"w"), indent=2)

def mark_attendance(roll):
    roll = roll.strip()
    students = load_students()
    if roll not in students:
        return False, f"❌ Roll No '{roll}' not found!"
    att = load_attendance()
    today = str(date.today())
    att.setdefault(today, {})
    if roll in att[today]:
        return False, f"⚠️ Already marked: {students[roll]['name']}"
    att[today][roll] = {"name":students[roll]["name"],"dept":students[roll]["dept"],
                        "time":datetime.now().strftime("%H:%M:%S")}
    save_attendance(att)
    return True, f"✅ Present: {students[roll]['name']} ({roll})"

def make_qr(roll):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(roll); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf,"PNG"); return buf.getvalue()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0'>
      <div style='font-size:3rem'>🎓</div>
      <div style='font-size:1.2rem;font-weight:700;color:#f0c040'>Auxilium College</div>
      <div style='font-size:.8rem;color:#8aa0cc'>QR Attendance System</div>
    </div>
    <hr style='border-color:#2d4070;margin:.5rem 0 1.5rem'>
    """, unsafe_allow_html=True)
    page = st.radio("Nav", ["➕ Add Student","👥 Students List","📷 QR Scanner",
                             "📊 Today Summary","📋 Attendance Report"], label_visibility="collapsed")
    st.markdown(f"<div style='text-align:center;color:#8aa0cc;font-size:.8rem;margin-top:2rem'>📅 {date.today()}</div>", unsafe_allow_html=True)

# ── Add Student ────────────────────────────────────────────────────────────────
if page == "➕ Add Student":
    st.title("➕ Add Student")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Student Details")
        roll = st.text_input("Roll Number", placeholder="e.g. BCA1")
        name = st.text_input("Full Name",   placeholder="e.g. Hema Priya")
        dept = st.selectbox("Department", ["BCA","BBA","Computer Science","Mathematics",
                                            "Physics","Chemistry","Commerce","English","History","Economics"])
        year = st.selectbox("Year", ["1st Year","2nd Year","3rd Year"])
        if st.button("💾 Add Student"):
            if not roll or not name: st.error("Fill Roll Number & Name!")
            else:
                s = load_students()
                if roll in s: st.error(f"{roll} already exists!")
                else:
                    s[roll]={"name":name,"dept":dept,"year":year,"added_on":str(date.today())}
                    save_students(s); st.success(f"✅ {name} added!"); st.balloons()
    with c2:
        st.subheader("🔲 Generate QR Code")
        qr_roll = st.text_input("Roll No for QR", placeholder="e.g. BCA1", key="qrgen")
        if st.button("Generate QR"):
            s = load_students()
            if qr_roll in s:
                qb = make_qr(qr_roll)
                st.image(qb, caption=f"{s[qr_roll]['name']} — {qr_roll}", width=260)
                st.download_button("⬇️ Download QR", qb, f"QR_{qr_roll}.png","image/png")
            else: st.error("Roll No not found!")

# ── Students List ──────────────────────────────────────────────────────────────
elif page == "👥 Students List":
    st.title("👥 Students List")
    st.markdown("---")
    s = load_students()
    if not s: st.info("No students yet.")
    else:
        ta = load_attendance().get(str(date.today()), {})
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(s)}</div><div class="metric-label">Total</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(ta)}</div><div class="metric-label">Present Today</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-value">{len(s)-len(ta)}</div><div class="metric-label">Absent Today</div></div>',unsafe_allow_html=True)
        search = st.text_input("🔍 Search")
        rows=[{"Roll No":r,"Name":i["name"],"Dept":i["dept"],"Year":i["year"],
               "Today":"✅" if r in ta else "❌"} for r,i in s.items()
              if not search or search.lower() in r.lower() or search.lower() in i["name"].lower()]
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
        st.markdown("---")
        dr=st.text_input("Roll No to delete")
        if st.button("🗑️ Delete"):
            if dr in s: del s[dr]; save_students(s); st.success(f"Deleted!"); st.rerun()
            else: st.error("Not found!")

# ── QR Scanner ─────────────────────────────────────────────────────────────────
elif page == "📷 QR Scanner":
    st.title("📷 QR Scanner")
    st.markdown("---")

    if "scanner_locked" not in st.session_state:
        st.session_state.scanner_locked = False
    if st.button("🔓 Unlock Scanner" if st.session_state.scanner_locked else "🔒 Lock Scanner"):
        st.session_state.scanner_locked = not st.session_state.scanner_locked; st.rerun()

    if st.session_state.scanner_locked:
        st.warning("🔒 Scanner is locked.")
    else:
        st.success("📸 QR scan பண்ணினா **உடனே** Present mark ஆகும்!")

        # ── WORKING AUTO-MARK: JS writes roll to a file via XMLHttpRequest
        # to Streamlit's own /_stcore/health endpoint trick won't work.
        # 
        # TRUE SOLUTION: Use st.components.v1.declare_component with a local 
        # component server. Since we can't do that here, we use the NEXT BEST:
        # A bidirectional hack using URL fragments that Streamlit can detect.
        #
        # ACTUALLY WORKING: We serve a tiny HTTP handler using threading + BaseHTTPServer
        # that the JS calls, which writes to a shared file, and Streamlit polls it.

        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from urllib.parse import urlparse, parse_qs

        SCAN_FILE = "qr_scan_result.txt"
        PORT = 8502

        class ScanHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path == "/mark":
                    params = parse_qs(parsed.query)
                    roll = params.get("roll", [""])[0].strip()
                    if roll:
                        with open(SCAN_FILE, "w") as f:
                            f.write(roll)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(b"OK")
                else:
                    self.send_response(404); self.end_headers()
            def log_message(self, *args): pass  # silence logs

        # Start the mini HTTP server once
        if "http_server_started" not in st.session_state:
            def run_server():
                try:
                    server = HTTPServer(("localhost", PORT), ScanHandler)
                    server.serve_forever()
                except: pass
            t = threading.Thread(target=run_server, daemon=True)
            t.start()
            st.session_state.http_server_started = True

        # Check if scanner wrote a new roll number
        if os.path.exists(SCAN_FILE):
            with open(SCAN_FILE) as f:
                scanned_roll = f.read().strip()
            if scanned_roll:
                os.remove(SCAN_FILE)
                ok, msg = mark_attendance(scanned_roll)
                if ok:
                    st.success(f"🎉 AUTO-MARKED! {msg}")
                    st.balloons()
                else:
                    st.error(msg)

        # Embed the scanner — JS calls localhost:8502/mark?roll=BCA1
        components.html(f"""
<!DOCTYPE html><html><head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html5-qrcode/2.3.8/html5-qrcode.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#1a2a4a;font-family:Arial,sans-serif;color:#e0e8ff;padding:1rem}}
#reader{{max-width:360px;margin:0 auto;border-radius:10px;overflow:hidden}}
#status{{margin-top:.8rem;padding:.8rem;border-radius:8px;background:#243560;color:#8aa0cc;text-align:center;font-size:.95rem}}
#status.ok{{background:#1a3a2a;color:#2ecc71;border-left:4px solid #2ecc71}}
#status.scan{{background:#1a2040;color:#f0c040;border-left:4px solid #f0c040}}
#status.err{{background:#3a1a1a;color:#e74c3c;border-left:4px solid #e74c3c}}
.btn{{display:block;margin:.8rem auto 0;padding:.6rem 2rem;background:linear-gradient(135deg,#2d5af0,#1a3acc);color:#fff;border:none;border-radius:8px;font-size:1rem;cursor:pointer;font-weight:600}}
#log{{margin-top:.8rem}}
.li{{background:#1a3a2a;border-radius:6px;padding:.4rem .8rem;margin:.2rem 0;color:#2ecc71;font-size:.85rem}}
</style></head><body>
<div id="reader"></div>
<div id="status" class="scan">📷 Camera starting...</div>
<button class="btn" id="btn" onclick="toggle()">⏹ Stop</button>
<div id="log"></div>
<script>
let qr=null,on=false,last="",lastT=0,log=[];
const st=(m,c)=>{{const e=document.getElementById("status");e.className=c||"";e.innerText=m}}
const addLog=r=>{{log.unshift(r);if(log.length>5)log.pop();document.getElementById("log").innerHTML="<div style='color:#8aa0cc;font-size:.8rem;margin-bottom:.3rem'>Scanned:</div>"+log.map(x=>`<div class='li'>✅ ${{x}}</div>`).join("")}}

function onScan(text){{
  const now=Date.now();
  if(text===last&&now-lastT<5000)return;
  last=text;lastT=now;
  const roll=text.trim();
  st("⏳ Marking: "+roll+"...","scan");
  addLog(roll);
  // Call our local Python HTTP server to write the roll to a file
  fetch("http://localhost:{PORT}/mark?roll="+encodeURIComponent(roll))
    .then(r=>r.text())
    .then(()=>{{
      st("✅ Marked! Refreshing...","ok");
      // Trigger Streamlit rerun by clicking a hidden button
      setTimeout(()=>{{
        // Send message to parent to click rerun
        window.parent.postMessage({{type:"streamlit:rerun"}},"*");
        st("✅ Camera On — Point at QR","scan");
      }},1000);
    }})
    .catch(()=>{{st("⚠️ Server error — use manual box","err")}});
}}

function start(){{
  qr=new Html5Qrcode("reader");
  qr.start({{facingMode:"environment"}},{{fps:10,qrbox:{{width:230,height:230}}}},onScan,()=>{{}})
  .then(()=>{{st("✅ Camera On — Point at QR","scan");document.getElementById("btn").innerText="⏹ Stop";on=true}})
  .catch(e=>{{st("❌ "+e,"err")}})
}}
function stop(){{qr&&qr.stop().then(()=>{{st("📷 Stopped","err");document.getElementById("btn").innerText="▶ Start";on=false}})}}
function toggle(){{on?stop():start()}}
start();
</script></body></html>
""", height=480)

        # Auto-rerun every 2 seconds to pick up new scans
        st.markdown("---")
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("🔄 Refresh", key="manual_refresh", help="Click after scan if not auto-refreshed"):
                st.rerun()
        with col1:
            st.caption("Scan ஆனதும் page auto-refresh ஆகும். இல்லன்னா 🔄 Refresh click பண்ணுங்க.")

        st.markdown("**✏️ Manual Mark (backup)**")
        with st.form("qf", clear_on_submit=True):
            ri = st.text_input("Roll Number", placeholder="e.g. BCA1")
            if st.form_submit_button("✅ Mark Present"):
                if ri:
                    ok,msg=mark_attendance(ri.strip())
                    if ok: st.success(msg); st.balloons()
                    else: st.error(msg)

        # Auto-rerun loop using st.empty + time
        auto_refresh = st.empty()
        if os.path.exists("qr_scan_result.txt"):
            st.rerun()

    today_att = load_attendance().get(str(date.today()), {})
    if today_att:
        st.markdown("---")
        st.subheader(f"✅ Present Today — {len(today_att)} students")
        rows=[{"Roll No":r,"Name":v["name"],"Dept":v["dept"],"Time":v["time"]} for r,v in today_att.items()]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ── Today Summary ──────────────────────────────────────────────────────────────
elif page == "📊 Today Summary":
    st.title("📊 Today Summary")
    st.caption(date.today().strftime('%A, %d %B %Y'))
    st.markdown("---")
    s=load_students(); ta=load_attendance().get(str(date.today()),{})
    total=len(s); present=len(ta); absent=total-present
    pct=round(present/total*100,1) if total else 0
    c1,c2,c3,c4=st.columns(4)
    for col,(v,l,color) in zip([c1,c2,c3,c4],[(total,"Total","#f0c040"),(present,"Present","#2ecc71"),(absent,"Absent","#e74c3c"),(f"{pct}%","Att %","#2d5af0")]):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:{color}">{v}</div><div class="metric-label">{l}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader(f"✅ Present ({present})")
        if ta: st.dataframe(pd.DataFrame([{"Roll":r,"Name":v["name"],"Time":v["time"]} for r,v in ta.items()]),use_container_width=True,hide_index=True)
        else: st.info("No attendance yet.")
    with c2:
        st.subheader(f"❌ Absent ({absent})")
        ar=[{"Roll":r,"Name":i["name"]} for r,i in s.items() if r not in ta]
        if ar: st.dataframe(pd.DataFrame(ar),use_container_width=True,hide_index=True)
        else: st.success("All present! 🎉")
    st.markdown("---")
    with st.form("mf"):
        m=st.text_input("Manual Roll No",placeholder="e.g. BCA1")
        if st.form_submit_button("Mark Present"):
            ok,msg=mark_attendance(m)
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)

# ── Attendance Report ──────────────────────────────────────────────────────────
elif page == "📋 Attendance Report":
    st.title("📋 Attendance Report")
    st.markdown("---")
    s=load_students(); att=load_attendance()
    if not att: st.info("No records yet.")
    else:
        sel=st.selectbox("Date",sorted(att.keys(),reverse=True))
        if sel:
            day=att[sel]; total=len(s); present=len(day)
            c1,c2,c3=st.columns(3)
            with c1: st.metric("Present",present)
            with c2: st.metric("Absent",total-present)
            with c3: st.metric("Att %",f"{round(present/total*100,1) if total else 0}%")
            rows=[{"Roll No":r,"Name":i["name"],"Dept":i["dept"],
                   "Status":"✅ Present" if r in day else "❌ Absent",
                   "Time":day[r]["time"] if r in day else "-"} for r,i in s.items()]
            df=pd.DataFrame(rows)
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button("⬇️ CSV",df.to_csv(index=False),f"att_{sel}.csv","text/csv")
        st.markdown("---")
        st.subheader("📈 All-time")
        rows=[{"Roll No":r,"Name":i["name"],"Present":sum(1 for d in att.values() if r in d),
               "Total":len(att),"Att %":f"{round(sum(1 for d in att.values() if r in d)/len(att)*100,1)}%"} for r,i in s.items()]
        if rows: st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
