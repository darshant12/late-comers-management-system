import sqlite3

# Connect to your existing database
conn = sqlite3.connect('latecomers.db')
c = conn.cursor()

# # Delete all rows from the late_entries table
# c.execute("DELETE FROM late_entries")

# # Reset auto-increment counter so IDs start from 1 again
# c.execute("DELETE FROM sqlite_sequence WHERE name='late_entries'")

# conn.commit()
# conn.close()

# print("✅ All data deleted successfully! Database is now empty.")

c.execute("SELECT * FROM late_entries")
entries = c.fetchall()
print(entries)