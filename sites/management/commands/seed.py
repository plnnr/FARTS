from django.core.management.base import BaseCommand
from sites.models import BaseZone, BaseZoneClass, District
from django.db import transaction # to roll back db changes in event of error

# https://stackoverflow.com/questions/51577441/how-to-seed-django-project-insert-a-bunch-of-data-into-the-project-for-initi

DEFAULT_BASE_ZONES = [
    'CE', 'CM1', 'CM2', 'CM3', 'CR', 'CX', 'R1', 'R2', 'R3', 
    'RH', 'RMP', 'RX', 'RM1', 'RM2', 'RM3', 'RM4',
]

DEFAULT_BASE_ZONE_CLASSES = [
    'MUZ', 'MDZ',
]

DEFAULT_DISTRICTS = [
    (2, 'Central City Plan District'), 
    (2, 'Central City/South Auditorium Plan District'),
    (2, 'Johnson Creek Plan District'),
    (1, 'Eliot Conservation District'),
    (1, 'Mississippi Conservation District'),
    (1, 'Russell Conservation District'),
    (1, 'Kenton Conservation District'),
    (1, 'Woodlawn Conservation District'),
    (1, 'Piedmont Conservation District'),
    (0, '13th Avenue Historic District'),
    (0, 'Alphabet Historic District'),
    (0, 'East Portland / Grand Avenue Historic District'),
    (0, 'Halprin Open Space Sequence Historic District'),
    (0, 'Irvington Historic District'),
    (0, 'Kenton Commercial Historic District'),
    (0, 'King\'s Hill Historic District'),
    (0, 'Ladd\'s Addition Historic District'),
    (0, 'Mount Tabor Park Historic District'),
    (0, 'Mount Tabor Park Reservoirs Historic District'),
    (0, 'New Chinatown / Japantown Historic District'),
    (0, 'Peacock Lane Historic District'),
    (0, 'Rocky Butte Scenic Drive Historic District'),
    (0, 'Skidmore / Old Town Historic District'),
    (0, 'South Portland Historic District'),
    (0, 'Washington Park Reservoirs Historic District'),
    (0, 'Willamette National Cemetery Historic District'),
    (0, 'Yamhill Historic District'),
]

class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
       self.stdout.write("Seeding database...")
       seed_db()
       self.stdout.write("Database successfully seeded! GOOD JOB.")


def seed_base_zones():
    for zone in DEFAULT_BASE_ZONES:
        BaseZone.objects.get_or_create(name=zone)

def seed_base_zone_classes():
    for zone_class in DEFAULT_BASE_ZONE_CLASSES:
        BaseZoneClass.objects.get_or_create(name=zone_class)

def seed_districts():
    for code, district in DEFAULT_DISTRICTS:
        District.objects.get_or_create(type=code, name=district)

@transaction.atomic
def seed_db():
    seed_base_zones()
    seed_base_zone_classes()
    seed_districts()

