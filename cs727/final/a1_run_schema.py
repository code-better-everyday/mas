from pathlib import Path

import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
}

schema_path = Path(__file__).with_name('schema.sql')

# Read the schema file
with schema_path.open('r', encoding='utf-8') as f:
    schema_sql = f.read()

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Split by the active delimiter so stored procedures/functions/triggers work.
statements = []
current = []
delimiter = ';'
for line in schema_sql.splitlines():
    stripped = line.strip()

    if not stripped or stripped.startswith('--'):
        continue

    if stripped.upper().startswith('DELIMITER '):
        delimiter = stripped.split(None, 1)[1]
        continue

    current.append(line)
    joined = '\n'.join(current).rstrip()
    if joined.endswith(delimiter):
        statements.append(joined[:-len(delimiter)].strip())
        current = []

# Add any remaining
if current:
    statements.append('\n'.join(current).rstrip(delimiter).strip())

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
