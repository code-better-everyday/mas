import mysql.connector
import sys

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
}

# Read the schema file
with open('schema.sql', 'r', encoding='utf-8') as f:
    schema_sql = f.read()

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Split by semicolon, but handle DELIMITER blocks
statements = []
current = ""
for line in schema_sql.split('\n'):
    if line.strip().startswith('--'):
        continue
    if 'DELIMITER //' in line or 'DELIMITER ;' in line:
        continue
    current += line + '\n'
    if line.rstrip().endswith(';'):
        stmt = current.rstrip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt[:-1].strip())  # Remove trailing semicolon
        current = ""

# Add any remaining
if current.strip():
    statements.append(current.rstrip(';').strip())

print(f"[*] Found {len(statements)} statements to execute")

# Execute each statement
for i, stmt in enumerate(statements):
    if not stmt:
        continue
    if stmt.startswith('--'):
        continue
    try:
        cursor.execute(stmt)
        if i % 5 == 0:
            print(f"[*] Executed {i+1}/{len(statements)} statements")
    except mysql.connector.Error as e:
        print(f"[!] Error on statement {i+1}: {e}")
        print(f"    Statement: {stmt[:100]}")

conn.commit()
cursor.close()

# Verify
cursor2 = conn.cursor()
cursor2.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'NetflixDB'")
count = cursor2.fetchone()[0]
print(f"\n[OK] NetflixDB has {count} tables")
cursor2.close()
conn.close()
