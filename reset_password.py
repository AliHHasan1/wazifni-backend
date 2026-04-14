import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wazifni_backend.settings')
django.setup()

from users.models import User


def reset():
    """Reset password for the test candidate user."""
    username = 'hussam_candidate'
    try:
        user = User.objects.get(username=username)
        user.set_password('password123')
        user.save()
        print(f"Password reset successfully for user '{username}'")

        if not user.is_active:
            user.is_active = True
            user.save()
            print(f"User account '{username}' has been activated")

    except User.DoesNotExist:
        print(f"User '{username}' not found.")


if __name__ == "__main__":
    reset()
