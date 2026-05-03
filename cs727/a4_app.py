# create a simple command-line application that allows an admin to perform CRUD operations 
# on the UserAccount table in the NetflixDB database. 
# The application will connect to the MySQL database, execute SQL queries, and display results

import mysql.connector
from datetime import date

# Database Connection Configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1jOzVhEk*Vh2TRd',
    'database': 'NetflixDB'
}

def get_connection():
    return mysql.connector.connect(**db_config)

def create_user():
    print("\n--- CREATE NEW USER ---")
    email = input("Enter user email: ")
    country = input("Enter user country: ")
    password = input("Enter user password: ")
    
    # Present the plan options to the admin
    print("\nSelect Subscription Plan:")
    print("1. Basic (720p) - $9.99")
    print("2. Standard (1080p) - $15.49")
    print("3. Premium (4K) - $22.99")
    
    # Loop until the admin enters a valid option
    while True:
        plan_id = input("Enter Plan ID (1, 2, or 3): ")
        if plan_id in ['1', '2', '3']:
            break
        else:
            print("[WARNING] Invalid selection. Please enter 1, 2, or 3.")

    join_date = date.today()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO UserAccount (PlanID, Email, PasswordHash, JoinDate, Country) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (plan_id, email, password, join_date, country))
        conn.commit()
        print(f"\n[SUCCESS] User {email} created with AccountID: {cursor.lastrowid}")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def read_users():
    print("\n--- VIEW LATEST USERS ---")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Fetch the 5 most recently added users
        cursor.execute("SELECT AccountID, Email, Country, PlanID FROM UserAccount ORDER BY AccountID DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print(f"{'ID':<5} | {'Email':<30} | {'Country':<15} | {'PlanID':<5}")
        print("-" * 65)
        for row in rows:
            print(f"{row[0]:<5} | {row[1]:<30} | {row[2]:<15} | {row[3]:<5}")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def update_user():
    print("\n--- UPDATE USER PLAN ---")
    account_id = input("Enter the AccountID of the user to update: ")
    new_plan = input("Enter the new PlanID (1=Basic, 2=Standard, 3=Premium): ")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE UserAccount SET PlanID = %s WHERE AccountID = %s"
        cursor.execute(sql, (new_plan, account_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n[SUCCESS] AccountID {account_id} updated to PlanID {new_plan}.")
        else:
            print(f"\n[WARNING] No user found with AccountID {account_id}.")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def delete_user():
    print("\n--- DELETE USER ---")
    account_id = input("Enter the AccountID of the user to delete: ")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM UserAccount WHERE AccountID = %s"
        cursor.execute(sql, (account_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n[SUCCESS] AccountID {account_id} successfully deleted.")
        else:
            print(f"\n[WARNING] No user found with AccountID {account_id}.")
    except mysql.connector.Error as err:
        print(f"\n[ERROR] {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def main_menu():
    while True:
        print("\n=================================")
        print("  NETFLIX DATABASE MANAGER 1.0   ")
        print("=================================")
        print("1. Create a new user (CREATE)")
        print("2. View recent users (READ)")
        print("3. Upgrade/Update a user plan (UPDATE)")
        print("4. Delete a user (DELETE)")
        print("5. Exit Application")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            create_user()
        elif choice == '2':
            read_users()
        elif choice == '3':
            update_user()
        elif choice == '4':
            delete_user()
        elif choice == '5':
            print("\nExiting application. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number from 1 to 5.")

if __name__ == "__main__":
    main_menu()