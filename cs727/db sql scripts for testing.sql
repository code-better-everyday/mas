select * from netflixdb.vw_highlyratedcontent


CALL netflixdb.sp_LogWatchProgress(1, 15, 3600, 5);

select * from netflixdb.useraccount

SELECT netflixdb.fn_TotalWatchTimeHours(1) AS TotalWatchHours;

SELECT AccountID, Email 
FROM  netflixdb.UserAccount 
WHERE PlanID = 1 
LIMIT 1;

INSERT INTO netflixdb.Profile (AccountID, ProfileName, MaturityRating)
VALUES (3, 'Main Profile', 'TV-MA');

ALTER TABLE netflixdb.UserAccount ADD UNIQUE (Email);