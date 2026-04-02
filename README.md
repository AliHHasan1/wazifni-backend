# مشروع "وظفني" - الواجهة الخلفية (Backend)

هذا المستودع يحتوي على الواجهة الخلفية لمشروع "وظفني"، مبني باستخدام Django و Django REST Framework (DRF)، مع تكامل الذكاء الاصطناعي (Google Gemini) لتطوير السير الذاتية وتوليد ملفات PDF.

## الهيكلية

```
wazifni_backend/
├── wazifni_backend/    # إعدادات المشروع الأساسية (settings.py, urls.py)
├── users/              # تطبيق إدارة المستخدمين والصلاحيات
├── profiles/           # تطبيق إدارة السير الذاتية والذكاء الاصطناعي
├── jobs/               # تطبيق إدارة الوظائف والتقديم عليها
├── services/           # طبقة الخدمات (AI, PDF)
│   ├── ai_service.py   # كود التعامل مع Gemini API
│   └── pdf_service.py  # كود التعامل مع WeasyPrint
├── .env                # ملف سري لمفاتيح الـ API وقاعدة البيانات
├── requirements.txt    # قائمة المكتبات المستخدمة
└── manage.py
```

## الإعداد والتشغيل

اتبع الخطوات التالية لإعداد وتشغيل المشروع:

### 1. استنساخ المستودع (Clone the repository)

```bash
git clone <your-repository-url>
cd wazifni_backend
```

### 2. إعداد البيئة الافتراضية (Virtual Environment)

```bash
python3.11 -m venv venv
source venv/bin/activate  # لنظام Linux/macOS
# venv\Scripts\activate   # لنظام Windows
```

### 3. تثبيت المتطلبات (Install Dependencies)

```bash
pip install -r requirements.txt
```

### 4. إعداد ملف المتغيرات البيئية (.env)

قم بإنشاء ملف `.env` في المجلد الرئيسي للمشروع (`wazifni_backend/`) وأضف المتغيرات التالية:

```dotenv
SECRET_KEY="YOUR_DJANGO_SECRET_KEY_HERE" # قم بتوليد مفتاح سري قوي
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY_HERE"
```

**ملاحظة:** للحصول على `GEMINI_API_KEY`، قم بزيارة [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. تطبيق الهجرات (Apply Migrations)

```bash
python3.11 manage.py makemigrations
python3.11 manage.py migrate
```

### 6. إنشاء مستخدم مشرف (Create Superuser)

```bash
python3.11 manage.py createsuperuser
```

### 7. تشغيل الخادم (Run the Server)

```bash
python3.11 manage.py runserver
```

سيتم تشغيل الخادم على `http://127.0.0.1:8000/`.

## نقاط نهاية الـ API (API Endpoints)

يمكنك الوصول إلى نقاط نهاية الـ API عبر `http://127.0.0.1:8000/api/`.

### المستخدمون (Users)

*   **التسجيل:** `POST /api/users/register/`
    *   **البيانات:** `username`, `email`, `password`, `first_name`, `last_name`, `user_type` (candidate/organization)
*   **إنشاء منظمة:** `POST /api/users/organization/create/`
    *   **البيانات:** `name`, `description`, `location` (يتطلب مصادقة المستخدم كـ `organization`)

### الملفات الشخصية (Profiles)

*   **إدارة الملف الشخصي:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/profiles/profiles/`
*   **إدارة الخبرات:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/profiles/experiences/`
    *   **نقطة نهاية تحسين الوصف بالذكاء الاصطناعي:** `POST /api/profiles/experiences/{id}/enhance_description/`
*   **إدارة التعليم:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/profiles/education/`
*   **إدارة المهارات:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/profiles/skills/`

### الوظائف (Jobs)

*   **إدارة الوظائف:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/jobs/jobs/`
*   **إدارة طلبات التقديم:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE` على `/api/jobs/applications/`

## التوثيق الإضافي

*   **Django REST Framework Browsable API:** يمكنك استعراض نقاط النهاية واختبارها مباشرة من المتصفح عبر `http://127.0.0.1:8000/api/`.
*   **Postman Collection:** يوصى بإنشاء Postman Collection لتوثيق واختبار الـ APIs بشكل فعال.

## ملاحظات هامة

*   **الأمان:** تأكد من استخدام مفتاح سري قوي في ملف `.env` الخاص بالإنتاج.
*   **قاعدة البيانات:** المشروع يستخدم SQLite افتراضياً. يوصى بالتبديل إلى PostgreSQL للإنتاج.
*   **تكامل Gemini:** تأكد من أن `GEMINI_API_KEY` صحيح ويعمل بشكل سليم.

بالتوفيق في مشروعك الجامعي! هذا الأساس سيمكنك من بناء واجهة خلفية قوية ومبهرة. إذا واجهت أي مشاكل، لا تتردد في السؤال.
