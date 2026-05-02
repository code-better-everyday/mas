import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'NetflixDB'")
tables = cursor.fetchall()

print("\n[*] Tables in NetflixDB:")
for table in tables:
    print(f"  - {table[0]}")

# Show detailed structure for each table
print("\n[*] Table Structures:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    print(f"\n  {table_name}:")
    for col in columns:
        col_name, col_type, nullable, key, default, extra = col
        print(f"    - {col_name}: {col_type} {f'(KEY: {key})' if key else ''}")

# Show row counts
print(f"\n[*] Row Counts:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count} rows")

cursor.close()
conn.close()
print("\nDone!")
