import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wazifni_backend.settings')
django.setup()

from users.models import User
from profiles.models import Profile, Experience, Education, Skill, CV
from datetime import date

def create_users():
    # 1. إنشاء Superuser (المسؤول)
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', first_name='Admin', last_name='User')
        print("✅ تم إنشاء حساب المسؤول بنجاح (admin / admin123)")
    else:
        print("ℹ️ حساب المسؤول موجود مسبقاً.")

    # 2. إنشاء Candidate (المستخدم التجريبي)
    username = 'hussam_candidate'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email='hussam@example.com',
            password='password123',
            first_name='حسام',
            last_name='أحمد',
            phone_number='+963900000000',
            address='دمشق، سوريا',
            user_type='candidate'
        )
        print(f"✅ تم إنشاء حساب المستخدم التجريبي بنجاح ({username} / password123)")
        
        # 3. إنشاء الملف الشخصي (Profile)
        profile = Profile.objects.create(
            user=user,
            bio="مطور برمجيات طموح لديه خبرة في بناء تطبيقات الويب باستخدام Django و React. مهتم جداً بتقنيات الذكاء الاصطناعي وتطبيقاتها العملية.",
            portfolio="https://hussam-portfolio.com",
            projects=[
                {
                    "name": "نظام إدارة المهام الذكي",
                    "description": "تطبيق ويب يستخدم الذكاء الاصطناعي لتنظيم المهام اليومية وتحديد الأولويات تلقائياً.",
                    "technologies": ["Django", "React", "OpenAI API"]
                },
                {
                    "name": "تطبيق الطقس المتقدم",
                    "description": "تطبيق يعرض توقعات الطقس بدقة باستخدام خرائط تفاعلية.",
                    "technologies": ["Python", "Flask", "OpenWeatherMap API"]
                }
            ]
        )
        
        # 4. إضافة خبرة (Experience)
        Experience.objects.create(
            profile=profile,
            title="مطور بايثون جونيور",
            company="شركة الحلول الرقمية",
            description="عملت على تطوير الواجهات الخلفية وتحسين أداء الاستعلامات في قاعدة البيانات.",
            start_date=date(2021, 6, 1),
            is_current=True
        )
        
        # 5. إضافة تعليم (Education)
        Education.objects.create(
            profile=profile,
            institution="جامعة دمشق",
            degree="بكالوريوس في هندسة المعلوماتية",
            field_of_study="هندسة البرمجيات",
            start_date=date(2016, 9, 1),
            end_date=date(2021, 5, 30),
            is_current=False
        )
        
        # 6. إضافة مهارات (Skills)
        skills_list = [
            ("Python", "متقدم"),
            ("Django", "متوسط"),
            ("JavaScript", "متوسط"),
            ("React", "مبتدئ"),
            ("SQL", "متقدم")
        ]
        for name, level in skills_list:
            Skill.objects.create(profile=profile, name=name, level=level)
            
        print("✅ تم تعبئة بيانات الملف الشخصي (Profile, Experience, Education, Skills) بنجاح.")
    else:
        print(f"ℹ️ المستخدم التجريبي '{username}' موجود مسبقاً.")

if __name__ == "__main__":
    create_users()
