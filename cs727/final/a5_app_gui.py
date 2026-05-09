import streamlit as st
import mysql.connector
import pandas as pd
from datetime import date


st.set_page_config(page_title="Netflix Database Admin", page_icon="🎬", layout="wide")

# ==========================================
# AUTHENTICATION GATE (LOGIN SCREEN)
# ==========================================

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False


if not st.session_state['authenticated']:
    st.markdown(
        "<h1 style='text-align: center;'>🔒 System Administrator Login - Netflix Database 🎬</h1>",
        unsafe_allow_html=True,
    )
    
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Please sign in")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if username == "admin" and password == "pass@123":
                    st.session_state['authenticated'] = True
                    st.rerun() # Refresh the page to load the main app!
                else:
                    st.error("⚠️ Invalid username or password.")
    
    # st.stop() prevents any code below this line from running until authenticated
    st.stop() 

# ==========================================
# MAIN APPLICATION (Only visible if authenticated)
# ==========================================
st.title("🎬 Netflix Database Management System")

# Add a logout button to the sidebar
if st.sidebar.button("Logout 🚪"):
    st.session_state['authenticated'] = False
    st.rerun()

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
    
    
    try:
        # Ping the server. If it's dead, reconnect=True automatically spins up a new connection.
        conn.ping(reconnect=True, attempts=3, delay=1)
    except mysql.connector.Error as err:
        st.error(f"⚠️ Critical Database Connection Error: {err}")
        return None
    # ---------------------------------------------------
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return True
    except mysql.connector.Error as err:
        st.error(f"SQL Error: {err}")
        return None
    finally:
        cursor.close()

