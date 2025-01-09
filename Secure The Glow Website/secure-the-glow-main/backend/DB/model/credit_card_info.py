from app import ma, db, datetime
from cryptography.fernet import Fernet

# Generate and securely store this key
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

class CreditCardInfo(db.Model):
    __tablename__ = 'credit_card_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(30), db.ForeignKey('users.email', ondelete="CASCADE"), nullable=False)  # Foreign key to users
    card_number_encrypted = db.Column(db.LargeBinary, nullable=False)  # Encrypted card number
    card_last_four = db.Column(db.String(4), nullable=False)  # Last 4 digits of the card
    expiration_date = db.Column(db.String(7), nullable=False)  # Format: MM/YYYY
    name_on_card = db.Column(db.String(255), nullable=False)  # Name as it appears on the card
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, user_email, card_number, expiration_date, name_on_card):
        self.user_email = user_email
        self.card_number_encrypted = cipher_suite.encrypt(card_number.encode())  # Encrypt the card number
        self.card_last_four = card_number[-4:]  # Store only the last 4 digits
        self.expiration_date = expiration_date
        self.name_on_card = name_on_card

    def decrypt_card_number(self):
        """Decrypt and return the full card number."""
        return cipher_suite.decrypt(self.card_number_encrypted).decode()

class CreditCardInfoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CreditCardInfo
        fields = ("id", "user_email", "card_last_four", "expiration_date", "name_on_card", "created_at")

credit_card_info_schema = CreditCardInfoSchema()
credit_card_infos_schema = CreditCardInfoSchema(many=True)
