import mysql.connector
from faker import Faker
import random

fake = Faker()

# Database Connection Configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

def generate_mock_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("Connected to MySQL Database successfully.\n")

        # 1. Insert Subscription Plans
        print("Inserting Subscription Plans...")
        plans = [
            ('Basic', 9.99, '720p', 1),
            ('Standard', 15.49, '1080p', 2),
            ('Premium', 22.99, '4K', 4),
            ('Testing', 0.00, '480p', 1)  # The 4th plan with 0 users
        ]
        cursor.executemany(
            "INSERT INTO SubscriptionPlan (PlanName, MonthlyPrice, Resolution, MaxUsers) VALUES (%s, %s, %s, %s)",
            plans
        )
        
        # Dynamically fetch the real IDs from the database, ignoring the 'Testing' plan
        cursor.execute("SELECT PlanID, PlanName FROM SubscriptionPlan")
        active_plan_ids = [row[0] for row in cursor.fetchall() if row[1] != 'Testing']
        
        if not active_plan_ids:
            raise ValueError("No active plans found! Make sure SubscriptionPlan was populated.")

        # 2. Insert User Accounts (20 records)
        print("Inserting User Accounts...")
        account_ids = []
        for _ in range(20):
            plan_id = random.choice(active_plan_ids)
            email = fake.unique.email()
            password = fake.password(length=12)
            join_date = fake.date_between(start_date='-3y', end_date='today')
            country = fake.country()[:50]
            
            cursor.execute(
                "INSERT INTO UserAccount (PlanID, Email, PasswordHash, JoinDate, Country) VALUES (%s, %s, %s, %s, %s)",
                (plan_id, email, password, join_date, country)
            )
            account_ids.append(cursor.lastrowid)

        # 3. Insert Profiles (35 records)
        print("Inserting Profiles...")
        profile_ids = []
        maturities = ['TV-G', 'TV-PG', 'TV-14', 'TV-MA']
        for _ in range(35):
            account_id = random.choice(account_ids)
            profile_name = fake.first_name()
            maturity = random.choice(maturities)
            
            try:
                cursor.execute(
                    "INSERT INTO Profile (AccountID, ProfileName, MaturityRating) VALUES (%s, %s, %s)",
                    (account_id, profile_name, maturity)
                )
                profile_ids.append(cursor.lastrowid)
            except mysql.connector.Error as err:
                # This gracefully catches instances where our random generator 
                # hits the MaxUsers trigger we built in the schema!
                pass 

        # 4. Insert Media Content (30 records)
        print("Inserting Media Content...")
        content_ids = []
        types = ['Movie', 'TV Show']
        for _ in range(30):
            title = fake.catch_phrase()
            year = random.randint(1990, 2026)
            duration = random.randint(1200, 7200) # 20 mins to 2 hours
            c_type = random.choice(types)
            
            cursor.execute(
                "INSERT INTO MediaContent (Title, ReleaseYear, DurationSeconds, ContentType) VALUES (%s, %s, %s, %s)",
                (title, year, duration, c_type)
            )
            content_ids.append(cursor.lastrowid)

        # 5. Insert Genres (10 records)
        print("Inserting Genres...")
        genre_ids = []
        genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Documentary', 'Romance', 'Thriller', 'Animation', 'Fantasy']
        for genre in genres:
            cursor.execute("INSERT INTO Genre (GenreName) VALUES (%s)", (genre,))
            genre_ids.append(cursor.lastrowid)

        # 6. Insert ContentGenre (Many-to-Many Mappings)
        print("Inserting Content-Genre Mappings...")
        for c_id in content_ids:
            assigned_genres = random.sample(genre_ids, random.randint(1, 3))
            for g_id in assigned_genres:
                cursor.execute(
                    "INSERT INTO ContentGenre (ContentID, GenreID) VALUES (%s, %s)",
                    (c_id, g_id)
                )

        # 7. Insert Watch History (50 records)
        print("Inserting Watch History...")
        for _ in range(50):
            p_id = random.choice(profile_ids)
            c_id = random.choice(content_ids)
            watch_date = fake.date_time_between(start_date='-1y', end_date='now')
            progress = random.randint(60, 7200)
            rating = random.randint(1, 5)
            
            # INSERT IGNORE skips duplicates to satisfy our unique constraint
            cursor.execute(
                "INSERT IGNORE INTO WatchHistory (ProfileID, ContentID, WatchDate, ProgressSeconds, Rating) VALUES (%s, %s, %s, %s, %s)",
                (p_id, c_id, watch_date, progress, rating)
            )

        conn.commit()
        print("\nSUCCESS: All mock data inserted and committed!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    generate_mock_data()