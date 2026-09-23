
CREATE TABLE IF NOT EXISTS anno_users (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`username` VARCHAR(255) NOT NULL,
`email` VARCHAR(255) NOT NULL,
`password` VARCHAR(255) NOT NULL,
`status` ENUM('active', 'inactive') DEFAULT 'active',
`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO anno_users (username, email, `password`, `status`) VALUES ('denis', 'denis@example.com', '123', 'active');
INSERT INTO anno_users (username, email, `password`, `status`) VALUES ('alex', 'alex@example.com', '123', 'active');
INSERT INTO anno_users (username, email, `password`, `status`) VALUES ('test', 'test@example.com', '123', 'active');

CREATE TABLE IF NOT EXISTS admin_sessions (
`id` VARCHAR(64) PRIMARY KEY,
`user_id` INT NOT NULL,
`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
`expires_at` DATETIME NOT NULL
);