def handle_to_email(db, handle):
    return db.execute("SELECT email FROM user WHERE handle == ?", (handle,))