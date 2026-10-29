from django.db import migrations


def seed_job_categories(apps, schema_editor):
    JobCategory = apps.get_model('jobs', 'JobCategory')
    categories = [
        ('Tecnologia', 'bi-cpu', 1),
        ('Marketing y Ventas', 'bi-megaphone', 2),
        ('Finanzas y Contabilidad', 'bi-cash-stack', 3),
        ('Diseno y Creatividad', 'bi-palette', 4),
        ('Administracion y RRHH', 'bi-building', 5),
        ('Educacion', 'bi-book', 6),
        ('Salud', 'bi-heart-pulse', 7),
        ('Construccion y Oficios', 'bi-tools', 8),
        ('Gastronomia y Hospitalidad', 'bi-cup-hot', 9),
        ('Comunicacion y Medios', 'bi-broadcast', 10),
        ('Legal', 'bi-briefcase', 11),
        ('Otro', 'bi-three-dots', 12),
    ]
    for name, icon, order in categories:
        JobCategory.objects.create(name=name, icon=icon, order=order)


def seed_tip_categories(apps, schema_editor):
    TipCategory = apps.get_model('jobs', 'TipCategory')

    parents = {
        'Tecnologia': ('Desarrollo Web', 'Ciencia de Datos', 'Soporte IT', 'Diseno UX/UI'),
        'Negocios': ('Emprendimiento', 'Administracion', 'Liderazgo'),
        'Idiomas': ('Ingles', 'Portugues', 'Otro idioma'),
        'Desarrollo Personal': ('Entrevistas de trabajo', 'Curriculum / CV', 'Networking'),
        'Habilidades Digitales': ('Excel y Office', 'Marketing Digital', 'Redes Sociales'),
    }

    order = 1
    for parent_name, children in parents.items():
        parent = TipCategory.objects.create(name=parent_name, parent=None, order=order)
        order += 1
        child_order = 1
        for child_name in children:
            TipCategory.objects.create(name=child_name, parent=parent, order=child_order)
            child_order += 1


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_job_categories, migrations.RunPython.noop),
        migrations.RunPython(seed_tip_categories, migrations.RunPython.noop),
    ]
