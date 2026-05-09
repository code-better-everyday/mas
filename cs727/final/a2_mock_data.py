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
            ('Testing', 0.00, '480p', 1)  
        ]
        # Use INSERT IGNORE just in case the plans are already there
        cursor.executemany(
            "INSERT IGNORE INTO SubscriptionPlan (PlanName, MonthlyPrice, Resolution, MaxUsers) VALUES (%s, %s, %s, %s)",
            plans
        )
        
        cursor.execute("SELECT PlanID, PlanName FROM SubscriptionPlan")
        active_plan_ids = [row[0] for row in cursor.fetchall() if row[1] != 'Testing']
        
        if not active_plan_ids:
            raise ValueError("No active plans found!")

        # 2. Insert User Accounts (Increased to 50)
        print("Inserting 50 User Accounts...")
        account_ids = []
        
        # Restrict to a pool of 30 specific countries to force data aggregation
        top_countries = [
            "United States", "Canada", "United Kingdom", "Australia", "Germany", 
            "France", "Japan", "Brazil", "India", "Mexico", 
            "Spain", "Italy", "South Korea", "Netherlands", "Sweden", 
            "Switzerland", "Argentina", "Colombia", "South Africa", "Nigeria", 
            "New Zealand", "Singapore", "Ireland", "Denmark", "Norway", 
            "Finland", "Belgium", "Austria", "Poland", "Turkey"
        ]

        for _ in range(50):
            plan_id = random.choice(active_plan_ids)
            email = fake.unique.email()
            password = fake.password(length=12)
            join_date = fake.date_between(start_date='-3y', end_date='today')
            country = random.choice(top_countries) # Pick from our curated list
            
            cursor.execute(
                "INSERT INTO UserAccount (PlanID, Email, PasswordHash, JoinDate, Country) VALUES (%s, %s, %s, %s, %s)",
                (plan_id, email, password, join_date, country)
            )
            account_ids.append(cursor.lastrowid)

        # 3. Insert Profiles (Loop 120 times)
        print("Inserting Profiles (Trigger will block accounts that exceed limits)...")
        profile_ids = []
        maturities = ['TV-G', 'TV-PG', 'TV-14', 'TV-MA']
        for _ in range(120):
            account_id = random.choice(account_ids)
            profile_name = fake.first_name()
            maturity = random.choice(maturities)
            
            try:
                cursor.execute(
                    "INSERT INTO Profile (AccountID, ProfileName, MaturityRating) VALUES (%s, %s, %s)",
                    (account_id, profile_name, maturity)
                )
                profile_ids.append(cursor.lastrowid)
            except mysql.connector.Error:
                # The custom Trigger catches accounts that try to exceed their plan limit
                pass 

        # 4. Insert Media Content (75 records)
        print("Inserting 75 Media Content Titles...")
        content_ids = []
        
        # A curated list of 85 highly recognizable movies and TV shows
        realistic_titles = [
            "Inception", "The Dark Knight", "Interstellar", "Stranger Things", "Breaking Bad", 
            "The Matrix", "Avengers: Endgame", "The Crown", "The Office", "Black Mirror", 
            "Gladiator", "The Godfather", "Pulp Fiction", "The Sopranos", "Game of Thrones", 
            "Parasite", "Dune", "The Mandalorian", "Succession", "The White Lotus",
            "Blade Runner 2049", "Mad Max: Fury Road", "Avatar", "Terminator 2", "Jurassic Park",
            "Die Hard", "John Wick", "Alien", "The Hunger Games", "The Batman",
            "The Wire", "True Detective", "Parks and Recreation", "Friends", "Seinfeld", 
            "Severance", "The Last of Us", "Better Call Saul", "Fargo", "Peaky Blinders",
            "Fight Club", "Forrest Gump", "The Shawshank Redemption", "The Silence of the Lambs", 
            "Seven", "The Prestige", "The Departed", "Whiplash", "Goodfellas", "No Country for Old Men", 
            "Shutter Island", "Zodiac", "Memento", "Prisoners", "Gone Girl", "Knives Out", 
            "The Social Network", "Toy Story", "Finding Nemo", "The Lion King", "Up", 
            "Wall-E", "Spider-Man: Into the Spider-Verse", "Spirited Away", "Coco", "Inside Out", 
            "Shrek", "The Grand Budapest Hotel", "Superbad", "Step Brothers", "The Hangover", 
            "Ghostbusters", "Back to the Future", "The Truman Show", "Groundhog Day", "Ratatouille", 
            "The Incredibles", "Catch Me If You Can", "The Big Lebowski", "Fargo", "The Shining", 
            "A Clockwork Orange", "Taxi Driver", "The Sixth Sense", "Schindler's List"
        ]

        # Use random.sample to pick 75 UNIQUE titles from the list above
        selected_titles = random.sample(realistic_titles, 75)
        
        for title in selected_titles:
            year = random.randint(1990, 2026)
            duration = random.randint(1200, 14400) # 20 mins to 4 hours
            
            # Smart logic: If it's a known TV show format (or just random chance), label it correctly
            if title in ["Stranger Things", "Breaking Bad", "The Crown", "The Office", "Black Mirror", "The Sopranos", "Game of Thrones", "The Mandalorian", "Succession", "The White Lotus", "The Wire", "True Detective", "Parks and Recreation", "Friends", "Seinfeld", "Severance", "The Last of Us", "Better Call Saul", "Peaky Blinders"]:
                c_type = 'TV Show'
            else:
                c_type = 'Movie'
            
            cursor.execute(
                "INSERT INTO MediaContent (Title, ReleaseYear, DurationSeconds, ContentType) VALUES (%s, %s, %s, %s)",
                (title, year, duration, c_type)
            )
            content_ids.append(cursor.lastrowid)

        # 5. Insert Genres (Expanded to 14)
        print("Inserting Genres...")
        genre_ids = []
        genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror', 'Documentary', 
                  'Romance', 'Thriller', 'Animation', 'Fantasy', 'Crime', 'Mystery', 'Family', 'Reality TV']
        for genre in genres:
            cursor.execute("INSERT INTO Genre (GenreName) VALUES (%s)", (genre,))
            genre_ids.append(cursor.lastrowid)

        # 6. Insert ContentGenre Mappings (Smart Mapping)
        print("Mapping Titles to Correct Real-World Genres...")
        
        # First, fetch all the Genre IDs from the database so we can link them
        cursor.execute("SELECT GenreName, GenreID FROM Genre")
        genre_dict = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Second, fetch all the inserted Media Content IDs and Titles
        cursor.execute("SELECT Title, ContentID FROM MediaContent")
        content_records = cursor.fetchall()

        # The Master Dictionary: All 85 titles mapped to their actual genres
        smart_genres = {
            "Inception": ["Sci-Fi", "Action", "Thriller"],
            "The Dark Knight": ["Action", "Crime", "Drama"],
            "Interstellar": ["Sci-Fi", "Drama"],
            "Stranger Things": ["Sci-Fi", "Horror", "Mystery"],
            "Breaking Bad": ["Crime", "Drama", "Thriller"],
            "The Matrix": ["Sci-Fi", "Action"],
            "Avengers: Endgame": ["Action", "Sci-Fi", "Fantasy"],
            "The Crown": ["Drama"],
            "The Office": ["Comedy"],
            "Black Mirror": ["Sci-Fi", "Drama", "Mystery"],
            "Gladiator": ["Action", "Drama"],
            "The Godfather": ["Crime", "Drama"],
            "Pulp Fiction": ["Crime", "Drama"],
            "The Sopranos": ["Crime", "Drama"],
            "Game of Thrones": ["Fantasy", "Drama", "Action"],
            "Parasite": ["Thriller", "Drama", "Comedy"],
            "Dune": ["Sci-Fi", "Action", "Drama"],
            "The Mandalorian": ["Sci-Fi", "Action", "Fantasy"],
            "Succession": ["Drama", "Comedy"],
            "The White Lotus": ["Comedy", "Drama", "Mystery"],
            "Blade Runner 2049": ["Sci-Fi", "Mystery", "Drama"],
            "Mad Max: Fury Road": ["Action", "Sci-Fi"],
            "Avatar": ["Sci-Fi", "Action", "Fantasy"],
            "Terminator 2": ["Action", "Sci-Fi"],
            "Jurassic Park": ["Sci-Fi", "Action", "Thriller"],
            "Die Hard": ["Action", "Thriller"],
            "John Wick": ["Action", "Crime", "Thriller"],
            "Alien": ["Sci-Fi", "Horror"],
            "The Hunger Games": ["Action", "Sci-Fi", "Thriller"],
            "The Batman": ["Action", "Crime", "Mystery"],
            "The Wire": ["Crime", "Drama"],
            "True Detective": ["Crime", "Drama", "Mystery"],
            "Parks and Recreation": ["Comedy"],
            "Friends": ["Comedy", "Romance"],
            "Seinfeld": ["Comedy"],
            "Severance": ["Sci-Fi", "Drama", "Mystery"],
            "The Last of Us": ["Drama", "Horror", "Sci-Fi"],
            "Better Call Saul": ["Crime", "Drama"],
            "Fargo": ["Crime", "Drama", "Thriller"],
            "Peaky Blinders": ["Crime", "Drama"],
            "Fight Club": ["Drama", "Thriller"],
            "Forrest Gump": ["Drama", "Romance", "Comedy"],
            "The Shawshank Redemption": ["Drama"],
            "The Silence of the Lambs": ["Crime", "Thriller", "Horror"],
            "Seven": ["Crime", "Mystery", "Thriller"],
            "The Prestige": ["Drama", "Mystery", "Sci-Fi"],
            "The Departed": ["Crime", "Drama", "Thriller"],
            "Whiplash": ["Drama"],
            "Goodfellas": ["Crime", "Drama"],
            "No Country for Old Men": ["Crime", "Drama", "Thriller"],
            "Shutter Island": ["Mystery", "Thriller"],
            "Zodiac": ["Crime", "Mystery", "Drama"],
            "Memento": ["Mystery", "Thriller"],
            "Prisoners": ["Crime", "Drama", "Mystery"],
            "Gone Girl": ["Mystery", "Thriller", "Drama"],
            "Knives Out": ["Mystery", "Comedy", "Crime"],
            "The Social Network": ["Drama"],
            "Toy Story": ["Animation", "Family", "Comedy"],
            "Finding Nemo": ["Animation", "Family", "Comedy"],
            "The Lion King": ["Animation", "Family", "Drama"],
            "Up": ["Animation", "Family", "Comedy"],
            "Wall-E": ["Animation", "Family", "Sci-Fi"],
            "Spider-Man: Into the Spider-Verse": ["Animation", "Action", "Sci-Fi"],
            "Spirited Away": ["Animation", "Family", "Fantasy"],
            "Coco": ["Animation", "Family", "Fantasy"],
            "Inside Out": ["Animation", "Family", "Comedy"],
            "Shrek": ["Animation", "Family", "Comedy", "Fantasy"],
            "The Grand Budapest Hotel": ["Comedy", "Drama"],
            "Superbad": ["Comedy"],
            "Step Brothers": ["Comedy"],
            "The Hangover": ["Comedy"],
            "Ghostbusters": ["Comedy", "Sci-Fi", "Fantasy"],
            "Back to the Future": ["Sci-Fi", "Comedy", "Action"],
            "The Truman Show": ["Drama", "Comedy", "Sci-Fi"],
            "Groundhog Day": ["Comedy", "Fantasy", "Romance"],
            "Ratatouille": ["Animation", "Family", "Comedy"],
            "The Incredibles": ["Animation", "Action", "Family"],
            "Catch Me If You Can": ["Crime", "Drama"],
            "The Big Lebowski": ["Comedy", "Crime"],
            "The Shining": ["Horror", "Mystery"],
            "A Clockwork Orange": ["Crime", "Sci-Fi", "Drama"],
            "Taxi Driver": ["Crime", "Drama"],
            "The Sixth Sense": ["Mystery", "Thriller", "Drama"],
            "Schindler's List": ["Drama", "Documentary"]
        }

        for title, c_id in content_records:
            # Look up the actual genres for this title (fallback to 'Drama' if a title somehow isn't in the dictionary)
            assigned_genre_names = smart_genres.get(title, ["Drama"])
            
            for g_name in assigned_genre_names:
                # Get the actual database ID for that genre string
                g_id = genre_dict.get(g_name)
                if g_id:
                    cursor.execute(
                        "INSERT INTO ContentGenre (ContentID, GenreID) VALUES (%s, %s)",
                        (c_id, g_id)
                    )

        # 7. Insert Watch History (Increased to 300)
        print("Inserting 300 Watch History Records...")
        
        
        # Randomly select 3 content IDs to be isolated and never watched
        unwatched_content = random.sample(content_ids, 3)
        # Create a new list of available content that excludes those 3
        available_content_ids = [cid for cid in content_ids if cid not in unwatched_content]

        for _ in range(300):
            p_id = random.choice(profile_ids)
            # Pick ONLY from the available pool
            c_id = random.choice(available_content_ids) 
            watch_date = fake.date_time_between(start_date='-1y', end_date='now')
            progress = random.randint(60, 7200)
            rating = random.randint(1, 5)
            
            cursor.execute(
                "INSERT IGNORE INTO WatchHistory (ProfileID, ContentID, WatchDate, ProgressSeconds, Rating) VALUES (%s, %s, %s, %s, %s)",
                (p_id, c_id, watch_date, progress, rating)
            )

        conn.commit()
        print("\nSUCCESS: Expanded mock data successfully inserted!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    generate_mock_data()