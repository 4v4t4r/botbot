def handle_to_email(conn, handle):
    db = conn.cursor()
    row = db.execute("SELECT email FROM user WHERE handle == ?", (handle,)).fetchone()
    if row:
        return row[0]
    else:
        return ""