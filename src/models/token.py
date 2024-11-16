# from extensions import db
# from datetime import datetime

# class TokenBlacklist(db.Model):
#     __tablename__ = 'token_blacklist'
    
#     id = db.Column(db.Integer, primary_key=True)
#     jti = db.Column(db.String(36), nullable=False, unique=True)  # JTI (unique identifier of the JWT)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#     def __init__(self, jti):
#         self.jti = jti