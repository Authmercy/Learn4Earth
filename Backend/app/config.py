import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "EcoLearn AI"
    PROJECT_VERSION: str = "1.0.0"

    # Database (MySQL distant)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://magma:YAN%40mol1234@159.89.13.54:3306/ecolearnai_db?charset=utf8mb4",
    )

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Chiffrement RGPD (Fernet / AES)
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")

    # AI Service
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://ai-service:5000")

    # Umoja / FreshPay Card API (paiement par carte bancaire - PRODUCTION)
    MOKO_MERCHANT_CODE: str = os.getenv("MOKO_MERCHANT_CODE", "m3Z4PQ2xawz3p")
    MOKO_MERCHANT_ID: str = os.getenv("MOKO_MERCHANT_ID", "jNdXa~)e!C]04y&4b")
    MOKO_API_KEY: str = os.getenv("MOKO_API_KEY", "cb708fd745f34c78a07f4ff2b61a7531")
    MOKO_API_SECRET: str = os.getenv("MOKO_API_SECRET", "08a85493a552f6b93c1757c3627f3c9f5c317b14e00b753f2c344d162eac9d7c")
    MOKO_CALLBACK_SECRET: str = os.getenv("MOKO_CALLBACK_SECRET", "1d62a5fabff23029308d6c755a22ee48f40eb348ce068c7973932a6a49f8a399")
    MOKO_COMMISSION_RATE: float = float(os.getenv("MOKO_COMMISSION_RATE", "3.50"))
    MOKO_BASE_URL: str = os.getenv("MOKO_BASE_URL", "https://card.gofreshpay.com")
    MOKO_CALLBACK_URL: str = os.getenv("MOKO_CALLBACK_URL", "http://localhost:8000/api/payments/moko/callback")

    # MGT-SMS (envoi de SMS)
    SMS_API_URL: str = os.getenv("SMS_API_URL", "https://api.magictech-sms.com/send-sms")
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "")
    SMS_SENDER_ID: str = os.getenv("SMS_SENDER_ID", "EcoLearnAI")

    # Email SMTP (Gmail)
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "465"))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "ylangwana@gmail.com")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "nqoz qead ymmx kguj")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "EcoLearn AI")

    # Duree de validite du code OTP (minutes)
    OTP_EXPIRY_MINUTES: int = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))

    # Redis (cache)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))

    # Base de donnees de backup (replication cron)
    BACKUP_DATABASE_URL: str = os.getenv(
        "BACKUP_DATABASE_URL",
        "mysql+pymysql://magma:YAN%40mol1234@159.89.13.55:3306/ecolearnai_db_backup?charset=utf8mb4",
    )
    BACKUP_CRON_HOUR: int = int(os.getenv("BACKUP_CRON_HOUR", "1"))   # 1h du matin
    BACKUP_CRON_MINUTE: int = int(os.getenv("BACKUP_CRON_MINUTE", "0"))
    BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() in ("true", "1", "yes")

    # Monitoring
    MONITORING_ENABLED: bool = os.getenv("MONITORING_ENABLED", "true").lower() in ("true", "1", "yes")
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() in ("true", "1", "yes")

    # Carbon settings
    CARBON_PER_KWH: float = float(os.getenv("CARBON_PER_KWH", "0.475"))
    ENERGY_PER_HOUR_KWH: float = float(os.getenv("ENERGY_PER_HOUR_KWH", "0.2"))
    TREES_PER_TON_CO2: int = int(os.getenv("TREES_PER_TON_CO2", "6"))
    CO2_THRESHOLD_KG: float = float(os.getenv("CO2_THRESHOLD_KG", "10.0"))


settings = Settings()
