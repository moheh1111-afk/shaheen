"""
نسخة Vercel مع PostgreSQL (Supabase)
"""
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from google import genai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shaheen_secret'

# ================== إعداد قاعدة البيانات PostgreSQL ==================
uri = os.getenv('DATABASE_URL')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///instance/shaheen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================== نماذج قاعدة البيانات ==================
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

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "progress": self.progress, "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total, "status": self.status,
            "warning": self.warning, "last_activity": self.last_activity,
            "avatar_color": self.avatar_color, "initials": self.initials
        }

class Milestone(db.Model):
    __tablename__ = 'milestones'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    done = db.Column(db.Boolean, default=False)
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "done": self.done, "date": self.date}

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    case_type = db.Column(db.String(80), default='')
    client = db.Column(db.String(120), default='')
    status = db.Column(db.String(80), default='جديدة')
    priority = db.Column(db.String(80), default='متوسطة')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "type": self.case_type, "client": self.client, "status": self.status, "priority": self.priority, "date": self.date}

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(80), default='متوسطة')
    status = db.Column(db.String(80), default='قيد التنفيذ')
    assignee = db.Column(db.String(120), default='')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "priority": self.priority, "status": self.status, "assignee": self.assignee, "date": self.date}

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(80), default='فرد')
    status = db.Column(db.String(80), default='نشط')
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(40), default='')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "name": self.name, "type": self.type, "status": self.status, "email": self.email, "phone": self.phone, "date": self.date}

class LibraryItem(db.Model):
    __tablename__ = 'library_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(80), default='')
    category = db.Column(db.String(80), default='')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "type": self.item_type, "category": self.category, "date": self.date}

class EventItem(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(80), default='')
    date = db.Column(db.String(40), default='2026-04-28')
    location = db.Column(db.String(200), default='')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "type": self.event_type, "date": self.date, "location": self.location}

class PublishItem(db.Model):
    __tablename__ = 'publish_items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(80), default='')
    status = db.Column(db.String(80), default='مخطط')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "platform": self.platform, "status": self.status, "date": self.date}

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(120), default='')
    category = db.Column(db.String(80), default='')
    status = db.Column(db.String(80), default='متاح')
    date = db.Column(db.String(40), default='2026-04-28')

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author, "category": self.category, "status": self.status, "date": self.date}

CEO_IDENTITY = {
    "name": "المحامي محمد إحسان الشواف",
    "title": "المؤسس والمدير التنفيذي",
    "role_en": "CEO",
    "initials": "مح",
    "avatar_color": "#d97706"
}

SIDEBAR_CONFIG = {
    "groups_order": ["المحاماة", "التطوير المعرفي", "العلاقات العامة", "الإعلام الرقمي", "تطوير الأعمال"],
    "visible_items": {
        "dashboard": True, "cases": True, "library": True, "clients": True,
        "courses": True, "exams": True, "resources": True,
        "clients_rel": True, "events": True, "publish": True,
        "media": True, "social": True, "analytics": True,
        "foundation": True, "finance": True, "settings": True
    }
}

# ================== إعداد Gemini AI ==================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
client = genai.Client(api_key=GEMINI_API_KEY.strip()) if GEMINI_API_KEY else None

