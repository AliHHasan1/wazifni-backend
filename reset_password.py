import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wazifni_backend.settings')
django.setup()

from users.models import User

def reset():
    username = 'hussam_candidate'
    try:
        user = User.objects.get(username=username)
        user.set_password('password123')
        user.save()
        print(f"✅ تم إعادة تعيين كلمة مرور المستخدم '{username}' بنجاح إلى 'password123'")
        
        # التأكد من أن الحساب نشط
        if not user.is_active:
            user.is_active = True
            user.save()
            print(f"✅ تم تفعيل حساب المستخدم '{username}'")
            
    except User.DoesNotExist:
        print(f"❌ المستخدم '{username}' غير موجود.")

if __name__ == "__main__":
    reset()
