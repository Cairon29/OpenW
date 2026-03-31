import os

class Config:
    # General configuration
    SECRET_KEY                      = os.getenv('SECRET_KEY', "una-clave-secreta-de-respaldo")
    BACKEND_PORT                    = int(os.getenv('BACKEND_PORT', 2222))
    GROQ_API_KEY                    = os.getenv('GROQ_API_KEY')

    # Database configuration
    DB_USER                         = os.getenv('DB_USER', 'OpenWAdmin')
    DB_PASSWORD                     = os.getenv('DB_PASSWORD', 'Apex_999')
    DB_NAME                         = os.getenv('DB_NAME', 'OpenW')
    DB_HOST                         = os.getenv('DB_HOST', 'db')
    DB_PORT                         = int(os.getenv('DB_PORT', 5432))
    SQLALCHEMY_DATABASE_URI         = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Email configuration (SMTP Gmail)
    GMAIL_USER                      = os.getenv('GMAIL_USER')
    GMAIL_APP_PASSWORD              = os.getenv('GMAIL_APP_PASSWORD')
    FRONTEND_URL                    = os.getenv('FRONTEND_URL', 'http://localhost:1111')

    # Whatsapp API configuration
    WHATSAPP_APP_ID                 = os.getenv('WHATSAPP_APP_ID')
    WHATSAPP_ACCESS_TOKEN           = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID        = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_BUSINESS_ACCOUNT_ID    = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
    WHATSAPP_VERIFY_TOKEN           = os.getenv('WHATSAPP_VERIFY_TOKEN')
    WHATSAPP_APP_SECRET             = os.getenv('WHATSAPP_APP_SECRET')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

_env = os.getenv('FLASK_MODE', 'development')
config = ProductionConfig if _env == 'production' else DevelopmentConfig