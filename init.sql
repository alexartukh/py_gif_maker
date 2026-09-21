
CREATE TABLE IF NOT EXISTS anno_users (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`username` VARCHAR(255) NOT NULL,
`email` VARCHAR(255) NOT NULL,
`password` VARCHAR(255) NOT NULL,
`status` ENUM('active', 'inactive') DEFAULT 'active',
`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



