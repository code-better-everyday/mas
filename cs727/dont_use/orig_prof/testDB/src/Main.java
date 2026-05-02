import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Scanner;
// import java.sql.*;

public class Main {

    public static void main(String[] args) {
        String jdbcUrl = "jdbc:mysql://localhost:3306/ratemyprofdb";
        String username = "sqluser";
        String password = "password";
        Scanner keyboard = new Scanner(System.in);

        try {
            Connection connection = DriverManager.getConnection(jdbcUrl, username, password);

            // Read data

            boolean flag = true;
            printActions();
            while(flag){

                String str1 = keyboard.nextLine();
                int option = Integer.parseInt(str1);
                switch (option){
                    case 0 -> {
                    System.out.println("reading data");
//                        items.addItems();
                        String selectQuery = "SELECT SID, Sname FROM student1";
                        PreparedStatement selectStatement = connection.prepareStatement(selectQuery);
                        ResultSet rs = selectStatement.executeQuery();

                        while (rs.next()) {
                            int id = rs.getInt("SID");
                            String name = rs.getString("Sname");
                            System.out.println("ID: " + id + ", Name: " + name );
                        }

//                        // Close resources

//                        connection.close();
                        break;
                    }
                    case 1 ->{
//                    System.out.println("second option");
                        System.out.println("reading data");
//                        items.addItems();
                        String insertQuery = "INSERT INTO student1 (SID, Sname, Uni, GPA) VALUES (?, ?, ?, ?)";
                        PreparedStatement insertStatement = connection.prepareStatement(insertQuery);

                        insertStatement.setInt(1,999);
                        insertStatement.setString(2, "Pope");
                        insertStatement.setString(3, "IIT");
                        insertStatement.setDouble(4,2.20);
//            // insertStatement.setDouble(2, 50000.0);
                         int rowsInserted = insertStatement.executeUpdate();
                         System.out.println(rowsInserted + " rows inserted.");
//                        String selectQuery = "INSERT INTO student1 values (87, Mary, MIT, 4.59 )";
//                        PreparedStatement selectStatement = connection.prepareStatement(selectQuery);

//                        while (rs.next()) {
//                            int id = rs.getInt("SID");
//                            String name = rs.getString("Sname");
//                            System.out.println("ID: " + id + ", Name: " + name );
//                        }

                        // Close resources
//                        rs.close();
                        insertStatement.close();
//                        connection.close();
                        break;

                    }
                    case 2 ->{
                    System.out.println("third option");
//                        items.printItems();
                        break;
                    }
                    case 3 ->{
                        System.out.println("fourth option");
//                        items.printItems();
                        break;
                    }
                    case 4 ->{
                        System.out.println("fifth option");
//                        items.printItems();
                        break;
                    }
                    case 5 ->{
                        System.out.println("sixth option");
//                        items.printItems();
                        break;
                    }

                    default -> flag = false;
                }
                System.out.print("do you want to continue (Y/N): ");
                Scanner keyboard1 = new Scanner(System.in);
                char answer = keyboard1.next().charAt(0);
                if((answer == 'y') || (answer == 'Y')){
                    printActions();
                    flag= true;
                }else flag =false;
            }
            System.out.println("---thank you program shutting---!");



            // Close resources
//            rs.close();
//            selectStatement.close();
            connection.close();

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private static void printActions(){
        //use java textBlock to print the menu options
        String textBlock = """
                =======================
                  GROCERY LIST MENU
                =======================
                0 - Read data
                1 - Write data
                2 - Update data
                3 - Delete data
                4 - Window queries
                5 - OLAP queries
                6 - exit
                ------------------------
                Enter a number for which actions you want to do: """;

        System.out.print(textBlock + " ");

    }





}
