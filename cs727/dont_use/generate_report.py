from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from datetime import datetime
import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB',
}

BASE_DIR = Path(__file__).resolve().parent
REPORT_PATH = BASE_DIR / 'assignment_report.md'
LOG_PATH = BASE_DIR / 'assignment_report.log'


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_one(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchone()


def fetch_all(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchall()


def add_section(lines, title):
    lines.append(f'## {title}')
    lines.append('')


def add_code_block(lines, text, language='sql'):
    lines.append(f'```{language}')
    lines.append(text.rstrip())
    lines.append('```')
    lines.append('')


def main():
    conn = connect_db()
    cur = conn.cursor()

    report: list[str] = []
    report.append('# NetflixDB Assignment Verification Report')
    report.append('')
    report.append(f'Generated: {datetime.now().isoformat(sep=" ", timespec="seconds")}')
    report.append('')
    report.append('This report is read-only. It documents what currently exists in `NetflixDB` and shows the SQL statements used to verify it.')
    report.append('')

    # Tables and counts
    add_section(report, '1. Table Counts')
    table_rows = fetch_all(
        cur,
        """
        SELECT TABLE_NAME
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = 'NetflixDB' AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """,
    )
    for (table_name,) in table_rows:
        count = fetch_one(cur, f'SELECT COUNT(*) FROM `{table_name}`')[0]
        status = 'OK' if count >= 15 else 'BELOW 15'
        report.append(f'- {table_name}: {count} rows ({status})')
    report.append('')
    add_code_block(
        report,
        dedent(
            """
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'NetflixDB' AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME;
            """
        ).strip(),
    )
    report.append('Output: table names and row counts listed above.')
    report.append('')

    # Create table definitions
    add_section(report, '2. CREATE TABLE Statements')
    for (table_name,) in table_rows:
        create_row = fetch_one(cur, f'SHOW CREATE TABLE `{table_name}`')
        create_sql = create_row[1]
        report.append(f'### {table_name}')
        add_code_block(report, create_sql)
    
    # Index verification
    add_section(report, '3. Indexes')
    index_rows = fetch_all(cur, 'SHOW INDEX FROM MediaContent')
    add_code_block(report, 'SHOW INDEX FROM MediaContent;')
    report.append('Output:')
    for row in index_rows:
        report.append(f'- Key_name={row[2]}, Column_name={row[4]}, Non_unique={row[1]}')
    report.append('')

    # View verification
    add_section(report, '4. View')
    view_row = fetch_one(cur, 'SHOW CREATE VIEW vw_HighlyRatedContent')
    add_code_block(report, 'SHOW CREATE VIEW vw_HighlyRatedContent;')
    report.append('Output:')
    report.append(view_row[1])
    report.append('')

    # Trigger verification
    add_section(report, '5. Trigger')
    trigger_row = fetch_one(cur, "SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA='NetflixDB' AND TRIGGER_NAME='trg_CheckProfileLimit'")
    if trigger_row:
        trigger_create = fetch_one(cur, 'SHOW CREATE TRIGGER trg_CheckProfileLimit')[2]
        add_code_block(report, 'SHOW CREATE TRIGGER trg_CheckProfileLimit;')
        report.append('Output:')
        report.append(trigger_create)
        report.append('')
    else:
        report.append('Trigger trg_CheckProfileLimit not found.')
        report.append('')

    # Routine verification
    add_section(report, '6. Stored Procedure and Function')
    routines = fetch_all(
        cur,
        """
        SELECT ROUTINE_NAME, ROUTINE_TYPE
        FROM information_schema.ROUTINES
        WHERE ROUTINE_SCHEMA='NetflixDB'
        ORDER BY ROUTINE_TYPE, ROUTINE_NAME
        """,
    )
    add_code_block(
        report,
        dedent(
            """
            SELECT ROUTINE_NAME, ROUTINE_TYPE
            FROM information_schema.ROUTINES
            WHERE ROUTINE_SCHEMA='NetflixDB'
            ORDER BY ROUTINE_TYPE, ROUTINE_NAME;
            """
        ).strip(),
    )
    report.append('Output:')
    for name, rtype in routines:
        report.append(f'- {rtype}: {name}')
    report.append('')
    if any(r[0] == 'sp_LogWatchProgress' and r[1] == 'PROCEDURE' for r in routines):
        proc_sql = fetch_one(cur, 'SHOW CREATE PROCEDURE sp_LogWatchProgress')[2]
        report.append('### sp_LogWatchProgress')
        add_code_block(report, 'SHOW CREATE PROCEDURE sp_LogWatchProgress;')
        report.append('Output:')
        report.append(proc_sql)
        report.append('')
    if any(r[0] == 'fn_TotalWatchTimeHours' and r[1] == 'FUNCTION' for r in routines):
        func_sql = fetch_one(cur, 'SHOW CREATE FUNCTION fn_TotalWatchTimeHours')[2]
        report.append('### fn_TotalWatchTimeHours')
        add_code_block(report, 'SHOW CREATE FUNCTION fn_TotalWatchTimeHours;')
        report.append('Output:')
        report.append(func_sql)
        report.append('')

    # Temporary table note
    add_section(report, '7. Temporary Table Requirement')
    report.append('Temporary tables are session-scoped and are not persisted in MySQL metadata, so they cannot be verified after the session ends.')
    report.append('If your assignment specifically requires a screenshot of a temporary table, use a one-off MySQL session and capture the result there.')
    report.append('')

    # Final requirement summary
    add_section(report, '8. Requirement Checklist')
    table_counts = {name: fetch_one(cur, f'SELECT COUNT(*) FROM `{name}`')[0] for (name,) in table_rows}
    all_tables_15 = all(count >= 15 for count in table_counts.values())
    has_index = any(row[2] == 'idx_media_title' for row in index_rows)
    has_view = view_row is not None
    has_trigger = trigger_row is not None
    has_proc = any(r[0] == 'sp_LogWatchProgress' and r[1] == 'PROCEDURE' for r in routines)
    has_func = any(r[0] == 'fn_TotalWatchTimeHours' and r[1] == 'FUNCTION' for r in routines)

    report.append(f'- At least 15 records per base table: {"Yes" if all_tables_15 else "No"}')
    report.append(f'- Index implemented: {"Yes" if has_index else "No"}')
    report.append(f'- View implemented: {"Yes" if has_view else "No"}')
    report.append(f'- Trigger implemented: {"Yes" if has_trigger else "No"}')
    report.append(f'- Stored procedure implemented: {"Yes" if has_proc else "No"}')
    report.append(f'- Function implemented: {"Yes" if has_func else "No"}')
    report.append('')

    text = '\n'.join(report)
    REPORT_PATH.write_text(text, encoding='utf-8')
    LOG_PATH.write_text(text, encoding='utf-8')
    print(text)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
