-- Total number of measurements
SELECT COUNT(*) FROM measurements;

-- Average temp across all measurements
SELECT AVG(temperature) FROM measurements;

-- Measurements from the last 24 hours
SELECT * FROM measurements WHERE created_at >= NOW() - INTERVAL '24 hours';
