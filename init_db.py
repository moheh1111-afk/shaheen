"""
سكريبت مستقل لإنشاء جداول PostgreSQL في Supabase
لا يستورد app.py لتجنب تفعيل SQLite
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 1. إعداد الرابط من متغير البيئة أو يدوياً
DATABASE_URL = os.getenv('DATABASE_URL')

# إذا لم يكن متغير البيئة موجوداً، أدخل الرابط يدوياً هنا:
if not DATABASE_URL:
    # استبدل هذا بالرابط الفعلي من Supabase
    DATABASE_URL = "postgresql://postgres:MohamedLaw2026@db.cklyncllpofxvbleoza.supabase.co:5432/postgres"

# تصحيح بروتوكول postgres:// إلى postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔗 جاري الاتصال بـ: {DATABASE_URL[:50]}...")

# 2. إنشاء تطبيق Flask مؤقت
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 3. تعريف جميع النماذج (مُكررة من app.py لتجنب الاستيراد)
class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    progress = db.Column(db.Integer, default=0)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_total = db.Column(db.Integer, default=0)
    status = db.Column(db.String(40), default='active')
    warning = db.Column(db.Boolean, default=False)
    last_activity = db.Column(db.String(40), default='2026-04-28')
    avatar_color = db.Column(db.String(20), default='#64748b')
    initials = db.Column(db.String(10), default='؟')

class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    done = db.Column(db.Boolean, default=False)
    date = db.Column(db.String(40), default='2026-04-28')

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(80), default='')
    client = db.Column(db.String(120), default='')
    status = db.Column(db.String(80), default='جديدة')
    priority = db.Column(db.String(80), default='متوسطة')
    date = db.Column(db.String(40), default='2026-04-28')

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(80), default='متوسطة')
    status = db.Column(db.String(80), default='قيد التنفيذ')
    assignee = db.Column(db.String(120), default='')
    date = db.Column(db.String(40), default='2026-04-28')

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), default='فرد')
    status = db.Column(db.String(80), default='نشط')
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(40), default='')
    date = db.Column(db.String(40), default='2026-04-28')

class LibraryItem(db.Model):
    __tablename__ = 'library_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(80), default='')
    category = db.Column(db.String(80), default='')
    date = db.Column(db.String(40), default='2026-04-28')

class EventItem(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(80), default='')
    date = db.Column(db.String(40), default='2026-04-28')
    location = db.Column(db.String(200), default='')

class PublishItem(db.Model):
    __tablename__ = 'publish_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(80), default='')
    status = db.Column(db.String(80), default='مخطط')
    date = db.Column(db.String(40), default='2026-04-28')

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), default='')
    category = db.Column(db.String(80), default='')
    status = db.Column(db.String(80), default='متاح')
    date = db.Column(db.String(40), default='2026-04-28')

# 4. إنشاء الجداول
if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("✅ تم إنشاء جميع الجداول في Supabase بنجاح!")
            print("\n📋 الجداول المُنشأة:")
            for table in db.metadata.tables.keys():
                print(f"   • {table}")
        except Exception as e:
            print(f"❌ فشل الاتصال: {e}")
            print("\nتأكد من:")
            print("1. صحة رابط DATABASE_URL")
            print("2. توفر اتصال الإنترنت")
            print("3. إعدادات جدار الحماية في Supabase")
