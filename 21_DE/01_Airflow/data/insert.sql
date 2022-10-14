CREATE TABLE IF NOT EXISTS iss_location (
country VARCHAR(255),
continent VARCHAR(255),
distance DECIMAL(6,1),
issLatitude DECIMAL(9,6),
issLongitude DECIMAL(9,6),
eventTimestamp TIMESTAMP,
processedTimestamp TIMESTAMP);
INSERT INTO iss_location
(country, continent, distance, issLatitude, issLongitude, eventTimestamp, processedTimestamp)
SELECT 'Lesotho' as country,
'Africa' as continent,
3293.1643325044406 as distance,
-50.4605 as issLatitude,
56.3153 as issLongitude,
TO_TIMESTAMP(1665610094) as eventTimestamp,
CURRENT_TIMESTAMP as processedTimestamp;