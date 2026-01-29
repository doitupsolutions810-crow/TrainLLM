import os

def is_testflight():
    """
    Detects if the current environment is likely TestFlight.
    Simulated for backend logic via environment variables.
    """
    # Check for APP_ENVIRONMENT or similar flags often set in CI/CD or Docker
    app_env = os.environ.get("APP_ENVIRONMENT", "").lower()
    is_beta = os.environ.get("IS_BETA_DISTRIBUTION", "").lower() == "true"
    
    if app_env == "testflight" or is_beta:
        return True
        
    return False

def get_runtime_environment():
    if is_testflight():
        return "Apple TestFlight (Beta)"
    
    if os.environ.get("FLASK_ENV") == "production":
        return "Production"
        
    return "Development/Local"
