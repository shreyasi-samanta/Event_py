-- Drop tables if they already exist (optional)
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS users;

-- 1. USER TABLE
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,   -- For hashed passwords
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

-- 2. EVENT TABLE
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image VARCHAR(255),               -- Image path or URL
    location VARCHAR(150) NOT NULL,
    date DATE NOT NULL
);

-- 3. BOOKING TABLE
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    uid INT NOT NULL,
    e_id INT NOT NULL,

    CONSTRAINT fk_user
        FOREIGN KEY (uid)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_event
        FOREIGN KEY (e_id)
        REFERENCES events(id)
        ON DELETE CASCADE
);
ALTER TABLE events
ADD COLUMN price DECIMAL(10,2) NOT NULL DEFAULT 0.00;