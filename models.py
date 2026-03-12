from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    price = db.Column(db.Integer, nullable=False)   # harga dalam sen (Rp)
    condition = db.Column(db.String(50))
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(200))
    image_filename2 = db.Column(db.String(200))
    image_filename3 = db.Column(db.String(200))
    image_filename4 = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    stock = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def get_images(self):
        images = []
        if self.image_filename:
            images.append(self.image_filename)
        if self.image_filename2:
            images.append(self.image_filename2)
        if self.image_filename3:
            images.append(self.image_filename3)
        if self.image_filename4:
            images.append(self.image_filename4)
        return images

    def __repr__(self):
        return f'<Product {self.name}>'

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Setting {self.key}>'

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    rating = db.Column(db.Integer, default=5)
    text = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.name}>'

class HeroSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HeroSlide {self.id}>'