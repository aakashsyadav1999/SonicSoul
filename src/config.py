import os

# Add database connection configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql_service"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "ray"),
    "password": os.getenv("DB_PASSWORD", "advicr49"),
    "database": os.getenv("DB_NAME", "music_prediction_db"),
    "table": "music_data",
}

# Update connection_string to use the potentially overridden host and port
DATABASE_CONFIG["connection_string"] = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"