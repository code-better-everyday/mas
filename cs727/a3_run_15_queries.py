import mysql.connector
import pandas as pd

# Database Connection Configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

# The 15 Deliverable Queries
queries = [
    {
        "title": "1. Monthly Recurring Revenue (MRR) by Subscription Tier",
        "sql": """
            SELECT 
                sp.PlanName, 
                COUNT(ua.AccountID) AS TotalSubscribers,
                SUM(sp.MonthlyPrice) AS TotalMonthlyRevenue
            FROM SubscriptionPlan sp
            LEFT JOIN UserAccount ua ON sp.PlanID = ua.PlanID
            GROUP BY sp.PlanName
            ORDER BY TotalMonthlyRevenue DESC;
        """
    },
    {
        "title": "2. Platform Content Composition",
        "sql": """
            SELECT 
                ContentType, 
                COUNT(ContentID) AS TotalTitles,
                ROUND(AVG(DurationSeconds)/60, 2) AS AvgDurationMinutes
            FROM MediaContent
            GROUP BY ContentType;
        """
    },
    {
        "title": "3. Account Utilization Rate",
        "sql": """
            SELECT 
                ua.Email, 
                sp.PlanName, 
                sp.MaxUsers, 
                COUNT(p.ProfileID) AS CurrentProfiles,
                (sp.MaxUsers - COUNT(p.ProfileID)) AS AvailableSlots
            FROM UserAccount ua
            JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
            LEFT JOIN Profile p ON ua.AccountID = p.AccountID
            GROUP BY ua.AccountID, ua.Email, sp.PlanName, sp.MaxUsers
            HAVING AvailableSlots > 0;
        """
    },
    {
        "title": "4. Most Popular Genres by Content Volume",
        "sql": """
            SELECT 
                g.GenreName, 
                COUNT(cg.ContentID) AS NumberOfTitles
            FROM Genre g
            JOIN ContentGenre cg ON g.GenreID = cg.GenreID
            GROUP BY g.GenreName
            ORDER BY NumberOfTitles DESC
            LIMIT 5;
        """
    },
    {
        "title": "5. Global User Distribution",
        "sql": """
            SELECT 
                Country, 
                COUNT(AccountID) AS TotalAccounts
            FROM UserAccount
            GROUP BY Country
            ORDER BY TotalAccounts DESC;
        """
    },
    {
        "title": "6. The Churn Risk Report (Inactive Users)",
        "sql": """
            SELECT 
                ua.Email, 
                p.ProfileName, 
                MAX(wh.WatchDate) AS LastWatchedDate
            FROM UserAccount ua
            JOIN Profile p ON ua.AccountID = p.AccountID
            LEFT JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID
            GROUP BY ua.Email, p.ProfileName
            HAVING LastWatchedDate < DATE_SUB(NOW(), INTERVAL 6 MONTH) OR LastWatchedDate IS NULL;
        """
    },
    {
        "title": "7. The 'Never Watched' Content List",
        "sql": """
            SELECT 
                m.Title, 
                m.ReleaseYear, 
                m.ContentType
            FROM MediaContent m
            LEFT JOIN WatchHistory wh ON m.ContentID = wh.ContentID
            WHERE wh.HistoryID IS NULL;
        """
    },
    {
        "title": "8. Top 3 Highest Rated Content Pieces",
        "sql": """
            SELECT 
                m.Title, 
                ROUND(AVG(wh.Rating), 1) AS AverageRating,
                COUNT(wh.Rating) AS TotalReviews
            FROM MediaContent m
            JOIN WatchHistory wh ON m.ContentID = wh.ContentID
            GROUP BY m.Title
            HAVING TotalReviews >= 2
            ORDER BY AverageRating DESC
            LIMIT 3;
        """
    },
    {
        "title": "9. Cross-Profile Genre Preferences",
        "sql": """
            SELECT 
                p.ProfileName, 
                COUNT(wh.HistoryID) AS ActionTitlesWatched
            FROM Profile p
            JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID
            JOIN ContentGenre cg ON wh.ContentID = cg.ContentID
            JOIN Genre g ON cg.GenreID = g.GenreID
            WHERE g.GenreName = 'Action'
            GROUP BY p.ProfileName
            ORDER BY ActionTitlesWatched DESC;
        """
    },
    {
        "title": "10. Binge Viewer Identification",
        "sql": """
            SELECT 
                p.ProfileName, 
                COUNT(DISTINCT wh.ContentID) AS UniqueTitlesWatched
            FROM Profile p
            JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID
            GROUP BY p.ProfileName
            HAVING UniqueTitlesWatched > 5
            ORDER BY UniqueTitlesWatched DESC;
        """
    },
    {
        "title": "11. OLAP ROLLUP: Multidimensional Revenue Analysis",
        "sql": """
            SELECT 
                IFNULL(ua.Country, 'GLOBAL TOTAL') AS Region,
                IFNULL(sp.PlanName, 'ALL PLANS') AS PlanTier,
                SUM(sp.MonthlyPrice) AS TotalRevenue
            FROM UserAccount ua
            JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
            GROUP BY ua.Country, sp.PlanName WITH ROLLUP;
        """
    },
    {
        "title": "12. Window Function: Running Total of Platform Signups",
        "sql": """
            SELECT 
                JoinDate,
                Email,
                COUNT(AccountID) OVER (ORDER BY JoinDate ASC) AS CumulativeUsers
            FROM UserAccount
            ORDER BY JoinDate ASC;
        """
    },
    {
        "title": "13. Window Function: DENSE_RANK() by Genre Popularity",
        "sql": """
            WITH RankedContent AS (
                SELECT 
                    g.GenreName,
                    m.Title,
                    AVG(wh.Rating) as AvgRating,
                    DENSE_RANK() OVER(PARTITION BY g.GenreName ORDER BY AVG(wh.Rating) DESC) as RatingRank
                FROM Genre g
                JOIN ContentGenre cg ON g.GenreID = cg.GenreID
                JOIN MediaContent m ON cg.ContentID = m.ContentID
                JOIN WatchHistory wh ON m.ContentID = wh.ContentID
                GROUP BY g.GenreName, m.Title
            )
            SELECT * FROM RankedContent WHERE RatingRank <= 3;
        """
    },
    {
        "title": "14. Window Function: User Engagement Quartiles (NTILE)",
        "sql": """
            WITH UserWatchTime AS (
                SELECT 
                    ProfileID, 
                    SUM(ProgressSeconds) as TotalSeconds
                FROM WatchHistory
                GROUP BY ProfileID
            )
            SELECT 
                p.ProfileName,
                uwt.TotalSeconds,
                NTILE(4) OVER(ORDER BY uwt.TotalSeconds DESC) as EngagementQuartile
            FROM Profile p
            JOIN UserWatchTime uwt ON p.ProfileID = uwt.ProfileID;
        """
    },
    {
        "title": "15. Window Function: Time-to-First-Watch Analysis",
        "sql": """
            WITH FirstWatch AS (
                SELECT 
                    p.AccountID, 
                    MIN(wh.WatchDate) as FirstStreamDate
                FROM Profile p
                JOIN WatchHistory wh ON p.ProfileID = wh.ProfileID
                GROUP BY p.AccountID
            )
            SELECT 
                ua.Email,
                ua.JoinDate,
                fw.FirstStreamDate,
                DATEDIFF(fw.FirstStreamDate, ua.JoinDate) AS DaysToFirstStream
            FROM UserAccount ua
            JOIN FirstWatch fw ON ua.AccountID = fw.AccountID
            WHERE DATEDIFF(fw.FirstStreamDate, ua.JoinDate) >= 0
            ORDER BY DaysToFirstStream DESC;
        """
    }
]

def run_all_queries():
    try:
        print("Connecting to NetflixDB...\n")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for idx, query in enumerate(queries):
            print(f"{'='*80}")
            print(f"{query['title']}")
            print(f"{'-'*80}")
            
            try:
                cursor.execute(query['sql'])
                
                # Fetch headers and rows
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                if not rows:
                    print("(Query executed successfully, but returned 0 rows.)\n")
                    continue
                
                # Use Pandas to format the output perfectly
                df = pd.DataFrame(rows, columns=columns)
                print(df.to_string(index=False))
                print("\n")
                
            except mysql.connector.Error as err:
                print(f"[ERROR executing query] {err}\n")

    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed. All queries executed.")

if __name__ == "__main__":
    # Pandas display options to ensure wide tables don't wrap awkwardly
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    run_all_queries()