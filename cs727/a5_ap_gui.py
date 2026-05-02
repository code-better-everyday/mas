import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Netflix Database Admin", page_icon="🎬", layout="wide")
st.title("🎬 Netflix Database Management System")

# --- DATABASE CONNECTION ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

@st.cache_resource
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def run_query(query, params=None, fetch=True):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True) # Returns rows as dictionaries for easy DataFrame conversion
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
            conn.commit()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")
        return None
    finally:
        cursor.close()

# --- UI LAYOUT: TABS ---
tab1, tab2 = st.tabs(["🔄 User Management (CRUD)", "📊 Advanced Analytics (Reports)"])

# ==========================================
# TAB 1: CRUD OPERATIONS
# ==========================================
with tab1:
    st.header("User Account Administration")
    
    col1, col2 = st.columns(2)
    
    # --- CREATE ---
    with col1:
        st.subheader("➕ Create New User")
        with st.form("create_user_form", clear_on_submit=True):
            new_email = st.text_input("Email Address")
            new_country = st.text_input("Country")
            new_password = st.text_input("Password", type="password")
            new_plan = st.selectbox("Select Plan", options=[1, 2, 3], format_func=lambda x: {1:"Basic", 2:"Standard", 3:"Premium"}[x])
            
            submit_create = st.form_submit_button("Create Account")
            if submit_create:
                sql = "INSERT INTO UserAccount (PlanID, Email, PasswordHash, JoinDate, Country) VALUES (%s, %s, %s, %s, %s)"
                run_query(sql, (new_plan, new_email, new_password, date.today(), new_country), fetch=False)
                st.success(f"User {new_email} successfully created!")

    # --- UPDATE & DELETE ---
    with col2:
        st.subheader("⚙️ Update or Delete User")
        
        # We fetch active users to populate the dropdowns
        users = run_query("SELECT AccountID, Email FROM UserAccount ORDER BY AccountID DESC")
        if users:
            user_dict = {u['AccountID']: f"ID: {u['AccountID']} - {u['Email']}" for u in users}
            
            with st.form("update_user_form"):
                update_id = st.selectbox("Select User to Update", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])
                update_plan = st.selectbox("Change to New Plan", options=[1, 2, 3], format_func=lambda x: {1:"Basic", 2:"Standard", 3:"Premium"}[x])
                submit_update = st.form_submit_button("Update Plan")
                if submit_update:
                    run_query("UPDATE UserAccount SET PlanID = %s WHERE AccountID = %s", (update_plan, update_id), fetch=False)
                    st.success(f"Account {update_id} updated successfully!")

            with st.form("delete_user_form"):
                delete_id = st.selectbox("Select User to Delete", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])
                submit_delete = st.form_submit_button("Delete Account")
                if submit_delete:
                    # Because of foreign keys, we must delete child profiles first
                    run_query("DELETE FROM Profile WHERE AccountID = %s", (delete_id,), fetch=False)
                    run_query("DELETE FROM UserAccount WHERE AccountID = %s", (delete_id,), fetch=False)
                    st.error(f"Account {delete_id} has been deleted.")
        else:
            st.info("No users found in the database.")

    # --- READ ---
    st.divider()
    st.subheader("📋 Current User Directory (Read)")
    if st.button("Refresh User List"):
        df_users = pd.DataFrame(run_query("SELECT AccountID, Email, Country, PlanID, JoinDate FROM UserAccount ORDER BY AccountID DESC LIMIT 10"))
        st.dataframe(df_users, use_container_width=True)


