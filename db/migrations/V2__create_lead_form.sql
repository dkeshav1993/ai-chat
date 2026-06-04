-- Lead Form: captures contact details when user requests human sales agent assistance
CREATE TABLE IF NOT EXISTS lead_form (
    id            BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    name          VARCHAR(255)     NOT NULL,
    phone         VARCHAR(20)      NOT NULL,
    email         VARCHAR(255)     NOT NULL,
    query         TEXT             NULL COMMENT 'Original chat query that triggered the lead',
    created_at    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_lead_email (email),
    INDEX idx_lead_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
