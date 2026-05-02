import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

# Drop if exists
print('Dropping existing trigger/proc/function if they exist...')
try:
    cur.execute('DROP TRIGGER IF EXISTS trg_CheckProfileLimit')
except Exception as e:
    print('  trigger drop:', e)
try:
    cur.execute('DROP PROCEDURE IF EXISTS sp_LogWatchProgress')
except Exception as e:
    print('  proc drop:', e)
try:
    cur.execute('DROP FUNCTION IF EXISTS fn_TotalWatchTimeHours')
except Exception as e:
    print('  func drop:', e)

# Create Trigger
trigger_sql = '''CREATE TRIGGER trg_CheckProfileLimit
BEFORE INSERT ON Profile
FOR EACH ROW
BEGIN
    DECLARE current_profiles INT DEFAULT 0;
    DECLARE max_allowed INT DEFAULT 0;

    SELECT COUNT(*) INTO current_profiles FROM Profile WHERE AccountID = NEW.AccountID;

    SELECT sp.MaxUsers INTO max_allowed
    FROM UserAccount ua
    JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
    WHERE ua.AccountID = NEW.AccountID
    LIMIT 1;

    IF current_profiles >= max_allowed THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maximum number of profiles reached for this subscription plan.';
    END IF;
END;'''

print('\n-- Creating trigger:')
print(trigger_sql)
try:
    cur.execute(trigger_sql)
    print('Trigger created')
except Exception as e:
    print('Trigger create error:', e)

# Create Procedure
proc_sql = '''CREATE PROCEDURE sp_LogWatchProgress(
    IN p_ProfileID INT,
    IN p_ContentID INT,
    IN p_Seconds INT,
    IN p_Rating INT
)
BEGIN
    INSERT INTO WatchHistory (ProfileID, ContentID, WatchDate, ProgressSeconds, Rating)
    VALUES (p_ProfileID, p_ContentID, NOW(), p_Seconds, p_Rating)
    ON DUPLICATE KEY UPDATE
        WatchDate = NOW(),
        ProgressSeconds = p_Seconds,
        Rating = IFNULL(p_Rating, Rating);
END;'''

print('\n-- Creating procedure:')
print(proc_sql)
try:
    cur.execute(proc_sql)
    print('Procedure created')
except Exception as e:
    print('Procedure create error:', e)

# Create Function
func_sql = '''CREATE FUNCTION fn_TotalWatchTimeHours(p_ProfileID INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE total_hours DECIMAL(10,2) DEFAULT 0.00;
    SELECT IFNULL(SUM(ProgressSeconds) / 3600, 0.00) INTO total_hours
    FROM WatchHistory
    WHERE ProfileID = p_ProfileID;
    RETURN total_hours;
END;'''

print('\n-- Creating function:')
print(func_sql)
try:
    cur.execute(func_sql)
    print('Function created')
except Exception as e:
    print('Function create error:', e)

conn.commit()

# Verify creation
print('\n== Routines now:')
cur.execute("SELECT ROUTINE_NAME, ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='NetflixDB'")
for r in cur.fetchall():
    print(r)

print('\n== Triggers now:')
cur.execute("SELECT TRIGGER_NAME, EVENT_MANIPULATION, ACTION_TIMING FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='NetflixDB'")
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
print('\nDone')
