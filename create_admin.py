import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intelligence.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='titus',
            email='titus.asaph18@gmail.com',
            password='intelligence18'  # À modifier impérativement
        )
        print("Superuser créé avec succès !")
    else:
        print("Un superuser existe déjà")

if __name__ == '__main__':
    create_admin()