# ==========================================
# TAB 2: ADVANCED ANALYTICS (DELIVERABLE 5 REQUIREMENTS)
# ==========================================
with tab2:
    st.header("Advanced Business Intelligence")
    st.markdown("Execute complex SQL queries including SET operations, CTEs, OLAP, and comparisons.")
    
    report_type = st.selectbox(
        "Select a Report to Generate:",
        [
            "1. Multidimensional Revenue (OLAP ROLLUP & Advanced Aggregation)",
            "2. Genre Popularity Ranking (WITH clause & Window Functions)",
            "3. Premium Global Users (Set Membership 'IN')",
            "4. Content Duration Analysis (Set Comparison 'ALL')",
            "5. The Content Catalog (Set Operation 'UNION')"
        ]
    )

    if st.button("▶️ Run Selected Report", type="primary"):
        
        if "1." in report_type:
            st.subheader("OLAP ROLLUP: Subtotaled Revenue")
            st.code("SELECT Country, PlanName, SUM(MonthlyPrice) FROM UserAccount ... WITH ROLLUP", language="sql")
            sql = """
                SELECT 
                    IFNULL(ua.Country, 'GLOBAL TOTAL') AS Region,
                    IFNULL(sp.PlanName, 'ALL PLANS') AS PlanTier,
                    SUM(sp.MonthlyPrice) AS TotalRevenue,
                    COUNT(ua.AccountID) as TotalSubscribers
                FROM UserAccount ua
                JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
                GROUP BY ua.Country, sp.PlanName WITH ROLLUP;
            """
            st.dataframe(pd.DataFrame(run_query(sql)), use_container_width=True)

        elif "2." in report_type:
            st.subheader("CTE & Window Functions: Top Content by Genre")
            st.code("WITH RankedContent AS (SELECT ... DENSE_RANK() OVER(...) ) SELECT * FROM RankedContent", language="sql")
            sql = """
                WITH RankedContent AS (
                    SELECT 
                        g.GenreName,
                        m.Title,
                        ROUND(AVG(wh.Rating), 1) as AvgRating,
                        DENSE_RANK() OVER(PARTITION BY g.GenreName ORDER BY AVG(wh.Rating) DESC) as RankWithinGenre
                    FROM Genre g
                    JOIN ContentGenre cg ON g.GenreID = cg.GenreID
                    JOIN MediaContent m ON cg.ContentID = m.ContentID
                    JOIN WatchHistory wh ON m.ContentID = wh.ContentID
                    GROUP BY g.GenreName, m.Title
                )
                SELECT * FROM RankedContent WHERE RankWithinGenre <= 3;
            """
            st.dataframe(pd.DataFrame(run_query(sql)), use_container_width=True)

        elif "3." in report_type:
            st.subheader("Set Membership (IN): Premium Users in Top Markets")
            st.code("SELECT ... WHERE Country IN (SELECT Country ... HAVING COUNT > 1) AND PlanID = 3", language="sql")
            sql = """
                SELECT AccountID, Email, Country 
                FROM UserAccount 
                WHERE PlanID = 3 
                AND Country IN (
                    SELECT Country 
                    FROM UserAccount 
                    GROUP BY Country 
                    HAVING COUNT(AccountID) > 1
                );
            """
            st.dataframe(pd.DataFrame(run_query(sql)), use_container_width=True)

        elif "4." in report_type:
            st.subheader("Set Comparison (ALL): The Longest Movies")
            st.code("SELECT Title ... WHERE DurationSeconds > ALL (SELECT DurationSeconds FROM MediaContent WHERE ContentType = 'TV Show')", language="sql")
            sql = """
                SELECT Title, ContentType, DurationSeconds 
                FROM MediaContent 
                WHERE ContentType = 'Movie' 
                AND DurationSeconds > ALL (
                    SELECT DurationSeconds 
                    FROM MediaContent 
                    WHERE ContentType = 'TV Show'
                )
                ORDER BY DurationSeconds DESC;
            """
            st.dataframe(pd.DataFrame(run_query(sql)), use_container_width=True)

        elif "5." in report_type:
            st.subheader("Set Operation (UNION): Unified Content Catalog")
            st.code("SELECT Title, 'Cinematic' FROM MediaContent ... UNION SELECT Title, 'Episodic' ...", language="sql")
            sql = """
                SELECT Title, ReleaseYear, 'Cinematic Release' AS FormatType 
                FROM MediaContent 
                WHERE ContentType = 'Movie'
                UNION 
                SELECT Title, ReleaseYear, 'Episodic Series' AS FormatType 
                FROM MediaContent 
                WHERE ContentType = 'TV Show'
                ORDER BY ReleaseYear DESC
                LIMIT 15;
            """
            st.dataframe(pd.DataFrame(run_query(sql)), use_container_width=True)