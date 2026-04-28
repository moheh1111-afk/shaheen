from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, send
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shaheen_secret'

# إعداد SocketIO للمحادثات الجماعية
socketio = SocketIO(app, cors_allowed_origins="*")

# ================== قاعدة البيانات التجريبية ==================
USER_DATABASE = {"username": "admin", "password": "123", "role": "ceo"}

# ================== هوية المؤسس ==================
CEO_IDENTITY = {
    "name": "المحامي محمد إحسان الشواف",
    "title": "المؤسس والمدير التنفيذي",
    "role_en": "CEO",
    "initials": "مح",
    "avatar_color": "#d97706"
}

# ================== بيانات لوحة التحكم الرئيسية ==================
DASHBOARD_STATS = {
    "today_sessions": 4,
    "new_clients": 12,
    "completed_tasks_percent": 85,
    "consultations": 7,
    "active_cases": 23,
    "pending_docs": 5
}

# ================== بيانات طريق التأسيس (Admin Dashboard) ==================
# هذه المتغيرات يمكن للأدمن تعديلها بسهولة
FOUNDATION_DATA = {
    "team_progress": 65,
    "target_goal": "فتح شركة شاهين للمحاماة والاستشارات القانونية رسمياً",
    "target_date": "2026-12-31",
    "milestones": [
        {"id": 1, "title": "تسجيل الاسم التجاري", "done": True, "date": "2026-01-15"},
        {"id": 2, "title": "إعداد الهوية البصرية والشعار", "done": True, "date": "2026-02-10"},
        {"id": 3, "title": "تأسيس الموقع الإلكتروني الرسمي", "done": True, "date": "2026-03-05"},
        {"id": 4, "title": "توظيف الفريق الأساسي (3 أعضاء)", "done": False, "date": "2026-06-01"},
        {"id": 5, "title": "الحصول على الترخيص النهائي من الهيئة", "done": False, "date": "2026-09-01"},
        {"id": 6, "title": "افتتاح المقر الرسمي للشركة", "done": False, "date": "2026-12-01"}
    ],
    "members": [
        {
            "id": 1,
            "name": "المستشار محمد",
            "role": "المؤسس والمستشار القانوني العام",
            "progress": 78,
            "tasks_completed": 23,
            "tasks_total": 30,
            "status": "active",
            "warning": False,
            "last_activity": "2026-04-27",
            "avatar_color": "#f59e0b",
            "initials": "مح"
        },
        {
            "id": 2,
            "name": "العضو 2",
            "role": "مسؤول العلاقات العامة والعملاء",
            "progress": 35,
            "tasks_completed": 7,
            "tasks_total": 20,
            "status": "warning",
            "warning": True,
            "last_activity": "2026-04-20",
            "avatar_color": "#ef4444",
            "initials": "ع٢"
        },
        {
            "id": 3,
            "name": "العضو 3",
            "role": "مسؤول الإعلام الرقمي والمحتوى",
            "progress": 62,
            "tasks_completed": 13,
            "tasks_total": 21,
            "status": "active",
            "warning": False,
            "last_activity": "2026-04-25",
            "avatar_color": "#3b82f6",
            "initials": "ع٣"
        }
    ]
}

# ================== إعداد Gemini AI ==================
# ==========================================
# 🔑 منطقة مفتاح الذكاء الاصطناعي - لا تعدل يدوياً
# ==========================================
GOOGLE_API_KEY = "AIzaSyAK-MX4oF0fLWPPw4ZRuMHpll4qxD-6os4"
genai.configure(api_key=GOOGLE_API_KEY)

# ================== متاجر البيانات الديناميكية ==================
# العملاء
CLIENTS_DATA = {
    "items": [
        {"id": 1, "name": "أحمد العلي", "type": "شركة", "status": "نشط", "date": "2026-04-10"},
        {"id": 2, "name": "سارة محمد", "type": "فرد", "status": "معلق", "date": "2026-04-15"},
    ],
    "next_id": 3
}

