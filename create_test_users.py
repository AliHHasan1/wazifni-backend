import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wazifni_backend.settings')
django.setup()

from users.models import User
from profiles.models import Profile, Experience, Education, Skill, CV
from datetime import date


def create_users():
    """Create test users including admin, candidate with sample profile data."""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123', first_name='Admin', last_name='User')
        print("Admin account created successfully (admin / admin123)")
    else:
        print("Admin account already exists.")

    username = 'hussam_candidate'
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email='hussam@example.com',
            password='password123',
            first_name='Hussam',
            last_name='Ahmad',
            phone_number='+963900000000',
            address='Damascus, Syria',
            user_type='candidate'
        )
        print(f"Candidate account created successfully ({username} / password123)")

        profile = Profile.objects.create(
            user=user,
            bio="Software developer with experience in building web applications using Django and React.",
            portfolio="https://hussam-portfolio.com",
            projects=[
                {
                    "name": "Smart Task Management System",
                    "description": "Web application using AI to organize daily tasks and prioritize automatically.",
                    "technologies": ["Django", "React", "OpenAI API"]
                },
                {
                    "name": "Advanced Weather Application",
                    "description": "Weather forecast application with interactive maps.",
                    "technologies": ["Python", "Flask", "OpenWeatherMap API"]
                }
            ]
        )

        Experience.objects.create(
            profile=profile,
            title="Junior Python Developer",
            company="Digital Solutions Company",
            description="Worked on backend development and database query optimization.",
            start_date=date(2021, 6, 1),
            is_current=True
        )

        Education.objects.create(
            profile=profile,
            institution="Damascus University",
            degree="Bachelor in Computer Engineering",
            field_of_study="Software Engineering",
            start_date=date(2016, 9, 1),
            end_date=date(2021, 5, 30),
            is_current=False
        )

        skills_list = [
            ("Python", "Advanced"),
            ("Django", "Intermediate"),
            ("JavaScript", "Intermediate"),
            ("React", "Beginner"),
            ("SQL", "Advanced")
        ]
        for name, level in skills_list:
            Skill.objects.create(profile=profile, name=name, level=level)

        print("Profile data created successfully (Profile, Experience, Education, Skills).")
    else:
        print(f"Candidate user '{username}' already exists.")


if __name__ == "__main__":
    create_users()