# --- UI LAYOUT: TABS ---
st.markdown(
    """
    <style>
    div[data-baseweb="tab-list"] button {
        font-size: 1.5rem;
        font-weight: 1200;
        padding: 0.6rem 1rem;
    }
    div[data-baseweb="tab-list"] button p {
        font-size: 1.5rem;
        font-weight: 1200;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
tab1, tab2 = st.tabs(["**User Management (CRUD)**", "**Advanced Analytics Dashboard**"])

# ==========================================
# TAB 1: CRUD OPERATIONS
# ==========================================
with tab1:
    # st.subheader("User Account Administration")
    
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
                # NEW LOGIC: Check the database to see if the email already exists
                check_email = run_query("SELECT Email FROM UserAccount WHERE Email = %s", (new_email,))
                
                if check_email:
                    # If the query found a match, stop and show a red error
                    st.error(f"⚠️ Creation failed: The email '{new_email}' is already in use!")
                else:
                    # If it's a brand new email, proceed with creating the account
                    sql = "INSERT INTO UserAccount (PlanID, Email, PasswordHash, JoinDate, Country) VALUES (%s, %s, %s, %s, %s)"
                    run_query(sql, (new_plan, new_email, new_password, date.today(), new_country), fetch=False)
                    st.success(f"✅ User {new_email} successfully created!")

    # --- UPDATE & DELETE ---
    with col2:
        st.subheader("⚙️ Update or Delete User")
        
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
# TAB 2: ADVANCED ANALYTICS REPORTS
# ==========================================
with tab2:
    st.header("Advanced Business Intelligence")
    st.markdown("Generate complex queries for gaining insights into user behavior, content performance, and revenue trends. Select a report from the dropdown and click 'Generate Report' to see the results.")
    
    # Dictionary containing all 18 queries 
    report_library = {
        "1. Core BI: Monthly Recurring Revenue (MRR)": """
            SELECT sp.PlanName, 
                   COUNT(ua.AccountID) AS TotalSubscribers, 
                   SUM(sp.MonthlyPrice) AS TotalMonthlyRevenue 
            FROM SubscriptionPlan sp 
            LEFT JOIN UserAccount ua ON sp.PlanID = ua.PlanID 
            GROUP BY sp.PlanName 
            ORDER BY TotalMonthlyRevenue DESC;
        """,
        "2. Core BI: Platform Content Composition": """
            SELECT ContentType, 
                   COUNT(ContentID) AS TotalTitles, 
                   ROUND(AVG(DurationSeconds)/60, 2) AS AvgDurationMinutes 
            FROM MediaContent 
            GROUP BY ContentType;
        """,
        "3. Core BI: Account Utilization Rate": """
            SELECT ua.Email, 
                   sp.PlanName, 
                   sp.MaxUsers, 
                   COUNT(p.ProfileID) AS CurrentProfiles, 
                   (sp.MaxUsers - COUNT(p.ProfileID)) AS AvailableSlots 
            FROM UserAccount ua 
            JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID 
            LEFT JOIN Profile p ON ua.AccountID = p.AccountID 
            GROUP BY ua.AccountID, ua.Email, sp.PlanName, sp.MaxUsers 
            HAVING AvailableSlots > 0;
        """,
        "4. Core BI: Most Popular Genres": """
            SELECT g.GenreName, 
                   COUNT(cg.ContentID) AS NumberOfTitles 
            FROM Genre g 
            JOIN ContentGenre cg ON g.GenreID = cg.GenreID 
            GROUP BY g.GenreName 
            ORDER BY NumberOfTitles DESC 
            LIMIT 5;
        """,
        "5. Core BI: Global User Distribution": """
            SELECT Country, 
                   COUNT(AccountID) AS TotalAccounts 
            FROM UserAccount 
            GROUP BY Country 
            ORDER BY TotalAccounts DESC;
        """,
        "6. Subqueries: The Churn Risk Report": """
            SELECT ua.Email, 
                   p.ProfileName, 
                   MAX(wh.WatchDate) AS LastWatchedDate 
            FROM UserAccount ua 
            JOIN Profile p ON ua.AccountID = p.AccountID 
            LEFT JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID 
            GROUP BY ua.Email, p.ProfileName 
            HAVING LastWatchedDate < DATE_SUB(NOW(), INTERVAL 6 MONTH) 
                OR LastWatchedDate IS NULL;
        """,
        "7. Subqueries: The 'Never Watched' List": """
            SELECT m.Title, 
                   m.ReleaseYear, 
                   m.ContentType 
            FROM MediaContent m 
            LEFT JOIN WatchHistory wh ON m.ContentID = wh.ContentID 
            WHERE wh.HistoryID IS NULL;
        """,
        "8. Aggregation: Top 3 Highest Rated Content": """
            SELECT m.Title, 
                   ROUND(AVG(wh.Rating), 1) AS AverageRating, 
                   COUNT(wh.Rating) AS TotalReviews 
            FROM MediaContent m 
            JOIN WatchHistory wh ON m.ContentID = wh.ContentID 
            GROUP BY m.Title 
            HAVING TotalReviews >= 2 
            ORDER BY AverageRating DESC 
            LIMIT 3;
        """,
        "9. Multi-Join: Cross-Profile Genre Preferences": """
            SELECT p.ProfileName, 
                   COUNT(wh.HistoryID) AS TitlesWatched 
            FROM Profile p 
            JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID 
            JOIN ContentGenre cg ON wh.ContentID = cg.ContentID 
            JOIN Genre g ON cg.GenreID = g.GenreID 
            WHERE g.GenreName = 'Action' 
            GROUP BY p.ProfileName 
            ORDER BY TitlesWatched DESC;
        """,
        "10. Aggregation: Binge Viewer Identification": """
            SELECT p.ProfileName, 
                   COUNT(DISTINCT wh.ContentID) AS UniqueTitlesWatched 
            FROM Profile p 
            JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID 
            GROUP BY p.ProfileName 
            HAVING UniqueTitlesWatched > 5 
            ORDER BY UniqueTitlesWatched DESC;
        """,
        "11. OLAP ROLLUP: Multidimensional Revenue Analysis": """
            SELECT IFNULL(ua.Country, 'GLOBAL TOTAL') AS Region, 
                   IFNULL(sp.PlanName, 'ALL PLANS') AS PlanTier, 
                   SUM(sp.MonthlyPrice) AS TotalRevenue 
            FROM UserAccount ua 
            JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID 
            GROUP BY ua.Country, sp.PlanName WITH ROLLUP;
        """,
        "12. Window Function: Running Total of Signups": """
            SELECT JoinDate, 
                   Email, 
                   COUNT(AccountID) OVER (ORDER BY JoinDate ASC) AS CumulativeUsers 
            FROM UserAccount 
            ORDER BY JoinDate ASC;
        """,
        "13. Window Function (CTE): DENSE_RANK() by Genre": """
            WITH RankedContent AS (
                SELECT g.GenreName, 
                       m.Title, 
                       AVG(wh.Rating) as AvgRating, 
                       DENSE_RANK() OVER(PARTITION BY g.GenreName ORDER BY AVG(wh.Rating) DESC) as RatingRank 
                FROM Genre g 
                JOIN ContentGenre cg ON g.GenreID = cg.GenreID 
                JOIN MediaContent m ON cg.ContentID = m.ContentID 
                JOIN WatchHistory wh ON m.ContentID = wh.ContentID 
                GROUP BY g.GenreName, m.Title
            ) 
            SELECT * FROM RankedContent 
            WHERE RatingRank <= 3;
        """,
        "14. Window Function (CTE): User Engagement Quartiles": """
            WITH UserWatchTime AS (
                SELECT ProfileID, 
                       SUM(ProgressSeconds) as TotalSeconds 
                FROM WatchHistory 
                GROUP BY ProfileID
            ) 
            SELECT p.ProfileName, 
                   uwt.TotalSeconds, 
                   NTILE(4) OVER(ORDER BY uwt.TotalSeconds DESC) as EngagementQuartile 
            FROM Profile p 
            JOIN UserWatchTime uwt ON p.ProfileID = uwt.ProfileID;
        """,
        "15. Window Function (CTE): Time-to-First-Watch": """
            WITH FirstWatch AS (
                SELECT p.AccountID, 
                       MIN(wh.WatchDate) as FirstStreamDate 
                FROM Profile p 
                JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID 
                GROUP BY p.AccountID
            ) 
            SELECT ua.Email, 
                   ua.JoinDate, 
                   fw.FirstStreamDate, 
                   DATEDIFF(fw.FirstStreamDate, ua.JoinDate) AS DaysToFirstStream 
            FROM UserAccount ua 
            JOIN FirstWatch fw ON ua.AccountID = fw.AccountID 
            WHERE DATEDIFF(fw.FirstStreamDate, ua.JoinDate) >= 0 
            ORDER BY DaysToFirstStream DESC;
        """,
        "16. Advanced CTE: Top 3 Premium Markets & Users": """
            WITH TopPremiumCountries AS (
                SELECT Country, 
                       COUNT(AccountID) AS TotalPremiumUsers 
                FROM UserAccount 
                WHERE PlanID = 3 
                GROUP BY Country 
                HAVING COUNT(AccountID) > 1 
                ORDER BY TotalPremiumUsers DESC 
                LIMIT 3
            ) 
            SELECT tpc.Country, 
                   tpc.TotalPremiumUsers, 
                   ua.AccountID, 
                   ua.Email 
            FROM UserAccount ua 
            JOIN TopPremiumCountries tpc ON ua.Country = tpc.Country 
            WHERE ua.PlanID = 3 
            ORDER BY tpc.TotalPremiumUsers DESC, tpc.Country, ua.Email;
        """,
        "17. Set Comparison (ALL): The Longest Movies": """
            SELECT Title, 
                   ContentType, 
                   DurationSeconds 
            FROM MediaContent 
            WHERE ContentType = 'Movie' 
              AND DurationSeconds > ALL (
                  SELECT DurationSeconds 
                  FROM MediaContent 
                  WHERE ContentType = 'TV Show'
              ) 
            ORDER BY DurationSeconds DESC;
        """,
        "18. Set Operation (UNION): Unified Content Catalog": """
            SELECT Title, 
                   ReleaseYear, 
                   'Cinematic Release' AS FormatType 
            FROM MediaContent 
            WHERE ContentType = 'Movie' 
            UNION 
            SELECT Title, 
                   ReleaseYear, 
                   'Episodic Series' AS FormatType 
            FROM MediaContent 
            WHERE ContentType = 'TV Show' 
            ORDER BY ReleaseYear DESC 
            LIMIT 15;
        """
    }

    # Dictionary containing the business descriptions for the UI
    report_descriptions = {
        "1. Core BI: Monthly Recurring Revenue (MRR)": "Calculates total monthly recurring revenue generated by each active subscription plan to guide pricing strategy.",
        "2. Core BI: Platform Content Composition": "Evaluates the balance of the media catalog by counting Movies vs. TV Shows and calculating their average durations.",
        "3. Core BI: Account Utilization Rate": "Identifies accounts with unused profile slots compared to their plan's maximum allowed users, targeting upsell opportunities.",
        "4. Core BI: Most Popular Genres": "Determines the platform's top 5 most heavily stocked genres to balance catalog diversity.",
        "5. Core BI: Global User Distribution": "Groups user accounts by registered country to highlight the largest international markets.",
        "6. Subqueries: The Churn Risk Report": "Identifies inactive users who haven't watched anything in the last 6 months to target for re-engagement campaigns.",
        "7. Subqueries: The 'Never Watched' List": "Finds catalog 'dead weight' content that has zero entries in the watch history table.",
        "8. Aggregation: Top 3 Highest Rated Content": "Calculates the highest-rated content pieces (with at least two reviews) to feed the recommendation engine.",
        "9. Multi-Join: Cross-Profile Genre Preferences": "Navigates four tables to identify exactly how many specific Genre titles specific profiles have watched.",
        "10. Aggregation: Binge Viewer Identification": "Identifies highly engaged 'binge' viewers who have watched more than 5 unique titles.",
        "11. OLAP ROLLUP: Multidimensional Revenue Analysis": "Dynamically calculates revenue subtotaled by Plan Tier and automatically rolls it up into a Grand Global Total.",
        "12. Window Function: Running Total of Signups": "Calculates the cumulative running total of user accounts created over time to measure platform growth.",
        "13. Window Function (CTE): DENSE_RANK() by Genre": "Dynamically ranks content within its specific genre to find the Top 3 titles per category.",
        "14. Window Function (CTE): User Engagement Quartiles": "Sorts and buckets users into four statistical quartiles based on their total lifetime watch duration.",
        "15. Window Function (CTE): Time-to-First-Watch": "Calculates the exact gap in days between a user's initial signup and their first stream to measure onboarding success.",
        "16. Advanced CTE: Top 3 Premium Markets & Users": "Uses a Common Table Expression to dynamically isolate the 3 countries with the highest concentration of Premium users, then joins back to list the specific accounts within those regions.",
        "17. Set Comparison (ALL): The Longest Movies": "Finds movies that are strictly longer in duration than every single TV show on the platform.",
        "18. Set Operation (UNION): Unified Content Catalog": "Combines Movies and TV Shows into a single, unified list and appends custom format labels to each row."
    }

    # Dropdown to select the query
    selected_report = st.selectbox("Select a Report to Generate:", list(report_library.keys()))

    
    selected_genre = None
    
    # If the user selects Report 9, show a SINGLE select dropdown
    if "9." in selected_report:
        all_genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Documentary', 
                      'Romance', 'Thriller', 'Animation', 'Fantasy', 'Crime', 'Mystery', 
                      'Family', 'Reality TV']
        
        selected_genre = st.selectbox(
            "🎛️ Select a Genre to Analyze:",
            options=all_genres,
            index=0 # Defaults to 'Action'
        )

    if st.button("▶️ Generate Report", type="primary", key="generate_btn"):
        sql_query = report_library[selected_report]
        business_description = report_descriptions[selected_report]
        
        # --- DYNAMIC SQL REPLACEMENT ---
        if "9." in selected_report:
            # Replace the hardcoded 'Action' with the selected single genre
            sql_query = sql_query.replace("'Action'", f"'{selected_genre}'")
        # ------------------------------------

        # Display the descriptive text in a nice callout box
        st.info(f"**Business Objective:** {business_description}")
        
        # Display the dynamically updated SQL code being executed
        st.subheader("SQL Execution String")
        st.code(sql_query, language="sql")
        
        # Run and display the data
        st.subheader("Query Results")
        data = run_query(sql_query)
        
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("Query executed successfully, but returned 0 rows.")