"""
نسخة Vercel المبسطة - بدون SQLite و SocketIO
"""
from flask import Flask, render_template, request, jsonify
from google import genai
import os

app = Flask(__name__)

# ================== بيانات في الذاكرة (بدون SQLite) ==================
MEMBERS = [
    {"id": 1, "name": "المستشار محمد", "role": "المؤسس والمستشار القانوني العام", "progress": 78, "tasks_completed": 23, "tasks_total": 30, "status": "active", "warning": False, "last_activity": "2026-04-27", "avatar_color": "#f59e0b", "initials": "مح"},
    {"id": 2, "name": "العضو 2", "role": "مسؤول العلاقات العامة والعملاء", "progress": 35, "tasks_completed": 7, "tasks_total": 20, "status": "warning", "warning": True, "last_activity": "2026-04-20", "avatar_color": "#ef4444", "initials": "ع٢"},
    {"id": 3, "name": "العضو 3", "role": "مسؤول الإعلام الرقمي والمحتوى", "progress": 62, "tasks_completed": 13, "tasks_total": 21, "status": "active", "warning": False, "last_activity": "2026-04-25", "avatar_color": "#3b82f6", "initials": "ع٣"},
]

MILESTONES = [
    {"id": 1, "title": "تسجيل الاسم التجاري", "done": True, "date": "2026-01-15"},
    {"id": 2, "title": "إعداد الهوية البصرية والشعار", "done": True, "date": "2026-02-10"},
    {"id": 3, "title": "تأسيس الموقع الإلكتروني الرسمي", "done": True, "date": "2026-03-05"},
    {"id": 4, "title": "توظيف الفريق الأساسي (3 أعضاء)", "done": False, "date": "2026-06-01"},
    {"id": 5, "title": "الحصول على الترخيص النهائي من الهيئة", "done": False, "date": "2026-09-01"},
    {"id": 6, "title": "افتتاح المقر الرسمي للشركة", "done": False, "date": "2026-12-01"},
]

CASES = [
    {"id": 1, "title": "قضية أحمد العلي - شراكة تجارية", "type": "تجاري", "client": "أحمد العلي", "status": "قيد المراجعة", "priority": "عالية", "date": "2026-04-28"},
    {"id": 2, "title": "قضية سارة محمد - إيجار محل", "type": "عقاري", "client": "سارة محمد", "status": "جديدة", "priority": "متوسطة", "date": "2026-04-25"},
]

TASKS = [
    {"id": 1, "title": "مراجعة عقد شركة XYZ", "priority": "عالية", "status": "قيد التنفيذ", "assignee": "المستشار محمد", "date": "2026-04-28"},
    {"id": 2, "title": "إعداد مذكرة دفاعية", "priority": "متوسطة", "status": "معلق", "assignee": "العضو 2", "date": "2026-04-27"},
]

CLIENTS = [
    {"id": 1, "name": "شركة الأمل للتجارة", "type": "شركة", "status": "نشط", "email": "info@alamal.com", "phone": "0501234567", "date": "2026-04-20"},
    {"id": 2, "name": "فهد السالم", "type": "فرد", "status": "نشط", "email": "fahad@email.com", "phone": "0557654321", "date": "2026-04-18"},
]

LIBRARY = [
    {"id": 1, "title": "نظام المرافعات الشرعية السعودي", "type": "نظام", "category": "قوانين", "date": "2026-04-01"},
    {"id": 2, "title": "دليل المحامي الشامل", "type": "كتاب", "category": "مراجع", "date": "2026-03-15"},
]

EVENTS = [
    {"id": 1, "title": "ملتقى المحامين السعوديين", "type": "مؤتمر", "date": "2026-05-15", "location": "الرياض"},
]

PUBLISH = [
    {"id": 1, "title": "تغريدة توعوية ١", "platform": "تويتر", "status": "منشور", "date": "2026-04-20"},
]

