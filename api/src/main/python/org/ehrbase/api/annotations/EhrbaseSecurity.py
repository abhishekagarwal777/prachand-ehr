from functools import wraps

def ehrbase_security(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Implement security checks or logging here if needed
        print("Security check applied")
        return func(*args, **kwargs)
    return wrapper

@ehrbase_security
def some_secure_function():
    print("Executing secure function")
