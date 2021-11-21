from os import environ

MYSQL_USER = environ.get("MYSQL_USER")
MYSQL_PASSWORD = environ.get("MYSQL_PASSWORD")
MYSQL_DATABASE = environ.get("MYSQL_DATABASE")
MYSQL_HOST = environ.get("MYSQL_HOST")
MYSQL_PORT = environ.get("MYSQL_PORT")


class Config(object):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SLEEP_TIME = 3
    
    # Image Validation parameters
    MAX_UPLOAD_SIZE = 1024 * 1024
    UPLOAD_EXTENSIONS = ['.png']
    UPLOAD_PATH = 'static/img'
    
    # Email parameters
    MAIL_USERNAME = environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = environ.get("MAIL_PASSWORD")
    MAIL_PORT = 587
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # Reset PW parameters
    RESET_PW_KEY = environ.get("RESET_PW_KEY")
    RESET_PW_SALT = environ.get("RESET_PW_SALT")

    # OTP Secret
    OTP_SECRET = environ.get("OTP_SECRET")

    # RECAPTCHA Secret
    RECAPTCHA_SECRET = environ.get("RECAPTCHA_SECRET")
    

class ProductionConfig(Config):
    TESTING = False


class TestConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True
    TEST_SESSION_MOD = 2


class DevelopmentConfig(Config):
    TESTING = False
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
