import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'NetflixDB' ORDER BY TABLE_NAME")
tables = [r[0] for r in cur.fetchall()]

for table in tables:
    print('\n' + '='*60)
    print(f'Table: {table}')
    print('-'*60)
    cur.execute(f"SELECT * FROM `{table}` LIMIT 10")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    if not rows:
        print('(no rows)')
        continue
    # print header
    print(' | '.join(cols))
    for r in rows:
        print(' | '.join(str(x) if x is not None else 'NULL' for x in r))

cur.close()
conn.close()
print('\nDone')
