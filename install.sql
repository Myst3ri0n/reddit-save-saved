CREATE TABLE DOWNLOAD_LOG(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	DATE_DOWNLOADED TEXT,
	SAVED_USER TEXT,
	POSTED_BY TEXT,
	POSTED_DATE TEXT,
	SUB_REDDIT TEXT,
	URL TEXT,
	ALBUM_URL TEXT,
	FILE_NAME TEXT,
	PERMALINK TEXT,
	UP_VOTES TEXT,
	TITLE TEXT,
	IS_ALBUM TEXT,
	ALBUM_INDEX INT,
	DOWNLOAD_FAILED INT,
	ERROR_MSG TEXT,
	FAVE INT
);

CREATE TABLE JOB_TRACKER(
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	START_DATE TEXT,
	END_DATE TEXT,
	DOWNLOAD_COUNT INT
);

CREATE VIEW IMAGES_BY_SUBREDDIT AS
SELECT 	COUNT(*) AS COUNT, 
		SUB_REDDIT 
FROM 	DOWNLOAD_LOG 
WHERE 	DOWNLOAD_FAILED IS NULL
GROUP BY 
		SUB_REDDIT
ORDER BY
		COUNT DESC;

CREATE VIEW FAILED_DOWNLOADS AS
SELECT 	*
FROM 	DOWNLOAD_LOG 
WHERE 	DOWNLOAD_FAILED = 1
ORDER BY
		TITLE;