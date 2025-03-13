from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from flask_login import UserMixin



class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    books = db.relationship('Book', backref='author', lazy=True)  # علاقة واحد إلى متعدد
   


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    add_to_site_at = db.Column(db.Date, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)  
    price = db.Column(db.Float, nullable=False)
    appropriate = db.Column(db.String(20), nullable=False)  
    image_filename = db.Column(db.String(255))
    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable ')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
