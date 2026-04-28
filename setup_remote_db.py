import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ضع رابط Supabase الخاص بك هنا يدوياً للتأكد من نجاح العملية
DB_URL = "postgresql://postgres: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@db.uupfhmfayixurssyofhp.supabase.co:5432/postgres"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف الموديلات يدوياً هنا لضمان إنشائها في Supabase
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Lawsuit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    case_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(50))

with app.app_context():
    try:
        db.create_all()
        print("✅ تم إنشاء الجداول في Supabase بنجاح تام!")
    except Exception as e:
        print(f"❌ خطأ: {e}")
