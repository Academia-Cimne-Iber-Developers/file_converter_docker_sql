CREATE DATABASE IF NOT EXISTS conversions;
use conversions;

CREATE TABLE IF NOT EXISTS conversion_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(50) NOT NULL,
    source_format VARCHAR(10) NOT NULL,
    target_format VARCHAR(10) NOT NULL,
    file_size FLOAT NOT NULL,
    processing_time FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);