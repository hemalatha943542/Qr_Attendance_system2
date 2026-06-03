if menu == "QR Scanner":

    st.subheader("📷 QR Attendance Scanner")

    scan_roll = st.text_input(
        "Scanned QR Result"
    )

    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://unpkg.com/html5-qrcode"></script>
    </head>
    <body>

    <div id="reader" style="width:350px"></div>

    <script>

    function onScanSuccess(decodedText){

        const input =
        window.parent.document.querySelector('input');

        if(input){
            input.value = decodedText;
            input.dispatchEvent(
                new Event('input',{bubbles:true})
            );
        }
    }

    let scanner = new Html5QrcodeScanner(
        "reader",
        {
            fps:10,
            qrbox:{width:200,height:200}
        }
    );

    scanner.render(onScanSuccess);

    </script>

    </body>
    </html>
    """, height=450)
if scan_roll:

    today = str(date.today())

    c.execute("""
    SELECT *
    FROM attendance
    WHERE roll_no=?
    AND att_date=?
    """,
    (scan_roll, today))

    existing = c.fetchone()

    if existing:
        st.warning("Already Marked Today")
    else:
        c.execute("""
        INSERT INTO attendance
        (roll_no,att_date,status)
        VALUES(?,?,?)
        """,
        (scan_roll, today, "Present"))

        conn.commit()

        st.success(f"{scan_roll} Present")
    
