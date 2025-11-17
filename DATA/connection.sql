-- 1) Create a dedicated user for Jupyter TCP connections
CREATE USER IF NOT EXISTS 'nb_user'@'127.0.0.1'
  IDENTIFIED WITH caching_sha2_password BY 'Super_Strong_Passw0rd!';

-- 2) Grant access to your schema
GRANT ALL PRIVILEGES ON text_to_sql.* TO 'nb_user'@'127.0.0.1';
FLUSH PRIVILEGES;

-- (optional) See what you have for root (useful for debugging)
SELECT Host, User, plugin FROM mysql.user WHERE User IN ('root', 'nb_user');
