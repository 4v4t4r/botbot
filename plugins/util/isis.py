def handle_to_email(conn, handle):
    db = conn.cursor()
    return db.execute("SELECT email FROM user WHERE handle == ?", (handle,))