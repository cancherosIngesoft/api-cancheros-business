import os

class Config:
    pass
    """
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_secreto')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///cancheros.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """

class TestConfig(Config):
    pass
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    """