# ================== تهيئة البيانات الأولية ==================
def seed_data():
    if Member.query.first() is None:
        db.session.add_all([
            Member(id=1, name="المستشار محمد", role="المؤسس والمستشار القانوني العام", progress=78, tasks_completed=23, tasks_total=30, status="active", warning=False, last_activity="2026-04-27", avatar_color="#f59e0b", initials="مح"),
            Member(id=2, name="العضو 2", role="مسؤول العلاقات العامة والعملاء", progress=35, tasks_completed=7, tasks_total=20, status="warning", warning=True, last_activity="2026-04-20", avatar_color="#ef4444", initials="ع٢"),
            Member(id=3, name="العضو 3", role="مسؤول الإعلام الرقمي والمحتوى", progress=62, tasks_completed=13, tasks_total=21, status="active", warning=False, last_activity="2026-04-25", avatar_color="#3b82f6", initials="ع٣"),
        ])
    if Milestone.query.first() is None:
        db.session.add_all([
            Milestone(id=1, title="تسجيل الاسم التجاري", description="", done=True, date="2026-01-15"),
            Milestone(id=2, title="إعداد الهوية البصرية والشعار", description="", done=True, date="2026-02-10"),
            Milestone(id=3, title="تأسيس الموقع الإلكتروني الرسمي", description="", done=True, date="2026-03-05"),
            Milestone(id=4, title="توظيف الفريق الأساسي (3 أعضاء)", description="", done=False, date="2026-06-01"),
            Milestone(id=5, title="الحصول على الترخيص النهائي من الهيئة", description="", done=False, date="2026-09-01"),
            Milestone(id=6, title="افتتاح المقر الرسمي للشركة", description="", done=False, date="2026-12-01"),
        ])
    if Case.query.first() is None:
        db.session.add_all([
            Case(id=1, title="قضية أحمد العلي - شراكة تجارية", case_type="تجاري", client="أحمد العلي", status="قيد المراجعة", priority="عالية", date="2026-04-28"),
            Case(id=2, title="قضية سارة محمد - إيجار محل", case_type="عقاري", client="سارة محمد", status="جديدة", priority="متوسطة", date="2026-04-25"),
        ])
    if Task.query.first() is None:
        db.session.add_all([
            Task(id=1, title="مراجعة عقد شركة XYZ", priority="عالية", status="قيد التنفيذ", assignee="المستشار محمد", date="2026-04-28"),
            Task(id=2, title="إعداد مذكرة دفاعية", priority="متوسطة", status="معلق", assignee="العضو 2", date="2026-04-27"),
        ])
    if Client.query.first() is None:
        db.session.add_all([
            Client(id=1, name="شركة الأمل للتجارة", type="شركة", status="نشط", email="info@alamal.com", phone="0501234567", date="2026-04-20"),
            Client(id=2, name="فهد السالم", type="فرد", status="نشط", email="fahad@email.com", phone="0557654321", date="2026-04-18"),
        ])
    if LibraryItem.query.first() is None:
        db.session.add_all([
            LibraryItem(id=1, title="نظام المرافعات الشرعية السعودي", item_type="نظام", category="قوانين", date="2026-04-01"),
            LibraryItem(id=2, title="دليل المحامي الشامل", item_type="كتاب", category="مراجع", date="2026-03-15"),
        ])
    if EventItem.query.first() is None:
        db.session.add_all([
            EventItem(id=1, title="ملتقى المحامين السعوديين", event_type="مؤتمر", date="2026-05-15", location="الرياض"),
        ])
    if PublishItem.query.first() is None:
        db.session.add_all([
            PublishItem(id=1, title="تغريدة توعوية ١", platform="تويتر", status="منشور", date="2026-04-20"),
        ])
    if Book.query.first() is None:
        db.session.add_all([
            Book(id=1, title="القانون التجاري", author="د. أحمد الخليل", category="تجاري", status="متاح", date="2026-04-28"),
            Book(id=2, title="الإجراءات الجزائية", author="د. محمد سعيد", category="جزائي", status="معار", date="2026-04-25"),
        ])
    db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

# ================== دوال مساعدة ==================
def make_list_response(model_cls):
    items = [i.to_dict() for i in model_cls.query.order_by(model_cls.id).all()]
    return {"items": items}

# ================== المسارات الأساسية ==================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('u_name'), request.form.get('u_pass')
    if u == "admin" and p == "123":
        return redirect('/foundation_road')
    return "خطأ في البيانات"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ================== مسارات API للبيانات ==================
@app.route('/api/dashboard_stats')
def api_dashboard_stats():
    completed_tasks = Task.query.filter_by(status="مكتملة").count()
    return jsonify({
        "today_sessions": 4,
        "new_clients": Client.query.count(),
        "completed_tasks_percent": min(100, completed_tasks * 10 + 50),
        "consultations": 7,
        "active_cases": Case.query.count(),
        "pending_docs": 5
    })

@app.route('/api/foundation_data')
def api_foundation_data():
    members = [m.to_dict() for m in Member.query.all()]
    milestones = [m.to_dict() for m in Milestone.query.order_by(Milestone.id).all()]
    return jsonify({
        "team_progress": 40,
        "target_goal": "100 مهمة",
        "target_date": "2026-12-31",
        "members": members,
        "milestones": milestones
    })

@app.route('/api/update_foundation', methods=['POST'])
def api_update_foundation():
    return jsonify({"success": True})

