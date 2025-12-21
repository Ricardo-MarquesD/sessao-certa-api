import bcrypt

class PasswordHasher:

    @staticmethod
    def to_hash(password:str)->str:
        password_byte = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds = 12)
        hashed = bcrypt.hashpw(password_byte, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password_input:str, hashed_password:str)->bool:
        password_byte = password_input.encode('utf-8')
        hashed_byte = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_byte, hashed_byte)