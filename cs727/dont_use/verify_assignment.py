import mysql.connector
from faker import Faker
import random

fake = Faker()
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

def get_count(table):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]

def show_and_exec(sql, params=None, fetch=False):
    print('\n-- SQL:')
    print(sql)
    cur.execute(sql, params) if params else cur.execute(sql)
    if fetch:
        rows = cur.fetchall()
        print('\n-- Result:')
        for r in rows:
            print(r)
        return rows
    else:
        return None

print('\n== Row counts before adjustments ==')
tables = ['SubscriptionPlan','UserAccount','Profile','MediaContent','Genre','ContentGenre','WatchHistory']
counts = {}
for t in tables:
    counts[t] = get_count(t)
    print(f'{t}: {counts[t]}')

# Insert to reach 15 rows where needed
if counts['SubscriptionPlan'] < 15:
    to_add = 15 - counts['SubscriptionPlan']
    print(f"\nAdding {to_add} SubscriptionPlan rows to reach 15")
    for i in range(to_add):
        name = f"Plan_{fake.word()}_{i}"
        price = round(random.uniform(5,30),2)
        res = random.choice(['720p','1080p','4K'])
        maxu = random.randint(1,6)
        sql = "INSERT INTO SubscriptionPlan (PlanName, MonthlyPrice, Resolution, MaxUsers) VALUES (%s,%s,%s,%s)"
        print(sql, (name, price, res, maxu))
        cur.execute(sql, (name, price, res, maxu))
    conn.commit()

if counts['Genre'] < 15:
    to_add = 15 - counts['Genre']
    print(f"\nAdding {to_add} Genre rows to reach 15")
    for i in range(to_add):
        g = fake.word().title()[:50]
        sql = "INSERT INTO Genre (GenreName) VALUES (%s)"
        print(sql, (g,))
        try:
            cur.execute(sql, (g,))
        except mysql.connector.Error as e:
            print('  (ignored)', e)
    conn.commit()

# Ensure ContentGenre has at least 15 mappings
if counts['ContentGenre'] < 15:
    to_add = 15 - counts['ContentGenre']
    print(f"\nAdding {to_add} ContentGenre mappings to reach 15")
    # get existing ids
    cur.execute('SELECT ContentID FROM MediaContent')
    cids = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT GenreID FROM Genre')
    gids = [r[0] for r in cur.fetchall()]
    for _ in range(to_add):
        c = random.choice(cids)
        g = random.choice(gids)
        sql = 'INSERT IGNORE INTO ContentGenre (ContentID, GenreID) VALUES (%s,%s)'
        print(sql, (c,g))
        cur.execute(sql, (c,g))
    conn.commit()

print('\n== Row counts after adjustments ==')
for t in tables:
    cnt = get_count(t)
    print(f'{t}: {cnt}')

# Verify index on MediaContent
print('\n== Indexes on MediaContent ==')
show_and_exec('SHOW INDEX FROM MediaContent', fetch=True)

# Show view definition
print('\n== View definition vw_HighlyRatedContent ==')
show_and_exec("SHOW CREATE VIEW vw_HighlyRatedContent", fetch=True)

# Check triggers
print('\n== Triggers in NetflixDB ==')
show_and_exec("SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='NetflixDB'", fetch=True)

# Show procedures/functions
print('\n== Routines in NetflixDB ==')
show_and_exec("SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='NetflixDB'", fetch=True)

# If procedure exists, call it for a sample profile/content
cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='NetflixDB' AND ROUTINE_TYPE='PROCEDURE' AND ROUTINE_NAME='sp_LogWatchProgress'")
if cur.fetchone():
    print('\nCalling sp_LogWatchProgress for a sample profile/content...')
    cur.execute('SELECT ProfileID FROM Profile LIMIT 1')
    pid = cur.fetchone()[0]
    cur.execute('SELECT ContentID FROM MediaContent LIMIT 1')
    cid = cur.fetchone()[0]
    print('Sample IDs:', pid, cid)
    sql = "CALL sp_LogWatchProgress(%s, %s, %s, %s)"
    print(sql, (pid, cid, 120, 5))
    cur.execute(sql, (pid, cid, 120, 5))
    conn.commit()
    # show updated watchhistory row
    show_and_exec('SELECT * FROM WatchHistory WHERE ProfileID=%s AND ContentID=%s', (pid,cid), fetch=True)
else:
    print('\nProcedure sp_LogWatchProgress not found')

# If function exists, call it
cur.execute("SELECT ROUTINE_NAME FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='NetflixDB' AND ROUTINE_TYPE='FUNCTION' AND ROUTINE_NAME='fn_TotalWatchTimeHours'")
if cur.fetchone():
    cur.execute('SELECT ProfileID FROM Profile LIMIT 1')
    pid = cur.fetchone()[0]
    sql = 'SELECT fn_TotalWatchTimeHours(%s)'
    print('\nCalling function:', sql, (pid,))
    cur.execute(sql, (pid,))
    print('\n-- Result:', cur.fetchone()[0])
else:
    print('\nFunction fn_TotalWatchTimeHours not found')

# Create and display a temporary table (top watchers)
print('\n== Temporary table: top_watchers (session) ==')
cur.execute('CREATE TEMPORARY TABLE top_watchers AS SELECT ProfileID, COUNT(*) AS cnt FROM WatchHistory GROUP BY ProfileID ORDER BY cnt DESC LIMIT 10')
show_and_exec('SELECT * FROM top_watchers', fetch=True)

# Show index statements used earlier: we created idx_media_title in schema.sql
print('\n== Show index statements executed (manually echo) ==')
print('CREATE INDEX idx_media_title ON MediaContent(Title);')

# Show view statement
print('\n-- View statement used:')
print('CREATE VIEW vw_HighlyRatedContent AS SELECT m.Title, AVG(w.Rating) as AvgRating FROM MediaContent m JOIN WatchHistory w ON m.ContentID = w.ContentID GROUP BY m.Title HAVING AVG(w.Rating) >= 4.0;')

# Show trigger/procedure/function statements (echo)
print('\n-- Trigger statement used:')
print(open('schema.sql').read().split('\n')[60:90])

conn.commit()
cur.close()
conn.close()
print('\n== Verification complete ==')
