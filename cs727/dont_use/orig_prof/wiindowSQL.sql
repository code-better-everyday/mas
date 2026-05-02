-- show databases;
-- create DATABASE OLAPDB1;
use OLAPDB1;
-- SHOW tables;
-- SELECT DATABASE();

-- creating the employee1 table
CREATE TABLE employee1(
row_num int primary key,
first_name varchar(25),
last_name varchar(25),
dept varchar(25),
salary double);



-- inserting records into employee table
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (1,'Karen', 'Colmenares', 'sales', 10);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (2,'Guy', 'Himuro', 'logistics', 20);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (3,'Irene', 'Mikkilineni', 'accounts', 20);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (4,'Sigal', 'Tobias', 'HR', 20);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (5,'Shelli', 'Baida', 'logistics', 60);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (6,'Alexander', 'Khoo', 'accounts', 80);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (7,'Britney', 'Everett', 'HR', 80);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (8,'James', 'Madison', 'logistics', 100);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (9,'Diana', 'Lorentz', 'support', 110);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (10,'Jennifer', 'Whalen', 'logistics', 110);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (11,'David', 'Austin', 'logistics', 110);
INSERT INTO employee1(row_num, first_name, last_name, dept, salary) values (12,'Valli', 'Pataballa', 'support', 200);



-- usage of rank()

SELECT row_num, first_name, last_name, salary, dept,
rank() OVER (ORDER BY salary) as s_rank
FROM employee1;

--  usage of dense_rank()
SELECT row_num, first_name, last_name, salary, dept,
dense_rank() OVER (ORDER BY salary) as s_dense_rank
FROM employee1;

 -- usage multiple rank clauses in one select
SELECT row_num, first_name, last_name, salary, 
rank() OVER (ORDER BY salary) as s_rank,
dense_rank() OVER (ORDER BY salary) as s_dense_rank
FROM employee1;

  -- usage ranking over a partition
SELECT first_name, last_name, salary, dept,
rank() OVER (PARTITION BY dept ORDER BY salary) as s_rank
FROM employee1;

-- usage of percentage_rank()
SELECT first_name, last_name, salary, 
ROUND(PERCENT_RANK() OVER (ORDER BY salary),2) as 's_percent_rank',
ROUND(PERCENT_RANK() OVER (ORDER BY salary),2)*100 as 's_percent_rank (%age)'
FROM employee1;
 
 -- usage of cumulative distribution
SELECT first_name, last_name, salary, 
ROUND(CUME_DIST() OVER (ORDER BY salary),2) as 's_cume_dist',
ROUND(ROUND(CUME_DIST() OVER (ORDER BY salary),2)*100,2) as 's_cume_dist (%age)'
FROM employee1;

-- usage of row_number
SELECT ROW_NUMBER() OVER (ORDER BY salary) as row_num1,
first_name, last_name, salary, dept,
rank() OVER (ORDER BY salary) as s_rank
FROM employee1;

-- usage of ntile(n)
SELECT row_num, first_name, salary,
NTILE(2) OVER (ORDER BY salary) as 's_ntile(2)',
NTILE(3) OVER (ORDER BY salary) as 's_ntile(3)',
NTILE(4) OVER (ORDER BY salary) as 's_nitle(4)',
NTILE(5) OVER (ORDER BY salary) as 's_ntile(5)'
FROM employee1;

-- windowing functions
create table salesProduct(
saleDate varchar(50),
product varchar(50),
value int);


-- inserting records in salesProduct
insert into salesProduct values 
("2014/08/01", "mouse",10),
("2014/08/02","tablet", 30),
("2014/08/03","desktop", 40),
("2014/08/04","laptop", 20),
("2014/08/05","keyboard",60),
("2014/08/06", "desktop", 10),
("2014/08/07","tablet", 5),
("2014/08/08","tablet", 30),
("2014/08/09","desktop", 50),
("2014/08/10","tablet", 5);

-- Given product sales values for each date, calculate the average sales of products for each previous day, on that day and the next day.
SELECT saleDate, product, value, AVG(value)
OVER (ORDER  BY saleDate ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) as '3-day Averages'
FROM salesProduct;

-- find running total for each product category, you want to see the accummulating values in each product category
SELECT saleDate, product, value, 
SUM(value) OVER (PARTITION BY product ORDER  BY saleDate ROWS UNBOUNDED PRECEDING) as 'Running totals per product category', 
AVG(value) OVER (PARTITION BY product ORDER  BY saleDate ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) as '3-day Averages'
FROM salesProduct;

-- find running total and running averages in each product category
SELECT saleDate, product, value, 
SUM(value) OVER (PARTITION BY product ROWS UNBOUNDED PRECEDING) as 'Running totals per product category', 
ROUND(AVG(value) OVER (PARTITION BY product ROWS UNBOUNDED PRECEDING),2) as 'Running averages per product category'
FROM salesProduct;
-- ----------------------
-- OLAP Queries
-- ----------------------
-- drop database OLAPDB;
-- create database OLAPDB;
-- use OLAPDB;
-- creating sales table

create table sales (
product CHAR(1),
quarters char(2),
region varchar(20), 
salesqty int);

 -- inserting records in sales table
insert into sales values 
("A","Q1","Europe",10),
("A","Q1","America",20),
("A","Q2","Europe",	20),
("A","Q2","America",50),
("A","Q3","America",20),
("A","Q4","Europe",10),
("A","Q4","America",30),
("B","Q1","Europe",40),
("B","Q1","America",60),
("B","Q2","Europe",20),
("B","Q2","America",10),
("B","Q3","America",20),
("B","Q4","Europe",10),
("B","Q4","America",40);

-- aggregate group by query; find total salesqty per product, quarters, region
select product, quarters, region, sum(qty) as totalSales
from sales
GROUP BY product, quarters, region;

-- find the total salesqty and number of quarters for each region
select region, count(quarters), sum(salesqty) as totalSales
from sales
GROUP BY region WITH ROLLUP;

-- ROLLUP total salesqty per product, quarters, region along with the subtotal
select product, quarters, region, sum(salesqty) as totalSales
from sales
GROUP BY product, quarters, region WITH ROLLUP;

-- CUBE total salesqty per product, quarters, region, along all subtotal for each sub group
select product, quarters, region, sum(salesqty) as totalSales
from sales
GROUP BY CUBE (product, quarters, region);

-- -- ROLLUP and grouping sets query works well in mysql
select product, quarters, region, sum(salesqty) as totalSales,
grouping (region) as regionFlag,
grouping(quarters) as quarterFlag
from sales
GROUP BY product, quarters, region WITH ROLLUP; 



-- -- -----------------------------
-- -- TRY ROLLUP AND CUBE FUNCTIONS IN PSQL DBMS
-- select product, quarters, region, sum(salesqty) as totalSales
-- from sales
-- GROUP BY CUBE (product, quarters, region);
-- -- -----------------------------