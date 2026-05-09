-- 1. Create and Use the Database
CREATE DATABASE IF NOT EXISTS NetflixDB;
USE NetflixDB;


-- So that when we run this multiple times, we don't get errors about existing tables, views, triggers, etc., we will drop them if they exist before creating them again.:
DROP VIEW IF EXISTS vw_HighlyRatedContent;
DROP TRIGGER IF EXISTS trg_CheckProfileLimit;
DROP PROCEDURE IF EXISTS sp_LogWatchProgress;
DROP FUNCTION IF EXISTS fn_TotalWatchTimeHours;

DROP TABLE IF EXISTS WatchHistory;
DROP TABLE IF EXISTS ContentGenre;
DROP TABLE IF EXISTS Profile;
DROP TABLE IF EXISTS UserAccount;
DROP TABLE IF EXISTS SubscriptionPlan;
DROP TABLE IF EXISTS MediaContent;
DROP TABLE IF EXISTS Genre;

-- 2. Create Tables
CREATE TABLE SubscriptionPlan (
    PlanID INT PRIMARY KEY AUTO_INCREMENT,
    PlanName VARCHAR(50) NOT NULL,
    MonthlyPrice DECIMAL(4,2) NOT NULL,
    Resolution VARCHAR(10),
    MaxUsers INT NOT NULL
);

CREATE TABLE UserAccount (
    AccountID INT PRIMARY KEY AUTO_INCREMENT,
    PlanID INT NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    JoinDate DATE NOT NULL,
    Country VARCHAR(50),
    FOREIGN KEY (PlanID) REFERENCES SubscriptionPlan(PlanID)
);

ALTER TABLE netflixdb.UserAccount ADD UNIQUE (Email);

CREATE TABLE Profile (
    ProfileID INT PRIMARY KEY AUTO_INCREMENT,
    AccountID INT NOT NULL,
    ProfileName VARCHAR(50) NOT NULL,
    MaturityRating VARCHAR(10),
    FOREIGN KEY (AccountID) REFERENCES UserAccount(AccountID)
);

CREATE TABLE MediaContent (
    ContentID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(200) NOT NULL,
    ReleaseYear INT,
    DurationSeconds INT,
    ContentType VARCHAR(20)
);

CREATE TABLE Genre (
    GenreID INT PRIMARY KEY AUTO_INCREMENT,
    GenreName VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE ContentGenre (
    ContentID INT,
    GenreID INT,
    PRIMARY KEY (ContentID, GenreID),
    FOREIGN KEY (ContentID) REFERENCES MediaContent(ContentID),
    FOREIGN KEY (GenreID) REFERENCES Genre(GenreID)
);

CREATE TABLE WatchHistory (
    HistoryID INT PRIMARY KEY AUTO_INCREMENT,
    ProfileID INT NOT NULL,
    ContentID INT NOT NULL,
    WatchDate DATETIME NOT NULL,
    ProgressSeconds INT NOT NULL,
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    FOREIGN KEY (ProfileID) REFERENCES Profile(ProfileID),
    FOREIGN KEY (ContentID) REFERENCES MediaContent(ContentID),
    -- Unique constraint required for the UPSERT logic to work
    UNIQUE KEY unique_watch (ProfileID, ContentID) 
);

-- 3. Advanced Features 

-- INDEX: Speed up searching for a movie by its title
CREATE INDEX idx_media_title ON MediaContent(Title);

-- VIEW: Find the highest-rated content on the platform
CREATE VIEW vw_HighlyRatedContent AS
SELECT m.Title, AVG(w.Rating) as AvgRating
FROM MediaContent m
JOIN WatchHistory w ON m.ContentID = w.ContentID
GROUP BY m.Title
HAVING AVG(w.Rating) >= 4.0;

-- TRIGGER: Prevent creating a profile if the plan limit is reached
DELIMITER //
CREATE TRIGGER trg_CheckProfileLimit
BEFORE INSERT ON Profile
FOR EACH ROW
BEGIN
    DECLARE current_profiles INT;
    DECLARE max_allowed INT;

    SELECT COUNT(*) INTO current_profiles FROM Profile WHERE AccountID = NEW.AccountID;
    
    SELECT sp.MaxUsers INTO max_allowed
    FROM UserAccount ua
    JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
    WHERE ua.AccountID = NEW.AccountID;

    IF current_profiles >= max_allowed THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Maximum number of profiles reached for this subscription plan.';
    END IF;
END //
DELIMITER ;

-- STORED PROCEDURE: The "UPSERT" for logging watch progress
DELIMITER //
CREATE PROCEDURE sp_LogWatchProgress(
    IN p_ProfileID INT,
    IN p_ContentID INT,
    IN p_Seconds INT,
    IN p_Rating INT
)
BEGIN
    INSERT INTO WatchHistory (ProfileID, ContentID, WatchDate, ProgressSeconds, Rating)
    VALUES (p_ProfileID, p_ContentID, NOW(), p_Seconds, p_Rating)
    ON DUPLICATE KEY UPDATE
        WatchDate = NOW(),
        ProgressSeconds = p_Seconds,
        Rating = IFNULL(p_Rating, Rating);
END //
DELIMITER ;

-- FUNCTION: Calculate the total hours a specific profile has spent watching
DELIMITER //
CREATE FUNCTION fn_TotalWatchTimeHours(p_ProfileID INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE total_hours DECIMAL(10,2);
    SELECT SUM(ProgressSeconds) / 3600 INTO total_hours
    FROM WatchHistory
    WHERE ProfileID = p_ProfileID;
    RETURN IFNULL(total_hours, 0.00);
END //
DELIMITER ; 