# القضايا
CASES_DATA = {
    "items": [
        {"id": 1, "title": "قضية تجارية ١٢٣", "client": "أحمد العلي", "status": "جارية", "priority": "عالية", "date": "2026-04-01"},
        {"id": 2, "title": "دعوى مدنية ٤٥٦", "client": "سارة محمد", "status": "معلقة", "priority": "متوسطة", "date": "2026-04-05"},
    ],
    "next_id": 3
}

# المكتبة
LIBRARY_DATA = {
    "items": [
        {"id": 1, "title": "نظام المرافعات الشرعية", "type": "نظام", "category": "إجرائي", "date": "2026-04-01"},
        {"id": 2, "title": "نظام الشركات", "type": "نظام", "category": "تجاري", "date": "2026-04-02"},
    ],
    "next_id": 3
}

# المناسبات
EVENTS_DATA = {
    "items": [
        {"id": 1, "title": "ندوة القانون التجاري", "type": "ندوة", "date": "2026-05-15", "location": "الرياض"},
        {"id": 2, "title": "ورشة صياغة العقود", "type": "ورشة", "date": "2026-06-01", "location": "جدة"},
    ],
    "next_id": 3
}

# تخطيط النشر
PUBLISH_DATA = {
    "items": [
        {"id": 1, "title": "تغريدة توعوية ١", "platform": "تويتر", "status": "منشور", "date": "2026-04-20"},
        {"id": 2, "title": "مقال قانوني ٢", "platform": "لينكدإن", "status": "مخطط", "date": "2026-04-25"},
    ],
    "next_id": 3
}

# المهام
TASKS_DATA = {
    "items": [
        {"id": 1, "title": "مراجعة عقد شركة XYZ", "priority": "عالية", "status": "قيد التنفيذ", "assignee": "المستشار محمد", "date": "2026-04-28"},
        {"id": 2, "title": "إعداد مذكرة دفاعية", "priority": "متوسطة", "status": "معلقة", "assignee": "العضو 2", "date": "2026-04-27"},
    ],
    "next_id": 3
}

# الكتب والمراجع
BOOKS_DATA = {
    "items": [
        {"id": 1, "title": "الوجيز في شرح القانون المدني", "author": "د. عبدالرزاق السنهوري", "category": "قانون مدني", "status": "متاح"},
        {"id": 2, "title": "النظام القانوني للشركات", "author": "د. محمد فؤاد", "category": "قانون تجاري", "status": "مُعار"},
    ],
    "next_id": 3
}

# إعدادات الشريط الجانبي (افتراضي)
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

# ================== المسارات الأساسية ==================

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    u, p = request.form.get('u_name'), request.form.get('u_pass')
    if u == USER_DATABASE["username"] and p == USER_DATABASE["password"]:
        return redirect('/foundation_road')
    return "خطأ في البيانات"

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ================== مسارات API للبيانات ==================

def recalc_foundation_progress():
    """إعادة حساب نسبة تقدم التأسيس تلقائياً بناءً على حجم البيانات المُدخلة"""
    total_items = len(CLIENTS_DATA["items"]) + len(CASES_DATA["items"]) + len(LIBRARY_DATA["items"]) + len(EVENTS_DATA["items"]) + len(PUBLISH_DATA["items"])
    # كل 10 عناصر = 5% تقدم إضافي، حتى 100%
    bonus = min(35, (total_items * 0.5))
    # الأساس: إنجاز المعالم + إنجاز الأعضاء + العناصر المُدخلة
    ms_done = sum(1 for m in FOUNDATION_DATA["milestones"] if m["done"])
    ms_pct = (ms_done / len(FOUNDATION_DATA["milestones"])) * 30 if FOUNDATION_DATA["milestones"] else 0
    members_avg = sum(m["progress"] for m in FOUNDATION_DATA["members"]) / len(FOUNDATION_DATA["members"]) * 0.35 if FOUNDATION_DATA["members"] else 0
    new_progress = min(100, round(ms_pct + members_avg + bonus))
    FOUNDATION_DATA["team_progress"] = new_progress
    return new_progress

@app.route('/api/dashboard_stats')
def api_dashboard_stats():
    return jsonify(DASHBOARD_STATS)

@app.route('/api/foundation_data')
def api_foundation_data():
    recalc_foundation_progress()
    return jsonify(FOUNDATION_DATA)

