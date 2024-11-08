from models.token import TokenBlacklist
from extensions import db

def add_token_to_blacklist(jti):
    """Adds a token's JTI to the blacklist."""
    try:
        if TokenBlacklist.query.filter_by(jti=jti).first():
            return {"message": "Token is already blacklisted."}, 400

        blacklisted_token = TokenBlacklist(jti=jti)
        db.session.add(blacklisted_token)
        db.session.commit()

        return {"message": "Token successfully blacklisted."}, 200

    except Exception as ex:
        db.session.rollback()
        return {"message": f"An error occurred: {ex}"}, 500