@app.route('/api/clients', methods=['GET', 'POST'])
def api_clients():
    if request.method == 'GET':
        return jsonify(make_list_response(Client))
    data = request.json
    new_item = Client(
        name=data.get("name", ""),
        type=data.get("type", "فرد"),
        status=data.get("status", "نشط"),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/cases', methods=['GET', 'POST'])
def api_cases():
    if request.method == 'GET':
        return jsonify(make_list_response(Case))
    data = request.json
    new_item = Case(
        title=data.get("title", ""),
        case_type=data.get("type", ""),
        client=data.get("client", ""),
        status=data.get("status", "جديدة"),
        priority=data.get("priority", "متوسطة"),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/library', methods=['GET', 'POST'])
def api_library():
    if request.method == 'GET':
        return jsonify(make_list_response(LibraryItem))
    data = request.json
    new_item = LibraryItem(
        title=data.get("title", ""),
        item_type=data.get("type", ""),
        category=data.get("category", ""),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/events', methods=['GET', 'POST'])
def api_events():
    if request.method == 'GET':
        return jsonify(make_list_response(EventItem))
    data = request.json
    new_item = EventItem(
        title=data.get("title", ""),
        event_type=data.get("type", ""),
        date=data.get("date", "2026-04-28"),
        location=data.get("location", "")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/publish', methods=['GET', 'POST'])
def api_publish():
    if request.method == 'GET':
        return jsonify(make_list_response(PublishItem))
    data = request.json
    new_item = PublishItem(
        title=data.get("title", ""),
        platform=data.get("platform", ""),
        status=data.get("status", "مخطط"),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/sidebar_config', methods=['GET', 'POST'])
def api_sidebar_config():
    if request.method == 'GET':
        return jsonify(SIDEBAR_CONFIG)
    return jsonify({"success": True})

@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if request.method == 'GET':
        return jsonify(make_list_response(Task))
    data = request.json
    new_item = Task(
        title=data.get("title", ""),
        priority=data.get("priority", "متوسطة"),
        status=data.get("status", "قيد التنفيذ"),
        assignee=data.get("assignee", ""),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == 'GET':
        return jsonify(make_list_response(Book))
    data = request.json
    new_item = Book(
        title=data.get("title", ""),
        author=data.get("author", ""),
        category=data.get("category", ""),
        status=data.get("status", "متاح"),
        date=data.get("date", "2026-04-28")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"success": True, "item": new_item.to_dict(), "progress": 40})

@app.route('/api/update_member_points', methods=['POST'])
def api_update_member_points():
    return jsonify({"success": True, "progress": 40})

@app.route('/api/ceo_identity')
def api_ceo_identity():
    return jsonify(CEO_IDENTITY)

@app.route('/api/check_ceo', methods=['POST'])
def api_check_ceo():
    data = request.json
    if data.get("username") == "admin" and data.get("password") == "123":
        return jsonify({"is_ceo": True, "identity": CEO_IDENTITY})
    return jsonify({"is_ceo": False})

@app.route('/api/admin/add_member', methods=['POST'])
def api_admin_add_member():
    return jsonify({"success": True})

@app.route('/api/admin/update_milestones', methods=['POST'])
def api_admin_update_milestones():
    return jsonify({"success": True})

@app.route('/api/admin/update_permissions', methods=['POST'])
def api_admin_update_permissions():
    return jsonify({"success": True})

# ================== مسارات الأقسام الفرعية ==================
@app.route('/foundation_road')
def foundation_road():
    return render_template('dashboard.html')

@app.route('/clients')
def clients():
    return render_template('dashboard.html')

@app.route('/library')
def library():
    return render_template('dashboard.html')

@app.route('/events')
def events():
    return render_template('dashboard.html')

@app.route('/publish_plans')
def publish_plans():
    return render_template('dashboard.html')

@app.route('/finance')
def finance():
    return render_template('dashboard.html')

@app.route('/cases')
def cases():
    return render_template('dashboard.html')

@app.route('/media')
def media():
    return render_template('dashboard.html')

@app.route('/business_dev')
def business_dev():
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    return render_template('dashboard.html')

# ================== مسار الذكاء الاصطناعي (المحامي الذكي) ==================
@app.route('/chat')
def chat_page():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_message():
    if not client:
        return jsonify({"reply": "مفتاح Gemini API غير مضبوط. يرجى تعيين متغير GEMINI_API_KEY."}), 503
    data = request.json
    user_message = data.get("message", "")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_message
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"خطأ: {str(e)}"}), 500

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    if not client:
        return jsonify({"reply": "مفتاح Gemini API غير مضبوط."}), 503
    data = request.json
    user_query = data.get("message")
    try:
        prompt = f"""أنت المستشار القانوني الذكي لشركة شاهين للمحاماة والاستشارات القانونية.
أجب المستشار محمد بأسلوب قانوني رسمي ومهني.

السؤال: {user_query}"""
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "حدث خطأ في الاتصال."})

# ================== نقطة الدخول لـ Vercel ==================
# Vercel يبحث عن متغير 'app'
app = app
