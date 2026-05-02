import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

print('\n== Tables and row counts ==')
cur.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='NetflixDB' ORDER BY TABLE_NAME")
tables = [r[0] for r in cur.fetchall()]
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
    cnt = cur.fetchone()[0]
    status = 'OK' if cnt >= 15 else 'MISSING (<15)'
    print(f"{t}: {cnt} rows -> {status}")

print('\n== Table CREATE statements (first 60 chars) ==')
for t in tables:
    cur.execute(f"SHOW CREATE TABLE `{t}`")
    row = cur.fetchone()
    if row:
        print(f"\n-- {t} --")
        print(row[1][:1000])

print('\n== Indexes for each table ==')
for t in tables:
    cur.execute(f"SHOW INDEX FROM `{t}`")
    rows = cur.fetchall()
    if rows:
        print(f"\nIndexes on {t}:")
        for r in rows:
            # Key_name is at index 2, Column_name at index 4
            print(f"  {r[2]} -> column: {r[4]} (non_unique={r[1]})")

print('\n== Views ==')
cur.execute("SELECT TABLE_NAME FROM information_schema.VIEWS WHERE TABLE_SCHEMA='NetflixDB'")
views = [r[0] for r in cur.fetchall()]
if views:
    for v in views:
        cur.execute(f"SHOW CREATE VIEW `{v}`")
        print(f"\nView {v}:")
        print(cur.fetchone()[1])
else:
    print('No views found')

print('\n== Triggers ==')
cur.execute("SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='NetflixDB'")
triggers = cur.fetchall()
if triggers:
    for tr in triggers:
        print(f"{tr[0]}: {tr[2]} {tr[1]}")
        try:
            cur.execute(f"SHOW CREATE TRIGGER `{tr[0]}`")
            print(cur.fetchone()[2])
        except Exception as e:
            print('  (cannot SHOW CREATE TRIGGER:', e, ')')
else:
    print('No triggers found')

print('\n== Stored routines (procedures/functions) ==')
cur.execute("SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='NetflixDB'")
routines = cur.fetchall()
if routines:
    for rn, rtype in routines:
        print(f"{rtype}: {rn}")
        try:
            if rtype == 'PROCEDURE':
                cur.execute(f"SHOW CREATE PROCEDURE `{rn}`")
                print(cur.fetchone()[2])
            else:
                cur.execute(f"SHOW CREATE FUNCTION `{rn}`")
                print(cur.fetchone()[2])
        except Exception as e:
            print('  (cannot SHOW CREATE for routine:', e, ')')
else:
    print('No routines found')

print('\n== Notes ==')
print('- This script is read-only: no CREATE/INSERT/ALTER/DROP operations executed')
print('- Temporary tables are session-scoped and not checked here')

cur.close()
conn.close()
print('\nDone')
