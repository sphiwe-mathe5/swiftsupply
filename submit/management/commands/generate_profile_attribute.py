from django.core.management.base import BaseCommand
from submit.models import CustomUser

class Command(BaseCommand):
    help = 'Generate profile attributes for all users'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        count = 0
        
        for user in users:
            if not user.color1 or not user.color2 or not user.initials:
                user.generate_profile_attributes()
                user.save()
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated profile attributes for {count} users'))