BOOKS = [
    {"id": 1, "title": "القانون التجاري", "author": "د. أحمد الخليل", "category": "تجاري", "status": "متاح", "date": "2026-04-28"},
    {"id": 2, "title": "الإجراءات الجزائية", "author": "د. محمد سعيد", "category": "جزائي", "status": "معار", "date": "2026-04-25"},
]

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
    completed_tasks = sum(1 for t in TASKS if t["status"] == "مكتملة")
    return jsonify({
        "today_sessions": 4,
        "new_clients": len(CLIENTS),
        "completed_tasks_percent": min(100, completed_tasks * 10 + 50),
        "consultations": 7,
        "active_cases": len(CASES),
        "pending_docs": 5
    })

@app.route('/api/foundation_data')
def api_foundation_data():
    return jsonify({
        "team_progress": 40,
        "target_goal": "100 مهمة",
        "target_date": "2026-12-31",
        "members": MEMBERS,
        "milestones": MILESTONES
    })

@app.route('/api/update_foundation', methods=['POST'])
def api_update_foundation():
    return jsonify({"success": True})

@app.route('/api/clients', methods=['GET', 'POST'])
def api_clients():
    if request.method == 'GET':
        return jsonify({"items": CLIENTS})
    data = request.json
    new_item = {
        "id": len(CLIENTS) + 1,
        "name": data.get("name", ""),
        "type": data.get("type", "فرد"),
        "status": data.get("status", "نشط"),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "date": data.get("date", "2026-04-28")
    }
    CLIENTS.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/cases', methods=['GET', 'POST'])
def api_cases():
    if request.method == 'GET':
        return jsonify({"items": CASES})
    data = request.json
    new_item = {
        "id": len(CASES) + 1,
        "title": data.get("title", ""),
        "type": data.get("type", ""),
        "client": data.get("client", ""),
        "status": data.get("status", "جديدة"),
        "priority": data.get("priority", "متوسطة"),
        "date": data.get("date", "2026-04-28")
    }
    CASES.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/library', methods=['GET', 'POST'])
def api_library():
    if request.method == 'GET':
        return jsonify({"items": LIBRARY})
    data = request.json
    new_item = {
        "id": len(LIBRARY) + 1,
        "title": data.get("title", ""),
        "type": data.get("type", ""),
        "category": data.get("category", ""),
        "date": data.get("date", "2026-04-28")
    }
    LIBRARY.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/events', methods=['GET', 'POST'])
def api_events():
    if request.method == 'GET':
        return jsonify({"items": EVENTS})
    data = request.json
    new_item = {
        "id": len(EVENTS) + 1,
        "title": data.get("title", ""),
        "type": data.get("type", ""),
        "date": data.get("date", "2026-04-28"),
        "location": data.get("location", "")
    }
    EVENTS.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/publish', methods=['GET', 'POST'])
def api_publish():
    if request.method == 'GET':
        return jsonify({"items": PUBLISH})
    data = request.json
    new_item = {
        "id": len(PUBLISH) + 1,
        "title": data.get("title", ""),
        "platform": data.get("platform", ""),
        "status": data.get("status", "مخطط"),
        "date": data.get("date", "2026-04-28")
    }
    PUBLISH.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/sidebar_config', methods=['GET', 'POST'])
def api_sidebar_config():
    if request.method == 'GET':
        return jsonify(SIDEBAR_CONFIG)
    return jsonify({"success": True})

@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if request.method == 'GET':
        return jsonify({"items": TASKS})
    data = request.json
    new_item = {
        "id": len(TASKS) + 1,
        "title": data.get("title", ""),
        "priority": data.get("priority", "متوسطة"),
        "status": data.get("status", "قيد التنفيذ"),
        "assignee": data.get("assignee", ""),
        "date": data.get("date", "2026-04-28")
    }
    TASKS.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == 'GET':
        return jsonify({"items": BOOKS})
    data = request.json
    new_item = {
        "id": len(BOOKS) + 1,
        "title": data.get("title", ""),
        "author": data.get("author", ""),
        "category": data.get("category", ""),
        "status": data.get("status", "متاح"),
        "date": data.get("date", "2026-04-28")
    }
    BOOKS.append(new_item)
    return jsonify({"success": True, "item": new_item, "progress": 40})

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
