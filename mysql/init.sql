-- Drop tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS music_data;

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  spotify_access_token TEXT,
  email VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create music_data table
CREATE TABLE IF NOT EXISTS music_data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  track_id VARCHAR(255) NOT NULL,
  track_name VARCHAR(255) NOT NULL,
  artist_name VARCHAR(255) NOT NULL,
  mood VARCHAR(50) NOT NULL,
  user_id INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert test user
INSERT INTO users (username, password) VALUES ('testuser', 'testpassword')
ON DUPLICATE KEY UPDATE username=username;
