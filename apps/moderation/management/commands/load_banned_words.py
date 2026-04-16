from django.core.management.base import BaseCommand

from apps.moderation.models import BannedWord

# Lista base de palabras prohibidas en español
# El admin puede agregar más desde el panel
BANNED_WORDS = [
    # Grooming/Pedofilia - severidad: ban automático
    ('nudes', 'grooming', 'ban'),
    ('pack', 'grooming', 'ban'),
    ('cp', 'grooming', 'ban'),
    ('menor de edad', 'grooming', 'ban'),
    ('desnuda', 'grooming', 'ban'),
    ('desnudo', 'grooming', 'ban'),
    ('foto intima', 'grooming', 'ban'),
    ('fotos intimas', 'grooming', 'ban'),

    # Contenido sexual - severidad: bloquear
    ('porno', 'sexual', 'block'),
    ('sexo', 'sexual', 'block'),
    ('puta', 'sexual', 'block'),
    ('puto', 'sexual', 'block'),
    ('coger', 'sexual', 'block'),
    ('verga', 'sexual', 'block'),
    ('pene', 'sexual', 'block'),
    ('vagina', 'sexual', 'block'),
    ('tetas', 'sexual', 'block'),
    ('culo', 'sexual', 'block'),
    ('prostituta', 'sexual', 'block'),
    ('orgasmo', 'sexual', 'block'),
    ('masturb', 'sexual', 'block'),
    ('xxx', 'sexual', 'block'),
    ('onlyfans', 'sexual', 'block'),

    # Insultos - severidad: advertencia
    ('idiota', 'insult', 'warn'),
    ('estupido', 'insult', 'warn'),
    ('estupida', 'insult', 'warn'),
    ('imbecil', 'insult', 'warn'),
    ('pendejo', 'insult', 'warn'),
    ('pendeja', 'insult', 'warn'),
    ('mierda', 'insult', 'warn'),
    ('cabron', 'insult', 'warn'),
    ('cabrona', 'insult', 'warn'),
    ('boludo', 'insult', 'warn'),
    ('boluda', 'insult', 'warn'),
    ('huevon', 'insult', 'warn'),
    ('huevona', 'insult', 'warn'),
    ('cojudo', 'insult', 'warn'),
    ('maricon', 'insult', 'block'),
    ('marica', 'insult', 'block'),

    # Violencia - severidad: bloquear
    ('matar', 'violence', 'block'),
    ('asesinar', 'violence', 'block'),
    ('suicid', 'violence', 'block'),
    ('violar', 'violence', 'block'),
    ('violacion', 'violence', 'block'),
    ('golpear', 'violence', 'warn'),

    # Drogas - severidad: bloquear
    ('marihuana', 'drugs', 'block'),
    ('cocaina', 'drugs', 'block'),
    ('droga', 'drugs', 'block'),
    ('heroina', 'drugs', 'block'),
    ('metanfetamina', 'drugs', 'block'),
]


class Command(BaseCommand):
    help = 'Carga las palabras prohibidas iniciales para moderación'

    def handle(self, *args, **options):
        created_count = 0
        for word, category, severity in BANNED_WORDS:
            _, created = BannedWord.objects.get_or_create(
                word=word,
                defaults={'category': category, 'severity': severity},
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Se cargaron {created_count} palabras prohibidas '
                f'({BannedWord.objects.count()} total).'
            )
        )
