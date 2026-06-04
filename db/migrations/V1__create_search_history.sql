CREATE TABLE search_history (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    destination_type VARCHAR(32) NOT NULL,
    unique_identifier VARCHAR(64) NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    adult_count TINYINT UNSIGNED NOT NULL DEFAULT 1,
    child_count TINYINT UNSIGNED NOT NULL DEFAULT 0,
    room_count TINYINT UNSIGNED NOT NULL DEFAULT 1,
    auto_suggest_id VARCHAR(64) NULL,
    search_key VARCHAR(64) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
