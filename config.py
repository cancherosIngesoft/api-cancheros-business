class Config:
    """Base configuration class."""

    DEBUG = False
    TESTING = False
    # ... otros atributos de configuración


class DevelopmentConfig(Config):
    """Development configuration class."""

    DEBUG = True
    # ... otros atributos específicos de desarrollo
