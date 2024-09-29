from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_injector import FlaskInjector
from injector import Module, provider, singleton

# Initialize Flask application
app = Flask(__name__)

# Configuration classes can be added here
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Example configuration
app.config['CACHE_TYPE'] = 'simple'  # Example configuration

# Initialize extensions
db = SQLAlchemy(app)
cache = Cache(app)

class ServiceModuleConfiguration(Module):
    """Configuration module for services."""

    @provider
    @singleton
    def provide_db(self) -> SQLAlchemy:
        """Provide the SQLAlchemy instance."""
        return db

    @provider
    @singleton
    def provide_cache(self) -> Cache:
        """Provide the cache instance."""
        return cache

def configure_injector(app: Flask):
    """Configure Flask-Injector for dependency injection."""
    FlaskInjector(app=app, modules=[ServiceModuleConfiguration])

if __name__ == "__main__":
    configure_injector(app)
    app.run(debug=True)  # Start the Flask application
