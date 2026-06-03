elif menu == "QR Scanner":

    st.subheader("📷 QR Attendance Scanner")

    qr_value = st.text_input(
        "Scanned QR Result",
        key="qr_result"
    )

    if qr_value:

        today = str(date.today())

        c.execute(
            """
            SELECT *
            FROM attendance
            WHERE roll_no=?
            AND att_date=?
            """,
            (qr_value, today)
        )

        existing = c.fetchone()

        if existing is None:

            c.execute(
                """
                INSERT INTO attendance
                (roll_no,att_date,status)
                VALUES(?,?,?)
                """,
                (
                    qr_value,
                    today,
                    "Present"
                )
            )

            conn.commit()

            st.success(
                f"✅ Present Marked : {qr_value}"
            )

        else:

            st.warning(
                f"⚠ Already Marked : {qr_value}"
            )

    components.html("""
    <script src="https://unpkg.com/html5-qrcode"></script>

    <div id="reader" style="width:350px;margin:auto;"></div>

    <script>
    function onScanSuccess(decodedText){

        const input =
        window.parent.document.querySelector(
        'input[aria-label="Scanned QR Result"]'
        );

        if(input){

            input.value = decodedText;

            input.dispatchEvent(
                new Event('input',{
                    bubbles:true
                })
            );
        }
    }

    let scanner =
    new Html5QrcodeScanner(
        "reader",
        {
            fps:10,
            qrbox:200
        }
    );

    scanner.render(onScanSuccess);
    </script>
    """, height=450)