@app.route('/api/update_foundation', methods=['POST'])
def api_update_foundation():
    data = request.json
    if "team_progress" in data:
        FOUNDATION_DATA["team_progress"] = data["team_progress"]
    if "target_goal" in data:
        FOUNDATION_DATA["target_goal"] = data["target_goal"]
    if "target_date" in data:
        FOUNDATION_DATA["target_date"] = data["target_date"]
    if "members" in data:
        FOUNDATION_DATA["members"] = data["members"]
    if "milestones" in data:
        FOUNDATION_DATA["milestones"] = data["milestones"]
    return jsonify({"success": True, "data": FOUNDATION_DATA})

# ----- العملاء -----
@app.route('/api/clients', methods=['GET', 'POST'])
def api_clients():
    if request.method == 'GET':
        return jsonify(CLIENTS_DATA)
    data = request.json
    new_item = {"id": CLIENTS_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    CLIENTS_DATA["items"].append(new_item)
    CLIENTS_DATA["next_id"] += 1
    DASHBOARD_STATS["new_clients"] = len(CLIENTS_DATA["items"])
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- القضايا -----
@app.route('/api/cases', methods=['GET', 'POST'])
def api_cases():
    if request.method == 'GET':
        return jsonify(CASES_DATA)
    data = request.json
    new_item = {"id": CASES_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    CASES_DATA["items"].append(new_item)
    CASES_DATA["next_id"] += 1
    DASHBOARD_STATS["active_cases"] = len(CASES_DATA["items"])
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- المكتبة -----
@app.route('/api/library', methods=['GET', 'POST'])
def api_library():
    if request.method == 'GET':
        return jsonify(LIBRARY_DATA)
    data = request.json
    new_item = {"id": LIBRARY_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    LIBRARY_DATA["items"].append(new_item)
    LIBRARY_DATA["next_id"] += 1
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- المناسبات -----
@app.route('/api/events', methods=['GET', 'POST'])
def api_events():
    if request.method == 'GET':
        return jsonify(EVENTS_DATA)
    data = request.json
    new_item = {"id": EVENTS_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    EVENTS_DATA["items"].append(new_item)
    EVENTS_DATA["next_id"] += 1
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- خطط النشر -----
@app.route('/api/publish', methods=['GET', 'POST'])
def api_publish():
    if request.method == 'GET':
        return jsonify(PUBLISH_DATA)
    data = request.json
    new_item = {"id": PUBLISH_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    PUBLISH_DATA["items"].append(new_item)
    PUBLISH_DATA["next_id"] += 1
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- إعدادات الشريط الجانبي -----
@app.route('/api/sidebar_config', methods=['GET', 'POST'])
def api_sidebar_config():
    if request.method == 'GET':
        return jsonify(SIDEBAR_CONFIG)
    data = request.json
    if "groups_order" in data:
        SIDEBAR_CONFIG["groups_order"] = data["groups_order"]
    if "visible_items" in data:
        SIDEBAR_CONFIG["visible_items"].update(data["visible_items"])
    return jsonify({"success": True, "config": SIDEBAR_CONFIG})

# ----- المهام -----
@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if request.method == 'GET':
        return jsonify(TASKS_DATA)
    data = request.json
    new_item = {"id": TASKS_DATA["next_id"], **data, "date": data.get("date", "2026-04-28")}
    TASKS_DATA["items"].append(new_item)
    TASKS_DATA["next_id"] += 1
    DASHBOARD_STATS["completed_tasks_percent"] = min(100, len([t for t in TASKS_DATA["items"] if t["status"] == "مكتملة"]) * 10 + 50)
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- الكتب -----
@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == 'GET':
        return jsonify(BOOKS_DATA)
    data = request.json
    new_item = {"id": BOOKS_DATA["next_id"], **data, "status": data.get("status", "متاح")}
    BOOKS_DATA["items"].append(new_item)
    BOOKS_DATA["next_id"] += 1
    recalc_foundation_progress()
    return jsonify({"success": True, "item": new_item, "progress": FOUNDATION_DATA["team_progress"]})

# ----- تحديث نقاط العضو -----
@app.route('/api/update_member_points', methods=['POST'])
def api_update_member_points():
    data = request.json
    member_id = data.get("member_id")
    delta = data.get("delta", 0)
    for m in FOUNDATION_DATA["members"]:
        if m["id"] == member_id:
            m["progress"] = max(0, min(100, m["progress"] + delta))
            m["tasks_completed"] = max(0, m["tasks_completed"] + (1 if delta > 0 else -1))
            m["warning"] = m["progress"] < 40
            recalc_foundation_progress()
            return jsonify({"success": True, "member": m, "progress": FOUNDATION_DATA["team_progress"]})
    return jsonify({"success": False, "error": "Member not found"}), 404

# ----- معلومات المؤسس / CEO -----
@app.route('/api/ceo_identity')
def api_ceo_identity():
    return jsonify(CEO_IDENTITY)

@app.route('/api/check_ceo', methods=['POST'])
def api_check_ceo():
    data = request.json
    u = data.get("username")
    p = data.get("password")
    if u == USER_DATABASE["username"] and p == USER_DATABASE["password"] and USER_DATABASE.get("role") == "ceo":
        return jsonify({"is_ceo": True, "identity": CEO_IDENTITY})
    return jsonify({"is_ceo": False})

# ================== APIs إدارة النظام (Admin) ==================
@app.route('/api/admin/add_member', methods=['POST'])
def api_admin_add_member():
    data = request.json
    new_id = max([m["id"] for m in FOUNDATION_DATA["members"]], default=0) + 1
    new_member = {
        "id": new_id,
        "name": data.get("name", "عضو جديد"),
        "role": data.get("role", "محامي"),
        "progress": 0,
        "tasks_completed": 0,
        "tasks_total": 0,
        "status": "active",
        "warning": False,
        "last_activity": "2026-04-28",
        "avatar_color": data.get("avatar_color", "#64748b"),
        "initials": data.get("initials", "؟")
    }
    FOUNDATION_DATA["members"].append(new_member)
    recalc_foundation_progress()
    return jsonify({"success": True, "member": new_member, "progress": FOUNDATION_DATA["team_progress"]})

@app.route('/api/admin/update_milestones', methods=['POST'])
def api_admin_update_milestones():
    data = request.json
    if "milestones" in data:
        FOUNDATION_DATA["milestones"] = data["milestones"]
    if "target_goal" in data:
        FOUNDATION_DATA["target_goal"] = data["target_goal"]
    if "target_date" in data:
        FOUNDATION_DATA["target_date"] = data["target_date"]
    recalc_foundation_progress()
    return jsonify({"success": True, "data": FOUNDATION_DATA})

@app.route('/api/admin/update_permissions', methods=['POST'])
def api_admin_update_permissions():
    data = request.json
    if "visible_items" in data:
        SIDEBAR_CONFIG["visible_items"].update(data["visible_items"])
    return jsonify({"success": True, "config": SIDEBAR_CONFIG})

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

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    user_query = data.get("message")
    try:
        prompt = f"""أنت المستشار القانوني الذكي لشركة شاهين للمحاماة والاستشارات القانونية.
أجب المستشار محمد بأسلوب قانوني رسمي ومهني، مستخدماً المصطلحات القانونية العربية الفصحى والمرجعيات التشريعية السعودية والخليجية عند الحاجة.

التعليمات:
- ابدأ بتحية قانونية مختصرة (مثل: "بسم الله الرحمن الرحيم" أو "تحية قانونية طيبة")
- قدّم الإجابة بشكل منظم ومفصل باستخدام فقرات واضحة
- استخدم المرجعيات النظامية السعودية (نظام المرافعات، نظام التنفيذ، نظام الشركات، لائحة حماية العملاء...) عند الاقتضاء
- في نهاية الرد، اذكر إخلاء المسؤولية القانونية بأن الرد استشاري ولا يغني عن مراجعة محامٍ مختص

السؤال: {user_query}"""
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "نظام الذكاء الاصطناعي يحتاج لمفتاح API صحيح."})

# ================== محرك الدردشة الجماعية (SocketIO) ==================

@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

# ================== تشغيل التطبيق ==================

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5050)