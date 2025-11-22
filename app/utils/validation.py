def validate_email(email):
    import re
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def validate_password(password, min_length=6):
    return isinstance(password, str) and len(password) >= min_length
