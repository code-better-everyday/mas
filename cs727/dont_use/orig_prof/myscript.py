import mysql.connector

# Replace with your database connection details
host = "localhost"
user = "sqluser"
password = "password"
# user = "root"
# password = ""
database = "ratemyprofdb"

try:
    # Connect to the MySQL server
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


    if connection.is_connected():
        print("Connected to the MySQL database successfully")
    # Perform database operations here
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    def read_data():
        # Read data from the table
        select_query = "SELECT sid, sname FROM Student1"
        cursor.execute(select_query)
        students = cursor.fetchall()

        print("Employee Data:")
        for student in students:
            print(f"SID: {student[0]}, Sname: {student[1]}")  
    def write_data():
        # Read data from the table
        print("writing data happens here")
        # # Insert data into the table
        insert_query = "INSERT INTO Student1 (sid, sname, uni, gpa) VALUES (%s, %s, %s, %s)"
        student_data = (24, "John", "MIT", 3.5)
        cursor.execute(insert_query, student_data)
        connection.commit()
    def others1():
        # Read data from the table
        # select_query = "SELECT p.pid, p.pname, avg(score) as RScore FROM rating1 r, professor p WHERE r.pid = p.pid GROUP BY by pid HAVING count(*)>1"
        # Read data from the table
        select_query = "SELECT avg(score) FROM Rating1 "
        cursor.execute(select_query)
        students = cursor.fetchall()

        print("student Data:")
        for student in students:
            # print(f"SID: {student[0]}, Sname: {student[1]}")  
            print(f"Score: {student[0]}")  




# print("Data inserted successfully.")
    def insert_data():
        # Read data from the table
        print("insert data happens here")
    def update_data():
        # Read data from the table
        print("update data happens here")
    def others():
        # Read data from the table
        print("other queries happen here")

    def main():
        while True:
            print("Menu:")
            print("1. read data")
            print("2. write data")
            print("3. insert data")
            print("4. update data")
            print("5. others")
            print("6. Exit")
            
            choice = input("Enter your choice: ")
            if choice == '1':
                read_data()
            elif choice == '2':
                write_data()
            elif choice == '3':
                insert_data()
            elif choice == '4':
                update_data()
            elif choice == '5':
                others1()
            elif choice == '6':
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please select a valid option.")

    if __name__ == "__main__":
        main()
  




except mysql.connector.Error as e:
    print("Error:", e)

    

finally:
    # Close the database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Connection to MySQL database closed")

