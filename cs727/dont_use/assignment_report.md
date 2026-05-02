# NetflixDB Assignment Verification Report

Generated: 2026-05-02 09:43:42

This report is read-only. It documents what currently exists in `NetflixDB` and shows the SQL statements used to verify it.

## 1. Table Counts

- contentgenre: 58 rows (OK)
- genre: 15 rows (OK)
- mediacontent: 30 rows (OK)
- profile: 35 rows (OK)
- subscriptionplan: 15 rows (OK)
- useraccount: 20 rows (OK)
- watchhistory: 50 rows (OK)

```sql
SELECT TABLE_NAME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'NetflixDB' AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
```

Output: table names and row counts listed above.

## 2. CREATE TABLE Statements

### contentgenre
```sql
CREATE TABLE `contentgenre` (
  `ContentID` int NOT NULL,
  `GenreID` int NOT NULL,
  PRIMARY KEY (`ContentID`,`GenreID`),
  KEY `GenreID` (`GenreID`),
  CONSTRAINT `contentgenre_ibfk_1` FOREIGN KEY (`ContentID`) REFERENCES `mediacontent` (`ContentID`),
  CONSTRAINT `contentgenre_ibfk_2` FOREIGN KEY (`GenreID`) REFERENCES `genre` (`GenreID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### genre
```sql
CREATE TABLE `genre` (
  `GenreID` int NOT NULL AUTO_INCREMENT,
  `GenreName` varchar(50) NOT NULL,
  PRIMARY KEY (`GenreID`),
  UNIQUE KEY `GenreName` (`GenreName`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### mediacontent
```sql
CREATE TABLE `mediacontent` (
  `ContentID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(200) NOT NULL,
  `ReleaseYear` int DEFAULT NULL,
  `DurationSeconds` int DEFAULT NULL,
  `ContentType` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ContentID`),
  KEY `idx_media_title` (`Title`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### profile
```sql
CREATE TABLE `profile` (
  `ProfileID` int NOT NULL AUTO_INCREMENT,
  `AccountID` int NOT NULL,
  `ProfileName` varchar(50) NOT NULL,
  `MaturityRating` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ProfileID`),
  KEY `AccountID` (`AccountID`),
  CONSTRAINT `profile_ibfk_1` FOREIGN KEY (`AccountID`) REFERENCES `useraccount` (`AccountID`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### subscriptionplan
```sql
CREATE TABLE `subscriptionplan` (
  `PlanID` int NOT NULL AUTO_INCREMENT,
  `PlanName` varchar(50) NOT NULL,
  `MonthlyPrice` decimal(4,2) NOT NULL,
  `Resolution` varchar(10) DEFAULT NULL,
  `MaxUsers` int NOT NULL,
  PRIMARY KEY (`PlanID`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### useraccount
```sql
CREATE TABLE `useraccount` (
  `AccountID` int NOT NULL AUTO_INCREMENT,
  `PlanID` int NOT NULL,
  `Email` varchar(100) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `JoinDate` date NOT NULL,
  `Country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`AccountID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `PlanID` (`PlanID`),
  CONSTRAINT `useraccount_ibfk_1` FOREIGN KEY (`PlanID`) REFERENCES `subscriptionplan` (`PlanID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

### watchhistory
```sql
CREATE TABLE `watchhistory` (
  `HistoryID` int NOT NULL AUTO_INCREMENT,
  `ProfileID` int NOT NULL,
  `ContentID` int NOT NULL,
  `WatchDate` datetime NOT NULL,
  `ProgressSeconds` int NOT NULL,
  `Rating` int DEFAULT NULL,
  PRIMARY KEY (`HistoryID`),
  UNIQUE KEY `unique_watch` (`ProfileID`,`ContentID`),
  KEY `ContentID` (`ContentID`),
  CONSTRAINT `watchhistory_ibfk_1` FOREIGN KEY (`ProfileID`) REFERENCES `profile` (`ProfileID`),
  CONSTRAINT `watchhistory_ibfk_2` FOREIGN KEY (`ContentID`) REFERENCES `mediacontent` (`ContentID`),
  CONSTRAINT `watchhistory_chk_1` CHECK ((`Rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

## 3. Indexes

```sql
SHOW INDEX FROM MediaContent;
```

Output:
- Key_name=PRIMARY, Column_name=ContentID, Non_unique=0
- Key_name=idx_media_title, Column_name=Title, Non_unique=1

## 4. View

```sql
SHOW CREATE VIEW vw_HighlyRatedContent;
```

Output:
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_highlyratedcontent` AS select `m`.`Title` AS `Title`,avg(`w`.`Rating`) AS `AvgRating` from (`mediacontent` `m` join `watchhistory` `w` on((`m`.`ContentID` = `w`.`ContentID`))) group by `m`.`Title` having (avg(`w`.`Rating`) >= 4.0)

## 5. Trigger

```sql
SHOW CREATE TRIGGER trg_CheckProfileLimit;
```

Output:
CREATE DEFINER=`root`@`localhost` TRIGGER `trg_CheckProfileLimit` BEFORE INSERT ON `profile` FOR EACH ROW BEGIN
    DECLARE current_profiles INT DEFAULT 0;
    DECLARE max_allowed INT DEFAULT 0;

    SELECT COUNT(*) INTO current_profiles FROM Profile WHERE AccountID = NEW.AccountID;

    SELECT sp.MaxUsers INTO max_allowed
    FROM UserAccount ua
    JOIN SubscriptionPlan sp ON ua.PlanID = sp.PlanID
    WHERE ua.AccountID = NEW.AccountID
    LIMIT 1;

    IF current_profiles >= max_allowed THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maximum number of profiles reached for this subscription plan.';
    END IF;
END

## 6. Stored Procedure and Function

```sql
SELECT ROUTINE_NAME, ROUTINE_TYPE
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA='NetflixDB'
ORDER BY ROUTINE_TYPE, ROUTINE_NAME;
```

Output:
- FUNCTION: fn_TotalWatchTimeHours
- PROCEDURE: sp_LogWatchProgress

### sp_LogWatchProgress
```sql
SHOW CREATE PROCEDURE sp_LogWatchProgress;
```

Output:
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_LogWatchProgress`(
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
END

### fn_TotalWatchTimeHours
```sql
SHOW CREATE FUNCTION fn_TotalWatchTimeHours;
```

Output:
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_TotalWatchTimeHours`(p_ProfileID INT) RETURNS decimal(10,2)
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE total_hours DECIMAL(10,2) DEFAULT 0.00;
    SELECT IFNULL(SUM(ProgressSeconds) / 3600, 0.00) INTO total_hours
    FROM WatchHistory
    WHERE ProfileID = p_ProfileID;
    RETURN total_hours;
END

## 7. Temporary Table Requirement

Temporary tables are session-scoped and are not persisted in MySQL metadata, so they cannot be verified after the session ends.
If your assignment specifically requires a screenshot of a temporary table, use a one-off MySQL session and capture the result there.

## 8. Requirement Checklist

- At least 15 records per base table: Yes
- Index implemented: Yes
- View implemented: Yes
- Trigger implemented: Yes
- Stored procedure implemented: Yes
- Function implemented: Yes
