-- CREATE DATABASE ratemyprofdb;
-- use ratemyprofdb;
select database(); -- shows the active DB loaded

-- -- --------------------------
-- -- PROFESSOR TABLE
-- -- --------------------------
-- CREATE TABLE Professor(
-- PID int, 
-- Pname varchar(25) not null, 
-- Papers int, 
-- Topic varchar(25),
-- primary key (PID) 
-- );
-- -- --------------------------
-- -- STUDENT TABLE
-- -- --------------------------
-- CREATE TABLE Student1(
-- SID int, 
-- Sname varchar(25) not null,
-- Uni varchar(25) not null,
-- GPA double, 
-- primary key (SID) 
-- );

-- -- --------------------------
-- -- RATING TABLE
-- -- --------------------------
-- CREATE TABLE Rating1(
-- SID int, 
-- PID int,  
-- Score int not null, 
-- Attended int not null,
-- primary key (SID,PID), 
-- foreign key(SID) references Student1(SID), 
-- foreign key(PID) references Professor(PID),  
-- Check (Score between 0 and 100) 
-- );

-- -- inserting professor data
-- insert into Professor values (109,"Steven",10,"Java");
-- insert into Professor values (110,"Francis",50,"Databases");
-- insert into Professor values (111,"Daniel",40,"Java");
-- insert into Professor values (112,"Joy",20,"Java");

-- -- inserting rating data
-- insert into Rating1 values (23,109,6,60);
-- insert into Rating1 values (23,110,10,70);
-- insert into Rating1 values (24,111,8,40);
-- insert into Rating1 values (25,111,9,100);
-- insert into Rating1 values (25,109,4,20);
-- insert into Rating1 values (36,109,5,80);
-- insert into Rating1 values (36,112,1,4);

-- -- inserting Student data
-- insert into Student1 values (23,"Michelle","illinois Tech", 50.52);
-- insert into Student1 values (24,"Tomas","UChi",20.71);
-- insert into Student1 values (25,"Biden","illinois Tech",34.66);
-- insert into Student1 values (36,"John","UIC",10.82);

-- -- --------------------------
-- -- C.R.U.D operations
-- -- --------------------------
-- INSERT INTO Professor (PID, Pname, Papers, Topic) 
-- VALUES (113, "jane", 90, "Networks"), 
-- (114, "Sarah", 11, "Python"), 
-- (115, "Vick",65,"Networks"); 

-- select p.pname, r.score
-- from Professor p, Rating1 r
-- where p.pid = r.pid;

-- Update Professor
-- set Papers = Papers + 2
-- Where Topic ="Java" OR Topic= "Databases";

-- -- DELETE FROM Professor
-- -- Where PID = "115";

-- show index from Professor;
-- creating a new index
-- CREATE INDEX index_name ON Professor(Topic);
-- show index from Professor;


-- CREATE view prof_with_score5 as
--     SELECT p.Pname, r.Score, s.Sname 
--     FROM Professor p, Rating1 r, Student1 s 
--     WHERE p.pid = r.pid and s.sid = r.sid and r.score > 5; 

-- create temporary table student2( -- created a normal table; define table schema
-- sid int primary key,
-- uni varchar(20));

-- select * from student2;

-- insert into student2(sid, uni) -- then inserted data based on a query result
-- select sid, uni
-- from Student1
-- limit 2;

-- -- create tempo table based on query e.g., find profname, score with rating score > 8 points
-- create temporary table highScore
-- 	select p.pname, r.score
-- 	from Professor p, Rating1 r
-- 	where p.pid = r.pid and r.score > 8;

-- DELIMITER //
-- -- creating stored procedure (logic: task to compute the majority rating (%) of each professor)

-- CREATE PROCEDURE total_attended(IN p_id INT)
-- BEGIN

-- 	DECLARE m_rating DECIMAL(10, 2);
--     declare totalN int;
--     SELECT SUM(attended) INTO totalN
--     FROM Rating1;
--     SELECT (SUM(attended)/totalN) *100 INTO m_rating
--     FROM Rating1
--     WHERE pid = p_id;
    
--     SELECT CONCAT('majority rating per prof ', p_id, ': ', m_rating) AS result;
-- END;
-- //
-- DELIMITER ;
-- drop procedure total_attended;

-- CALL total_attended(111);
-- CALL total_attended(109);

-- -- -----------------------------------------------------
-- -- CREATE SQL FUNCTION
-- -- -- -----------------------------------------------------
-- DELIMITER //
-- -- counts the number of professors teaching the same topic
-- CREATE FUNCTION count_prof(T_opic varchar(20)) returns integer
-- 	deterministic -- the outcome of a non-deterministic function is not guaranteed to be consistent, 
--     -- and it can vary each time the function is invoked, so add the key word 'deterministic'.
-- BEGIN 
--    declare total int;
--    SELECT count(*) into total
--    FROM Professor p
--    where p.Topic = T_opic;
--    RETURN total; 
-- END //
-- delimiter ;
-- -- find topics taught by more than 1 professor
-- -- drop function count_prof;
-- -- select * from Professor
-- -- where count_prof(Topic) =1;

-- DELIMITER //
-- -- We use the DELIMITER command to change the delimiter from the default semicolon to double slashes. 
-- -- This is needed because triggers involve multiple statements.
-- CREATE PROCEDURE newRating
-- (
-- IN S_sids int,
-- IN P_pids int,
-- IN S_score int,
-- IN S_attended int)

-- BEGIN
--    -- declare the variable to store student ids and pids
--     DECLARE s_ids int;
-- 	DECLARE p_ids int;

--     -- get students ids
--     SELECT SID INTO s_ids
--     From Student1
--     where SID = s_ids;
    
-- 	-- get pids
--     SELECT PID INTO p_ids
--     From Professor
--     where PID = p_ids;

--     -- insert a new student's rating

--     INSERT INTO Rating1(SID, PID, Score, attended) 
--     values(S_sids, P_pids, S_score, S_attended);

-- END //
-- -- After defining the trigger, we reset the delimiter back to 
-- -- a semicolon using DELIMITER ;
-- DELIMITER ;


-- create table scoreTable(
-- PID int,
-- score_amount DECIMAL(10, 2),
-- primary key (PID)
-- );
-- -- Create the trigger
-- DELIMITER //
-- CREATE TRIGGER update_total_score
-- AFTER INSERT ON Rating1
-- FOR EACH ROW
-- BEGIN
--     DECLARE total_score DECIMAL(10, 2);
--     SELECT SUM(score) INTO total_score
--     FROM Rating1
--     WHERE PID = NEW.PID;

--     UPDATE scoreTable
--     SET score_amount = total_score
--     WHERE PID = NEW.PID;
-- END;
-- //
-- DELIMITER ;


-- -- --------------------------
-- -- TEAM TABLE USED IN BULK LOADING
-- -- --------------------------
-- CREATE table Team (
-- TmID char(3),
-- ConfID char(2),	
-- Ranking int,	
-- Playoff varchar(2),	
-- Name varchar(125), 	
-- Won int,
-- Lost int,
-- Games int,
-- primary key(TmID)
-- );

-- -- --------------------------
-- -- BULK LOADING
-- -- --------------------------
-- LOAD DATA INFILE '/home/coder/project/DB/team.csv' 
-- INTO TABLE Team 
-- FIELDS TERMINATED BY ',' 
-- ENCLOSED BY ''
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;


