"""
Management command to seed the database with realistic demo data.

Usage:
    python manage.py seed_demo_data          # Create demo data (idempotent)
    python manage.py seed_demo_data --flush   # Delete demo data and recreate
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import User, UserLanguage
from apps.chat.models import Conversation, Message
from apps.events.models import Event, RSVP
from apps.groups.models import (
    Group, GroupMembership, GroupPost, Proposal, ProposalParticipant,
)
from apps.jobs.models import (
    CareerTip, JobCategory, JobPosting, ProfessionalProfile, TipCategory,
)
from apps.posts.models import Comment, Hashtag, Post, PostHashtag, Reaction
from apps.profiles.models import Story, StoryHighlight, StoryHighlightItem
from apps.social.models import Follow, FriendRequest, Friendship


DEMO_DOMAIN = 'demo.iddam.app'
DEMO_PASSWORD = 'demo1234!'

# ── User definitions ──────────────────────────────────────────────────────────

USERS_DATA = [
    # Hispanohablantes
    dict(
        email='matias@demo.iddam.app',
        username='matias_valenzuela',
        first_name='Matías',
        last_name='Valenzuela',
        nickname='Mati',
        age=24,
        country='CL',
        city='Santiago',
        bio='Joven de Santiago, me encanta la música y servir en la congregación.',
        congregation='Santiago Centro',
        preferred_language='es',
        is_host_available=True,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'intermediate'),
        ],
    ),
    dict(
        email='daniela@demo.iddam.app',
        username='daniela_rios',
        first_name='Daniela',
        last_name='Ríos',
        nickname='Dani',
        age=22,
        country='MX',
        city='Guadalajara',
        bio='Estudiante de diseño, amo los devocionales y compartir con los hermanos.',
        congregation='Guadalajara',
        preferred_language='es',
        is_host_available=False,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'beginner'),
        ],
    ),
    dict(
        email='facundo@demo.iddam.app',
        username='facundo_lopez',
        first_name='Facundo',
        last_name='López',
        nickname='Facu',
        age=27,
        country='AR',
        city='Buenos Aires',
        bio='Músico y productor. Toco guitarra en el grupo de alabanza.',
        congregation='Buenos Aires Sur',
        preferred_language='es',
        is_host_available=True,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'intermediate'),
            ('pt', 'Português', False, 'beginner'),
        ],
    ),
    dict(
        email='camila@demo.iddam.app',
        username='camila_herrera',
        first_name='Camila',
        last_name='Herrera',
        nickname='Cami',
        age=21,
        country='CO',
        city='Medellín',
        bio='Recién bautizada, agradecida por esta comunidad de fe.',
        congregation='Medellín',
        preferred_language='es',
        is_host_available=False,
        languages=[
            ('es', 'Español', True, 'native'),
        ],
    ),
    # Brasileños
    dict(
        email='lucas@demo.iddam.app',
        username='lucas_oliveira',
        first_name='Lucas',
        last_name='Oliveira',
        nickname='Luke',
        age=25,
        country='BR',
        city='São Paulo',
        bio='Programador e músico. Gosto de estudar a Bíblia e tocar violão.',
        congregation='São Paulo',
        preferred_language='pt',
        is_host_available=True,
        languages=[
            ('pt', 'Português', True, 'native'),
            ('es', 'Español', False, 'intermediate'),
            ('en', 'English', False, 'fluent'),
        ],
    ),
    dict(
        email='ana@demo.iddam.app',
        username='ana_santos',
        first_name='Ana',
        last_name='Santos',
        nickname='Aninha',
        age=23,
        country='BR',
        city='Rio de Janeiro',
        bio='Amo a natureza e servir ao próximo. Sempre disposta a ajudar.',
        congregation='Rio de Janeiro',
        preferred_language='pt',
        is_host_available=False,
        languages=[
            ('pt', 'Português', True, 'native'),
            ('es', 'Español', False, 'beginner'),
        ],
    ),
    # Estadounidenses
    dict(
        email='david@demo.iddam.app',
        username='david_miller',
        first_name='David',
        last_name='Miller',
        nickname='Dave',
        age=28,
        country='US',
        city='Dallas',
        bio='Youth leader and Bible study enthusiast. Love connecting with brethren worldwide.',
        congregation='Dallas',
        preferred_language='en',
        is_host_available=True,
        languages=[
            ('en', 'English', True, 'native'),
            ('es', 'Español', False, 'intermediate'),
        ],
    ),
    dict(
        email='sarah@demo.iddam.app',
        username='sarah_johnson',
        first_name='Sarah',
        last_name='Johnson',
        nickname='',
        age=26,
        country='US',
        city='Cincinnati',
        bio='Teacher and aspiring writer. Passionate about serving the youth.',
        congregation='Cincinnati East',
        preferred_language='en',
        is_host_available=False,
        languages=[
            ('en', 'English', True, 'native'),
        ],
    ),
    # España
    dict(
        email='pablo@demo.iddam.app',
        username='pablo_garcia',
        first_name='Pablo',
        last_name='García',
        nickname='Pablito',
        age=30,
        country='ES',
        city='Madrid',
        bio='Ingeniero de software, organizador de estudios bíblicos online.',
        congregation='Madrid',
        preferred_language='es',
        is_host_available=True,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'fluent'),
            ('pt', 'Português', False, 'beginner'),
        ],
    ),
    # Guatemala
    dict(
        email='maria@demo.iddam.app',
        username='maria_mendez',
        first_name='María',
        last_name='Méndez',
        nickname='Mari',
        age=20,
        country='GT',
        city='Guatemala City',
        bio='Aprendiendo cada día más de la palabra. Me encanta cantar.',
        congregation='Guatemala Ciudad',
        preferred_language='es',
        is_host_available=False,
        languages=[
            ('es', 'Español', True, 'native'),
        ],
    ),
    # Perú
    dict(
        email='jose@demo.iddam.app',
        username='jose_paredes',
        first_name='José',
        last_name='Paredes',
        nickname='Pepe',
        age=29,
        country='PE',
        city='Lima',
        bio='Chef y amante de la cocina peruana. Sirvo en actividades sociales.',
        congregation='Lima Norte',
        preferred_language='es',
        is_host_available=True,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'beginner'),
        ],
    ),
    # Venezuela
    dict(
        email='genesis@demo.iddam.app',
        username='genesis_rojas',
        first_name='Génesis',
        last_name='Rojas',
        nickname='Gene',
        age=22,
        country='VE',
        city='Caracas',
        bio='Fotógrafa y diseñadora. Creo contenido para la iglesia.',
        congregation='Caracas',
        preferred_language='es',
        is_host_available=False,
        languages=[
            ('es', 'Español', True, 'native'),
            ('en', 'English', False, 'intermediate'),
        ],
    ),
]

# ── Posts ─────────────────────────────────────────────────────────────────────

POSTS_DATA = [
    # Testimonios
    dict(
        author_email='camila@demo.iddam.app',
        post_type='testimony',
        title='Mi bautismo',
        content=(
            'Hace dos meses me bauticé y fue el día más especial de mi vida. '
            'Sentí la presencia de Dios de una manera increíble. Agradezco a '
            'todos los hermanos que me acompañaron en este camino. '
            '#fe #bautismo #testimonio'
        ),
        hashtags=['fe', 'bautismo', 'testimonio'],
    ),
    dict(
        author_email='david@demo.iddam.app',
        post_type='testimony',
        title='God is faithful',
        content=(
            'I want to share how God opened doors for me this year. After months '
            'of searching, I finally got a job that allows me to keep the Sabbath. '
            'Never give up trusting in Him. #faith #testimony'
        ),
        hashtags=['faith', 'testimony'],
    ),
    dict(
        author_email='lucas@demo.iddam.app',
        post_type='testimony',
        title='Deus é bom',
        content=(
            'Quero compartilhar minha gratidão. Depois de um ano difícil, posso '
            'ver como Deus trabalhou em cada detalhe da minha vida. Ele é fiel! '
            '#fe #gratidao #testemunho'
        ),
        hashtags=['fe', 'gratidao', 'testemunho'],
    ),
    # Devocionales
    dict(
        author_email='sarah@demo.iddam.app',
        post_type='devotional',
        title='Morning reflection: Psalm 23',
        content=(
            'The Lord is my shepherd; I shall not want. What a powerful reminder '
            'that we lack nothing when we walk with God. Today I encourage you '
            'to meditate on this psalm and find peace in His promises. '
            '#devotional #psalms #biblestudy'
        ),
        hashtags=['devotional', 'psalms', 'biblestudy'],
    ),
    dict(
        author_email='pablo@demo.iddam.app',
        post_type='devotional',
        title='Reflexión: Filipenses 4:13',
        content=(
            'Todo lo puedo en Cristo que me fortalece. A veces olvidamos que '
            'nuestra fuerza no viene de nosotros mismos sino de Dios. Hoy te '
            'invito a recordar esta verdad en cada desafío que enfrentes. '
            '#devocional #biblia #fortaleza'
        ),
        hashtags=['devocional', 'biblia', 'fortaleza'],
    ),
    dict(
        author_email='maria@demo.iddam.app',
        post_type='devotional',
        title='Proverbios 3:5-6',
        content=(
            'Confía en el Señor con todo tu corazón y no te apoyes en tu propia '
            'prudencia. En todos tus caminos reconócelo y Él enderezará tus '
            'veredas. Un versículo que me ha acompañado toda la semana. '
            '#devocional #proverbios #confianza'
        ),
        hashtags=['devocional', 'proverbios', 'confianza'],
    ),
    # Hobby
    dict(
        author_email='facundo@demo.iddam.app',
        post_type='hobby',
        title='Nueva canción para el grupo de alabanza',
        content=(
            'Estuve trabajando en un arreglo nuevo para el grupo de alabanza. '
            'Es una versión acústica de un himno clásico, con un toque moderno. '
            'Pronto la comparto con ustedes. #musica #alabanza #guitarra'
        ),
        hashtags=['musica', 'alabanza', 'guitarra'],
    ),
    dict(
        author_email='jose@demo.iddam.app',
        post_type='hobby',
        title='Receta: Ceviche para el almuerzo fraternal',
        content=(
            'Les comparto mi receta de ceviche peruano que preparé para el '
            'último almuerzo fraternal. Ingredientes: pescado fresco, limón, '
            'cebolla morada, ají, cilantro y camote. El secreto está en el '
            'tiempo de marinado. #cocina #peru #receta'
        ),
        hashtags=['cocina', 'peru', 'receta'],
    ),
    dict(
        author_email='genesis@demo.iddam.app',
        post_type='hobby',
        title='Fotografía en el campamento',
        content=(
            'Tomé estas fotos durante el último campamento de jóvenes. La '
            'naturaleza nos recuerda lo maravillosa que es la creación de Dios. '
            'Pronto subo más fotos. #fotografia #campamento #naturaleza'
        ),
        hashtags=['fotografia', 'campamento', 'naturaleza'],
    ),
    dict(
        author_email='lucas@demo.iddam.app',
        post_type='hobby',
        title='Projeto de app para a igreja',
        content=(
            'Estou desenvolvendo um app para ajudar com os estudos bíblicos '
            'do nosso grupo. Se alguém tiver interesse em ajudar com o design, '
            'me avise! #programacao #tecnologia #igreja'
        ),
        hashtags=['programacao', 'tecnologia', 'igreja'],
    ),
    # Texto / General
    dict(
        author_email='matias@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Feliz Sabbat a todos los hermanos! Que este día de reposo sea de '
            'bendición para cada uno. Los saludo desde Santiago con mucho cariño. '
            '#sabbat #saludos'
        ),
        hashtags=['sabbat', 'saludos'],
    ),
    dict(
        author_email='daniela@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Acabo de terminar un diseño para la invitación del próximo estudio '
            'bíblico de jóvenes. Me encanta poder usar mis habilidades para '
            'servir a la iglesia. #juventud #diseño #servicio'
        ),
        hashtags=['juventud', 'servicio'],
    ),
    dict(
        author_email='ana@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Bom dia, irmãos! Que Deus abençoe o dia de cada um. Estou muito '
            'feliz por fazer parte desta comunidade. Abraços do Brasil! '
            '#comunidade #brasil'
        ),
        hashtags=['comunidade', 'brasil'],
    ),
    dict(
        author_email='david@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Just finished organizing the youth activity for next month. '
            'We are planning a Bible trivia night and a fellowship dinner. '
            'Looking forward to seeing everyone there! #youth #fellowship'
        ),
        hashtags=['youth', 'fellowship'],
    ),
    # Noticias
    dict(
        author_email='pablo@demo.iddam.app',
        post_type='news',
        title='Nuevo estudio bíblico online',
        content=(
            'Hermanos, les comparto que estamos organizando un estudio bíblico '
            'semanal por videoconferencia. Será todos los miércoles a las 20:00 '
            'hora de España. Todos están invitados, sin importar el país. '
            '#estudio #online #biblia'
        ),
        hashtags=['estudio', 'online', 'biblia'],
    ),
    dict(
        author_email='matias@demo.iddam.app',
        post_type='news',
        title='Campamento de jóvenes 2025',
        content=(
            'Se confirmó el campamento de jóvenes para enero. Será en las '
            'afueras de Santiago. Pronto publicaremos más detalles sobre la '
            'inscripción y las actividades. #campamento #jovenes #chile'
        ),
        hashtags=['campamento', 'jovenes', 'chile'],
    ),
    # Más testimonios y devocionales
    dict(
        author_email='genesis@demo.iddam.app',
        post_type='testimony',
        title='Agradecida por la comunidad',
        content=(
            'Cuando me mudé a Caracas no conocía a nadie en la iglesia. Hoy '
            'puedo decir que tengo una segunda familia. Gracias a cada uno que '
            'me recibió con los brazos abiertos. #comunidad #gratitud #fe'
        ),
        hashtags=['comunidad', 'gratitud', 'fe'],
    ),
    dict(
        author_email='jose@demo.iddam.app',
        post_type='devotional',
        title='Romanos 8:28',
        content=(
            'Y sabemos que a los que aman a Dios, todas las cosas les ayudan '
            'a bien. En momentos difíciles, este versículo me da mucha paz. '
            'Nada es casualidad, todo tiene un propósito. #devocional #romanos #paz'
        ),
        hashtags=['devocional', 'romanos', 'paz'],
    ),
    dict(
        author_email='sarah@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Happy Sabbath everyone! May this day bring you rest and renewal. '
            'I am reading through the book of Isaiah this week and it has been '
            'so inspiring. What are you studying? #sabbath #isaiah'
        ),
        hashtags=['sabbath', 'isaiah'],
    ),
    dict(
        author_email='ana@demo.iddam.app',
        post_type='devotional',
        title='Salmo 91',
        content=(
            'O que habita no esconderijo do Altíssimo descansará à sombra do '
            'Todo-Poderoso. Um salmo que me traz muita segurança. Deus é nosso '
            'refúgio em todos os momentos. #salmo91 #refugio #deus'
        ),
        hashtags=['salmo91', 'refugio', 'deus'],
    ),
    dict(
        author_email='daniela@demo.iddam.app',
        post_type='hobby',
        title='Bullet journal bíblico',
        content=(
            'Empecé a hacer un bullet journal con versículos y reflexiones '
            'diarias. Es una forma creativa de conectar con la palabra de Dios. '
            'Si quieren ideas, pregunten! #bulletjournal #creatividad #biblia'
        ),
        hashtags=['bulletjournal', 'creatividad', 'biblia'],
    ),
    dict(
        author_email='facundo@demo.iddam.app',
        post_type='text',
        title='',
        content=(
            'Hermanos, estoy buscando músicos para armar una banda de alabanza '
            'virtual. Si tocan algún instrumento o cantan, escríbanme. La idea '
            'es grabar covers de himnos. #musica #alabanza #banda'
        ),
        hashtags=['musica', 'alabanza', 'banda'],
    ),
]

# ── Groups ────────────────────────────────────────────────────────────────────

GROUPS_DATA = [
    dict(
        name='Jóvenes Chile',
        group_type='youth',
        description='Grupo para los jóvenes de las congregaciones de Chile. Actividades, estudios y más.',
        country='CL',
        creator_email='matias@demo.iddam.app',
        members=[
            ('matias@demo.iddam.app', 'admin'),
            ('daniela@demo.iddam.app', 'member'),
            ('facundo@demo.iddam.app', 'member'),
            ('camila@demo.iddam.app', 'member'),
            ('jose@demo.iddam.app', 'member'),
        ],
        posts=[
            ('matias@demo.iddam.app', 'Bienvenidos al grupo de Jóvenes Chile! Publiquen sus ideas para actividades.'),
            ('daniela@demo.iddam.app', 'Hola a todos! Propongo organizar un estudio bíblico semanal por Zoom.'),
            ('camila@demo.iddam.app', 'Me encanta la idea del estudio! Yo me apunto.'),
        ],
    ),
    dict(
        name='Alabanza y Adoración',
        group_type='musical',
        description='Para músicos y cantantes que sirven en los grupos de alabanza. Compartimos partituras, ideas y grabaciones.',
        country='',
        creator_email='facundo@demo.iddam.app',
        members=[
            ('facundo@demo.iddam.app', 'admin'),
            ('matias@demo.iddam.app', 'member'),
            ('lucas@demo.iddam.app', 'member'),
            ('maria@demo.iddam.app', 'member'),
            ('david@demo.iddam.app', 'member'),
            ('genesis@demo.iddam.app', 'member'),
        ],
        posts=[
            ('facundo@demo.iddam.app', 'Bienvenidos músicos! Suban sus covers y arreglos aquí.'),
            ('lucas@demo.iddam.app', 'Oi pessoal! Gravei um arranjo de violão, posso compartilhar aqui?'),
            ('maria@demo.iddam.app', 'Yo canto, me encantaría participar en alguna grabación virtual.'),
            ('facundo@demo.iddam.app', 'Lucas, sube el arreglo! Y María, te escribo para coordinar.'),
        ],
    ),
    dict(
        name='Estudio Bíblico Semanal',
        group_type='study',
        description='Grupo de estudio bíblico semanal. Cada semana un tema diferente. Todos los niveles bienvenidos.',
        country='',
        creator_email='pablo@demo.iddam.app',
        members=[
            ('pablo@demo.iddam.app', 'admin'),
            ('sarah@demo.iddam.app', 'mod'),
            ('david@demo.iddam.app', 'member'),
            ('daniela@demo.iddam.app', 'member'),
            ('jose@demo.iddam.app', 'member'),
            ('ana@demo.iddam.app', 'member'),
            ('camila@demo.iddam.app', 'member'),
            ('genesis@demo.iddam.app', 'member'),
        ],
        posts=[
            ('pablo@demo.iddam.app', 'Esta semana estudiaremos el libro de Filipenses. Lean los capítulos 1 y 2 antes del miércoles.'),
            ('sarah@demo.iddam.app', 'I will prepare some discussion questions for the study. Looking forward to it!'),
            ('ana@demo.iddam.app', 'Vou participar! Posso trazer uma perspectiva do texto em português?'),
            ('pablo@demo.iddam.app', 'Por supuesto Ana, todas las perspectivas son bienvenidas!'),
        ],
    ),
    dict(
        name='Hermanos en USA',
        group_type='country',
        description='Grupo para los hermanos que viven en Estados Unidos. Coordinación de actividades y comunidad.',
        country='US',
        creator_email='david@demo.iddam.app',
        members=[
            ('david@demo.iddam.app', 'admin'),
            ('sarah@demo.iddam.app', 'mod'),
            ('pablo@demo.iddam.app', 'member'),
        ],
        posts=[
            ('david@demo.iddam.app', 'Welcome to the US brethren group! Share events and activities in your area.'),
            ('sarah@demo.iddam.app', 'We are planning a potluck after services next month in Cincinnati. All welcome!'),
        ],
    ),
    dict(
        name='General COGWA Jóvenes',
        group_type='general',
        description='Grupo general para jóvenes de COGWA en todo el mundo. Anuncios, preguntas y compañerismo.',
        country='',
        creator_email='matias@demo.iddam.app',
        members=[
            ('matias@demo.iddam.app', 'admin'),
            ('david@demo.iddam.app', 'mod'),
            ('pablo@demo.iddam.app', 'mod'),
            ('daniela@demo.iddam.app', 'member'),
            ('facundo@demo.iddam.app', 'member'),
            ('camila@demo.iddam.app', 'member'),
            ('lucas@demo.iddam.app', 'member'),
            ('ana@demo.iddam.app', 'member'),
            ('sarah@demo.iddam.app', 'member'),
            ('maria@demo.iddam.app', 'member'),
            ('jose@demo.iddam.app', 'member'),
            ('genesis@demo.iddam.app', 'member'),
        ],
        posts=[
            ('matias@demo.iddam.app', 'Bienvenidos a todos los jóvenes de COGWA! Este es nuestro espacio para conectarnos.'),
            ('david@demo.iddam.app', 'Great to see this group growing! Let us use this space to encourage one another.'),
            ('lucas@demo.iddam.app', 'Que bom estar conectado com jovens do mundo todo! Olá de São Paulo!'),
        ],
    ),
]

# ── Stories ───────────────────────────────────────────────────────────────────

STORIES_DATA = [
    dict(user_email='matias@demo.iddam.app', text='Feliz Sabbat desde Santiago!', background_color='#2EA3F2'),
    dict(user_email='daniela@demo.iddam.app', text='Nuevo diseño terminado para la iglesia', background_color='#E91E63'),
    dict(user_email='lucas@demo.iddam.app', text='Bom dia! Deus abençoe seu dia', background_color='#4CAF50'),
    dict(user_email='david@demo.iddam.app', text='Bible study tonight at 7pm!', background_color='#FF9800'),
    dict(user_email='genesis@demo.iddam.app', text='Sesión de fotos para el campamento', background_color='#9C27B0'),
    dict(user_email='facundo@demo.iddam.app', text='Ensayo de alabanza, sonando bien!', background_color='#F44336'),
    dict(user_email='sarah@demo.iddam.app', text='Grateful for this community', background_color='#3F51B5'),
    dict(user_email='jose@demo.iddam.app', text='Preparando almuerzo fraternal', background_color='#795548'),
]

# ── Story Highlights ──────────────────────────────────────────────────────────

HIGHLIGHTS_DATA = [
    dict(
        user_email='matias@demo.iddam.app',
        name='Sabbat',
        story_indices=[0],  # indices into STORIES_DATA belonging to this user
    ),
    dict(
        user_email='genesis@demo.iddam.app',
        name='Fotografía',
        story_indices=[4],
    ),
    dict(
        user_email='david@demo.iddam.app',
        name='Bible Study',
        story_indices=[3],
    ),
]

# ── Chat conversations ───────────────────────────────────────────────────────

CONVERSATIONS_DATA = [
    dict(
        user1_email='matias@demo.iddam.app',
        user2_email='david@demo.iddam.app',
        messages=[
            ('matias@demo.iddam.app', 'Hola David! Cómo estás? Vi que están organizando actividades allá en Dallas.'),
            ('david@demo.iddam.app', 'Hey Matias! Yes, we have a youth meeting coming up. How are things in Chile?'),
            ('matias@demo.iddam.app', 'Todo bien por acá, preparando el campamento de enero. Sería genial hacer algo juntos online.'),
            ('david@demo.iddam.app', 'That sounds great! We could organize a virtual game night between both groups.'),
            ('matias@demo.iddam.app', 'Me encanta la idea! Lo conversamos esta semana?'),
        ],
    ),
    dict(
        user1_email='lucas@demo.iddam.app',
        user2_email='facundo@demo.iddam.app',
        messages=[
            ('lucas@demo.iddam.app', 'Oi Facundo! Vi que você toca guitarra. Eu também toco violão!'),
            ('facundo@demo.iddam.app', 'Hola Lucas! Qué bueno, deberíamos tocar algo juntos. Entendés español?'),
            ('lucas@demo.iddam.app', 'Sim, entendo bastante! Podemos misturar os dois idiomas, sem problema.'),
            ('facundo@demo.iddam.app', 'Dale, te mando un arreglo que estoy haciendo. Es un himno con ritmo bossa nova.'),
            ('lucas@demo.iddam.app', 'Bossa nova? Que legal! Manda sim, vou adorar.'),
            ('facundo@demo.iddam.app', 'Joya, te lo paso mañana. Abrazo hermano!'),
        ],
    ),
    dict(
        user1_email='daniela@demo.iddam.app',
        user2_email='genesis@demo.iddam.app',
        messages=[
            ('daniela@demo.iddam.app', 'Hola Génesis! Vi tus fotos del campamento, están hermosas.'),
            ('genesis@demo.iddam.app', 'Gracias Dani! Me encantaría ver tus diseños, sos diseñadora verdad?'),
            ('daniela@demo.iddam.app', 'Sí! Estudio diseño gráfico. Podríamos colaborar en algo para la iglesia.'),
            ('genesis@demo.iddam.app', 'Me encanta! Yo hago las fotos y vos los diseños. Sería un buen equipo.'),
        ],
    ),
    dict(
        user1_email='sarah@demo.iddam.app',
        user2_email='ana@demo.iddam.app',
        messages=[
            ('sarah@demo.iddam.app', 'Hi Ana! I saw your post about the Bible study. I would love to join!'),
            ('ana@demo.iddam.app', 'Oi Sarah! Que bom! O estudo é toda quarta-feira às 20h. Você pode participar?'),
            ('sarah@demo.iddam.app', 'Yes! I can join on Wednesdays. Do you study in Portuguese or Spanish?'),
            ('ana@demo.iddam.app', 'Normalmente em espanhol, mas podemos incluir inglês também! Todos são bem-vindos.'),
            ('sarah@demo.iddam.app', 'That is wonderful. I am learning some Spanish too. See you Wednesday!'),
        ],
    ),
    dict(
        user1_email='pablo@demo.iddam.app',
        user2_email='jose@demo.iddam.app',
        messages=[
            ('pablo@demo.iddam.app', 'Hola José! Quería preguntarte si te gustaría dar el tema del estudio bíblico esta semana.'),
            ('jose@demo.iddam.app', 'Hola Pablo! Claro, me encantaría. Estaba pensando en hacer algo sobre Romanos 8.'),
            ('pablo@demo.iddam.app', 'Excelente tema! Romanos 8 tiene mucho contenido. Te parece el miércoles a las 20h?'),
            ('jose@demo.iddam.app', 'Perfecto, ahí estaré. Voy a preparar unas notas y preguntas para la discusión.'),
        ],
    ),
]

# ── Events ────────────────────────────────────────────────────────────────────

EVENTS_DATA = [
    dict(
        organizer_email='matias@demo.iddam.app',
        event_type='youth_meeting',
        title='Reunión de Jóvenes Chile - Enero',
        description=(
            'Reunión mensual de jóvenes en Santiago. Tendremos estudio bíblico, '
            'juegos y cena fraternal. Todos los jóvenes están invitados!'
        ),
        location='Santiago, Chile',
        country='CL',
        is_virtual=False,
        days_ahead=30,
        rsvps=[
            ('matias@demo.iddam.app', 'going'),
            ('daniela@demo.iddam.app', 'going'),
            ('camila@demo.iddam.app', 'going'),
            ('facundo@demo.iddam.app', 'maybe'),
            ('jose@demo.iddam.app', 'maybe'),
        ],
    ),
    dict(
        organizer_email='facundo@demo.iddam.app',
        event_type='musical',
        title='Noche de Alabanza Virtual',
        description=(
            'Evento musical online donde presentaremos covers de himnos. '
            'Músicos de diferentes países participarán en vivo.'
        ),
        location='',
        country='',
        is_virtual=True,
        meeting_link='https://zoom.us/j/example',
        days_ahead=14,
        rsvps=[
            ('facundo@demo.iddam.app', 'going'),
            ('lucas@demo.iddam.app', 'going'),
            ('maria@demo.iddam.app', 'going'),
            ('matias@demo.iddam.app', 'going'),
            ('genesis@demo.iddam.app', 'going'),
            ('david@demo.iddam.app', 'maybe'),
        ],
    ),
    dict(
        organizer_email='pablo@demo.iddam.app',
        event_type='study',
        title='Estudio Bíblico: Epístola a los Filipenses',
        description=(
            'Serie de estudios sobre Filipenses. Esta semana veremos los '
            'capítulos 3 y 4. Trae tu Biblia y tus preguntas.'
        ),
        location='',
        country='',
        is_virtual=True,
        meeting_link='https://zoom.us/j/example2',
        days_ahead=3,
        rsvps=[
            ('pablo@demo.iddam.app', 'going'),
            ('sarah@demo.iddam.app', 'going'),
            ('daniela@demo.iddam.app', 'going'),
            ('jose@demo.iddam.app', 'going'),
            ('ana@demo.iddam.app', 'going'),
            ('camila@demo.iddam.app', 'maybe'),
        ],
    ),
    dict(
        organizer_email='david@demo.iddam.app',
        event_type='camp',
        title='Youth Camp USA - Summer',
        description=(
            'Annual summer youth camp in Texas. A week of Bible studies, '
            'outdoor activities, sports, and fellowship. Registration opens soon!'
        ),
        location='Dallas, Texas',
        country='US',
        is_virtual=False,
        days_ahead=90,
        rsvps=[
            ('david@demo.iddam.app', 'going'),
            ('sarah@demo.iddam.app', 'going'),
        ],
    ),
]

# ── Proposals ─────────────────────────────────────────────────────────────────

PROPOSALS_DATA = [
    dict(
        author_email='camila@demo.iddam.app',
        group_name='General COGWA Jóvenes',
        proposal_type='fasting',
        title='Día de ayuno por la paz',
        description='Propongo que hagamos un día de ayuno comunitario pidiendo por la paz en nuestros países y por los hermanos que están pasando dificultades.',
        days_ahead=7,
        participants=[
            'camila@demo.iddam.app', 'matias@demo.iddam.app',
            'daniela@demo.iddam.app', 'jose@demo.iddam.app',
            'maria@demo.iddam.app', 'genesis@demo.iddam.app',
        ],
    ),
    dict(
        author_email='david@demo.iddam.app',
        group_name='Hermanos en USA',
        proposal_type='prayer',
        title='Prayer chain for the youth',
        description='Let us organize a prayer chain for all the young people in the church. Each person prays for 30 minutes during the day.',
        days_ahead=5,
        participants=[
            'david@demo.iddam.app', 'sarah@demo.iddam.app',
            'pablo@demo.iddam.app',
        ],
    ),
    dict(
        author_email='matias@demo.iddam.app',
        group_name='Jóvenes Chile',
        proposal_type='activity',
        title='Día de senderismo en Cajón del Maipo',
        description='Organicemos una salida a Cajón del Maipo para caminar, compartir y disfrutar de la creación. Lleven almuerzo y protector solar.',
        days_ahead=21,
        participants=[
            'matias@demo.iddam.app', 'daniela@demo.iddam.app',
            'camila@demo.iddam.app', 'jose@demo.iddam.app',
        ],
    ),
]

# ── Comments on posts ─────────────────────────────────────────────────────────

# (post_index, commenter_email, content, parent_is_index_of_comment_or_None)
COMMENTS_DATA = [
    # Comments on post 0 (Camila's bautismo)
    (0, 'matias@demo.iddam.app', 'Qué hermoso testimonio Cami! Dios te bendiga siempre.', None),
    (0, 'daniela@demo.iddam.app', 'Felicidades por tu bautismo! Es un paso muy importante.', None),
    (0, 'camila@demo.iddam.app', 'Gracias a todos! Son una bendición.', 0),
    # Comments on post 1 (David's testimony)
    (1, 'sarah@demo.iddam.app', 'So happy for you David! God always provides.', None),
    (1, 'pablo@demo.iddam.app', 'Amen! Dios siempre abre puertas. Congratulations!', None),
    # Comments on post 3 (Sarah's devotional)
    (3, 'david@demo.iddam.app', 'One of my favorite psalms. Thanks for sharing Sarah.', None),
    (3, 'maria@demo.iddam.app', 'Mi salmo favorito también! Gracias por compartir.', None),
    # Comments on post 6 (Facundo's music)
    (6, 'lucas@demo.iddam.app', 'Muito legal! Quando você compartilhar, me avise!', None),
    (6, 'matias@demo.iddam.app', 'Crack Facu! Ya quiero escucharlo.', None),
    (6, 'facundo@demo.iddam.app', 'Gracias hermanos! Lo subo esta semana.', 7),
    # Comments on post 10 (Matias sabbat greeting)
    (10, 'jose@demo.iddam.app', 'Feliz Sabbat desde Lima hermano!', None),
    (10, 'genesis@demo.iddam.app', 'Feliz Sabbat! Saludos desde Caracas.', None),
    (10, 'ana@demo.iddam.app', 'Feliz Sábado! Abraços do Brasil!', None),
    # Comments on post 14 (Pablo's online study news)
    (14, 'daniela@demo.iddam.app', 'Me apunto! A qué hora sería en México?', None),
    (14, 'pablo@demo.iddam.app', 'Sería a las 13:00 hora de México. Te esperamos!', 13),
    (14, 'lucas@demo.iddam.app', 'Posso participar? Seria às 16h no Brasil, certo?', None),
    (14, 'pablo@demo.iddam.app', 'Sí Lucas, a las 16h en Brasil. Eres bienvenido!', 15),
]

# ── Reactions on posts ────────────────────────────────────────────────────────

# (post_index, reactor_email, reaction_type)
REACTIONS_DATA = [
    # Post 0 - Camila bautismo
    (0, 'matias@demo.iddam.app', 'love'),
    (0, 'daniela@demo.iddam.app', 'love'),
    (0, 'david@demo.iddam.app', 'pray'),
    (0, 'facundo@demo.iddam.app', 'amen'),
    (0, 'genesis@demo.iddam.app', 'love'),
    (0, 'sarah@demo.iddam.app', 'love'),
    (0, 'jose@demo.iddam.app', 'amen'),
    # Post 1 - David testimony
    (1, 'sarah@demo.iddam.app', 'love'),
    (1, 'pablo@demo.iddam.app', 'amen'),
    (1, 'matias@demo.iddam.app', 'pray'),
    (1, 'camila@demo.iddam.app', 'like'),
    # Post 2 - Lucas testimony
    (2, 'ana@demo.iddam.app', 'love'),
    (2, 'facundo@demo.iddam.app', 'amen'),
    (2, 'david@demo.iddam.app', 'pray'),
    # Post 3 - Sarah devotional
    (3, 'david@demo.iddam.app', 'love'),
    (3, 'maria@demo.iddam.app', 'pray'),
    (3, 'pablo@demo.iddam.app', 'like'),
    (3, 'daniela@demo.iddam.app', 'amen'),
    (3, 'jose@demo.iddam.app', 'pray'),
    # Post 4 - Pablo devotional
    (4, 'sarah@demo.iddam.app', 'amen'),
    (4, 'matias@demo.iddam.app', 'like'),
    (4, 'camila@demo.iddam.app', 'pray'),
    # Post 6 - Facundo music
    (6, 'lucas@demo.iddam.app', 'fire'),
    (6, 'matias@demo.iddam.app', 'fire'),
    (6, 'maria@demo.iddam.app', 'love'),
    (6, 'genesis@demo.iddam.app', 'like'),
    # Post 7 - Jose cocina
    (7, 'matias@demo.iddam.app', 'fire'),
    (7, 'daniela@demo.iddam.app', 'love'),
    (7, 'camila@demo.iddam.app', 'like'),
    # Post 8 - Genesis foto
    (8, 'daniela@demo.iddam.app', 'love'),
    (8, 'matias@demo.iddam.app', 'like'),
    (8, 'camila@demo.iddam.app', 'love'),
    # Post 10 - Matias sabbat
    (10, 'jose@demo.iddam.app', 'love'),
    (10, 'genesis@demo.iddam.app', 'like'),
    (10, 'ana@demo.iddam.app', 'love'),
    (10, 'david@demo.iddam.app', 'like'),
    # Post 14 - Pablo online study
    (14, 'daniela@demo.iddam.app', 'like'),
    (14, 'lucas@demo.iddam.app', 'like'),
    (14, 'sarah@demo.iddam.app', 'like'),
    (14, 'jose@demo.iddam.app', 'like'),
    # Scattered reactions on other posts
    (5, 'camila@demo.iddam.app', 'pray'),
    (5, 'genesis@demo.iddam.app', 'amen'),
    (9, 'facundo@demo.iddam.app', 'fire'),
    (9, 'pablo@demo.iddam.app', 'like'),
    (11, 'matias@demo.iddam.app', 'like'),
    (11, 'genesis@demo.iddam.app', 'love'),
    (12, 'lucas@demo.iddam.app', 'love'),
    (12, 'facundo@demo.iddam.app', 'like'),
    (13, 'sarah@demo.iddam.app', 'like'),
    (13, 'matias@demo.iddam.app', 'like'),
    (15, 'david@demo.iddam.app', 'like'),
    (15, 'facundo@demo.iddam.app', 'fire'),
    (16, 'matias@demo.iddam.app', 'love'),
    (16, 'jose@demo.iddam.app', 'pray'),
    (17, 'pablo@demo.iddam.app', 'amen'),
    (17, 'camila@demo.iddam.app', 'pray'),
    (18, 'david@demo.iddam.app', 'love'),
    (18, 'pablo@demo.iddam.app', 'like'),
    (19, 'lucas@demo.iddam.app', 'pray'),
    (19, 'sarah@demo.iddam.app', 'love'),
    (20, 'daniela@demo.iddam.app', 'love'),
    (20, 'genesis@demo.iddam.app', 'like'),
    (21, 'lucas@demo.iddam.app', 'fire'),
    (21, 'matias@demo.iddam.app', 'like'),
]

# ── Follow / friendship data ─────────────────────────────────────────────────

# Mutual follows (both directions)
MUTUAL_FOLLOWS = [
    ('matias@demo.iddam.app', 'daniela@demo.iddam.app'),
    ('matias@demo.iddam.app', 'facundo@demo.iddam.app'),
    ('matias@demo.iddam.app', 'david@demo.iddam.app'),
    ('matias@demo.iddam.app', 'camila@demo.iddam.app'),
    ('daniela@demo.iddam.app', 'genesis@demo.iddam.app'),
    ('daniela@demo.iddam.app', 'camila@demo.iddam.app'),
    ('facundo@demo.iddam.app', 'lucas@demo.iddam.app'),
    ('david@demo.iddam.app', 'sarah@demo.iddam.app'),
    ('david@demo.iddam.app', 'pablo@demo.iddam.app'),
    ('pablo@demo.iddam.app', 'sarah@demo.iddam.app'),
    ('lucas@demo.iddam.app', 'ana@demo.iddam.app'),
    ('jose@demo.iddam.app', 'matias@demo.iddam.app'),
    ('genesis@demo.iddam.app', 'camila@demo.iddam.app'),
    ('maria@demo.iddam.app', 'genesis@demo.iddam.app'),
]

# Unidirectional follows (A follows B, but B doesn't follow A)
UNI_FOLLOWS = [
    ('camila@demo.iddam.app', 'sarah@demo.iddam.app'),
    ('maria@demo.iddam.app', 'facundo@demo.iddam.app'),
    ('ana@demo.iddam.app', 'pablo@demo.iddam.app'),
    ('jose@demo.iddam.app', 'david@demo.iddam.app'),
    ('genesis@demo.iddam.app', 'lucas@demo.iddam.app'),
    ('maria@demo.iddam.app', 'matias@demo.iddam.app'),
    ('jose@demo.iddam.app', 'facundo@demo.iddam.app'),
    ('ana@demo.iddam.app', 'daniela@demo.iddam.app'),
]

FRIENDSHIPS_DATA = [
    ('matias@demo.iddam.app', 'facundo@demo.iddam.app'),
    ('matias@demo.iddam.app', 'david@demo.iddam.app'),
    ('daniela@demo.iddam.app', 'genesis@demo.iddam.app'),
    ('david@demo.iddam.app', 'sarah@demo.iddam.app'),
    ('lucas@demo.iddam.app', 'facundo@demo.iddam.app'),
    ('pablo@demo.iddam.app', 'david@demo.iddam.app'),
]

FRIEND_REQUESTS_DATA = [
    ('camila@demo.iddam.app', 'matias@demo.iddam.app', 'pending', 'Hola! Me gustaría ser tu amiga.'),
    ('jose@demo.iddam.app', 'pablo@demo.iddam.app', 'pending', 'Hola Pablo, saludos desde Lima!'),
    ('ana@demo.iddam.app', 'sarah@demo.iddam.app', 'pending', 'Hi Sarah! Would love to connect.'),
]

# ── Job categories & postings ─────────────────────────────────────────────

JOB_CATEGORIES_DATA = [
    dict(name='Tecnología', icon='bi-laptop', order=1),
    dict(name='Diseño', icon='bi-palette', order=2),
    dict(name='Educación', icon='bi-book', order=3),
    dict(name='Administración', icon='bi-briefcase', order=4),
    dict(name='Cocina / Gastronomía', icon='bi-cup-hot', order=5),
    dict(name='Música / Producción', icon='bi-music-note-beamed', order=6),
]

JOB_POSTINGS_DATA = [
    dict(
        author_email='pablo@demo.iddam.app',
        title='Desarrollador Frontend React',
        description=(
            'Buscamos desarrollador frontend con experiencia en React y TypeScript. '
            'Trabajo remoto, equipo internacional. Buen ambiente y horario flexible. '
            'Se valora experiencia con Next.js y Tailwind CSS.'
        ),
        category_name='Tecnología',
        company_name='TechSolutions Madrid',
        job_type='full_time',
        modality='remote',
        experience_level='mid',
        salary_type='range',
        salary_min=2000,
        salary_max=3500,
        salary_currency='EUR',
        location_city='Madrid',
        location_country='ES',
        skills='React, TypeScript, Next.js, Tailwind CSS, Git',
        requirements='2+ años de experiencia en desarrollo frontend. Inglés intermedio.',
        contact_email='pablo@demo.iddam.app',
    ),
    dict(
        author_email='david@demo.iddam.app',
        title='Youth Program Coordinator',
        description=(
            'We are looking for a coordinator for our youth programs. '
            'Responsibilities include organizing events, managing volunteers, '
            'and creating educational content for young adults. Part-time position '
            'with flexible hours.'
        ),
        category_name='Educación',
        company_name='Community Center Dallas',
        job_type='part_time',
        modality='on_site',
        experience_level='entry',
        salary_type='negotiable',
        location_city='Dallas',
        location_country='US',
        skills='Event planning, Leadership, Communication',
        requirements='Experience working with youth groups. Bilingual English/Spanish preferred.',
        contact_email='david@demo.iddam.app',
    ),
    dict(
        author_email='genesis@demo.iddam.app',
        title='Diseñador Gráfico Freelance',
        description=(
            'Busco diseñador gráfico freelance para proyectos de branding y '
            'redes sociales. Manejo de Illustrator, Photoshop y Figma. '
            'Proyectos puntuales con posibilidad de continuidad.'
        ),
        category_name='Diseño',
        company_name='',
        job_type='freelance',
        modality='remote',
        experience_level='any',
        salary_type='contact',
        location_city='Caracas',
        location_country='VE',
        skills='Illustrator, Photoshop, Figma, Branding',
        requirements='Portafolio con trabajos previos.',
        contact_email='genesis@demo.iddam.app',
    ),
    dict(
        author_email='lucas@demo.iddam.app',
        title='Desenvolvedor Backend Python/Django',
        description=(
            'Procuramos desenvolvedor backend com experiência em Python e Django. '
            'Projeto de aplicativo para comunidade. Trabalho remoto com reuniões '
            'semanais por videoconferência. Ambiente colaborativo.'
        ),
        category_name='Tecnología',
        company_name='DevBR Solutions',
        job_type='contract',
        modality='remote',
        experience_level='mid',
        salary_type='range',
        salary_min=3000,
        salary_max=5000,
        salary_currency='BRL',
        location_city='São Paulo',
        location_country='BR',
        skills='Python, Django, PostgreSQL, REST APIs, Docker',
        requirements='Experiência com Django REST Framework. Português nativo.',
        contact_email='lucas@demo.iddam.app',
    ),
    dict(
        author_email='jose@demo.iddam.app',
        title='Ayudante de cocina para eventos',
        description=(
            'Se necesita ayudante de cocina para los eventos fraternales de la '
            'congregación. Apoyo en preparación de alimentos, servicio y limpieza. '
            'Trabajo voluntario con almuerzo incluido.'
        ),
        category_name='Cocina / Gastronomía',
        company_name='',
        job_type='volunteer',
        modality='on_site',
        experience_level='any',
        salary_type='volunteer',
        location_city='Lima',
        location_country='PE',
        skills='Cocina básica, Trabajo en equipo',
        requirements='Ganas de servir y buena disposición.',
        contact_email='jose@demo.iddam.app',
    ),
    dict(
        author_email='facundo@demo.iddam.app',
        title='Profesor de guitarra online',
        description=(
            'Ofrezco clases de guitarra acústica y eléctrica por videollamada. '
            'Todos los niveles, desde principiante hasta avanzado. Repertorio '
            'variado incluyendo música de alabanza. Clases de 45 minutos.'
        ),
        category_name='Música / Producción',
        company_name='',
        job_type='freelance',
        modality='remote',
        experience_level='any',
        salary_type='range',
        salary_min=15,
        salary_max=25,
        salary_currency='USD',
        location_city='Buenos Aires',
        location_country='AR',
        skills='Guitarra acústica, Guitarra eléctrica, Teoría musical',
        requirements='Tener guitarra propia y conexión estable a internet.',
        contact_email='facundo@demo.iddam.app',
    ),
]

# ── Career tips ───────────────────────────────────────────────────────────

TIP_CATEGORIES_DATA = [
    dict(name='Búsqueda de empleo', order=1),
    dict(name='Desarrollo profesional', order=2),
    dict(name='Habilidades blandas', order=3),
]

CAREER_TIPS_DATA = [
    dict(
        author_email='pablo@demo.iddam.app',
        category_name='Búsqueda de empleo',
        title='Cómo armar un buen CV para tecnología',
        content=(
            'Un buen CV técnico debe ser conciso (máximo 2 páginas), incluir '
            'tus proyectos más relevantes con links a GitHub o demos, listar '
            'las tecnologías que manejas y tener una sección de logros medibles. '
            'Evita incluir información irrelevante como tu foto o estado civil.'
        ),
    ),
    dict(
        author_email='david@demo.iddam.app',
        category_name='Desarrollo profesional',
        title='Tips for networking as a young professional',
        content=(
            'Networking is about building genuine relationships, not just collecting '
            'contacts. Attend events related to your field, follow up with people '
            'you meet, and offer value before asking for favors. LinkedIn is a great '
            'tool but nothing beats a face-to-face conversation.'
        ),
    ),
    dict(
        author_email='genesis@demo.iddam.app',
        category_name='Desarrollo profesional',
        title='Cómo crear un portafolio de diseño que destaque',
        content=(
            'Tu portafolio es tu carta de presentación. Incluye solo tus mejores '
            'trabajos (calidad sobre cantidad), explica el proceso detrás de cada '
            'proyecto, y muestra el antes y después. Usa plataformas como Behance '
            'o crea tu propio sitio web.'
        ),
    ),
    dict(
        author_email='sarah@demo.iddam.app',
        category_name='Habilidades blandas',
        title='The importance of communication skills at work',
        content=(
            'Good communication is the foundation of professional success. Practice '
            'active listening, be clear and concise in emails, and learn to give '
            'constructive feedback. Remember that communication is not just about '
            'speaking, it is about making sure your message is understood.'
        ),
    ),
    dict(
        author_email='lucas@demo.iddam.app',
        category_name='Búsqueda de empleo',
        title='Como se preparar para entrevistas técnicas',
        content=(
            'Para entrevistas técnicas em programação: pratique algoritmos no '
            'LeetCode, revise conceitos fundamentais, prepare exemplos de projetos '
            'que você trabalhou e pratique explicar seu raciocínio em voz alta. '
            'Não tenha medo de perguntar ao entrevistador quando não entender algo.'
        ),
    ),
]

# ── Professional profiles ─────────────────────────────────────────────────

PROFESSIONAL_PROFILES_DATA = [
    dict(
        user_email='pablo@demo.iddam.app',
        headline='Ingeniero de Software Full Stack',
        summary='Desarrollador con 6 años de experiencia en aplicaciones web. Especializado en React, Django y arquitectura cloud.',
        availability='available',
        years_of_experience=6,
        education='Ingeniería Informática - Universidad Complutense de Madrid',
        skills='Python, Django, React, TypeScript, PostgreSQL, Docker, AWS',
        services='Desarrollo web, Consultoría técnica, Mentoría',
        category_name='Tecnología',
    ),
    dict(
        user_email='genesis@demo.iddam.app',
        headline='Diseñadora Gráfica y Fotógrafa',
        summary='Diseñadora creativa con pasión por el branding y la fotografía. Experiencia en proyectos para iglesias y organizaciones sin fines de lucro.',
        availability='available',
        years_of_experience=3,
        education='Diseño Gráfico - Universidad Central de Venezuela',
        skills='Photoshop, Illustrator, Figma, Fotografía, Video',
        services='Diseño de marca, Fotografía de eventos, Material gráfico para redes',
        category_name='Diseño',
    ),
    dict(
        user_email='lucas@demo.iddam.app',
        headline='Desenvolvedor Backend Python',
        summary='Programador backend focado em APIs REST e microsserviços. Experiência com Django, FastAPI e bancos de dados relacionais.',
        availability='busy',
        years_of_experience=4,
        education='Ciência da Computação - USP',
        skills='Python, Django, FastAPI, PostgreSQL, Redis, Docker, Linux',
        services='Desenvolvimento backend, APIs REST, Automação',
        category_name='Tecnología',
    ),
    dict(
        user_email='facundo@demo.iddam.app',
        headline='Músico y Productor Musical',
        summary='Guitarrista y productor con experiencia en grabación y producción de música de alabanza. Clases de guitarra online.',
        availability='available',
        years_of_experience=8,
        education='Producción Musical - Berklee Online',
        skills='Guitarra, Producción musical, Ableton, Logic Pro, Mezcla',
        services='Clases de guitarra, Producción musical, Arreglos',
        category_name='Música / Producción',
    ),
]


class Command(BaseCommand):
    help = 'Seed the database with realistic demo data for testing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all demo data (users with @demo.iddam.app) before seeding.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        self.user_cache = {}
        counters = {}

        counters['users'] = self._create_users()
        counters['languages'] = self._create_languages()
        counters['follows'] = self._create_follows()
        counters['friendships'] = self._create_friendships()
        counters['friend_requests'] = self._create_friend_requests()
        counters['posts'], post_objects = self._create_posts()
        counters['hashtags'] = self._count_hashtags()
        counters['reactions'] = self._create_reactions(post_objects)
        counters['comments'] = self._create_comments(post_objects)
        counters['groups'] = self._create_groups()
        counters['stories'], story_objects = self._create_stories()
        counters['highlights'] = self._create_highlights(story_objects)
        counters['conversations'] = self._create_conversations()
        counters['events'] = self._create_events()
        counters['proposals'] = self._create_proposals()
        counters['job_postings'] = self._create_job_postings()
        counters['career_tips'] = self._create_career_tips()
        counters['pro_profiles'] = self._create_professional_profiles()
        counters['real_user_links'] = self._link_real_users()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 50))
        self.stdout.write(self.style.SUCCESS('  Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('═' * 50))
        for label, count in counters.items():
            self.stdout.write(f'  {label:<20} {count}')
        self.stdout.write('')
        self.stdout.write(f'  Login with any @{DEMO_DOMAIN} email')
        self.stdout.write(f'  Password: {DEMO_PASSWORD}')
        self.stdout.write(self.style.SUCCESS('═' * 50))

    # ── Flush ─────────────────────────────────────────────────────────────

    def _flush(self):
        demo_users = User.objects.filter(email__endswith=f'@{DEMO_DOMAIN}')
        count = demo_users.count()
        # Delete groups created by demo users (SET_NULL doesn't cascade)
        group_names = [g['name'] for g in GROUPS_DATA]
        g_count, _ = Group.objects.filter(name__in=group_names).delete()
        # Remove follows/friendships between real users and demo users
        demo_ids = list(demo_users.values_list('pk', flat=True))
        if demo_ids:
            from django.db.models import Q
            Follow.objects.filter(
                Q(follower_id__in=demo_ids) | Q(followed_id__in=demo_ids),
            ).delete()
            Friendship.objects.filter(
                Q(user1_id__in=demo_ids) | Q(user2_id__in=demo_ids),
            ).delete()
        if count == 0 and g_count == 0:
            self.stdout.write('No demo data found to flush.')
            return
        demo_users.delete()
        self.stdout.write(self.style.WARNING(
            f'Flushed {count} demo users, {g_count} related objects (groups etc).'
        ))

    # ── Helpers ───────────────────────────────────────────────────────────

    def _get_user(self, email):
        if email not in self.user_cache:
            self.user_cache[email] = User.objects.get(email=email)
        return self.user_cache[email]

    # ── Users ─────────────────────────────────────────────────────────────

    def _create_users(self):
        created = 0
        for data in USERS_DATA:
            user, was_created = User.objects.get_or_create(
                email=data['email'],
                defaults=dict(
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    nickname=data.get('nickname', ''),
                    age=data.get('age'),
                    country=data.get('country', ''),
                    city=data.get('city', ''),
                    bio=data.get('bio', ''),
                    congregation=data.get('congregation', ''),
                    preferred_language=data.get('preferred_language', 'es'),
                    is_host_available=data.get('is_host_available', False),
                ),
            )
            if was_created:
                user.set_password(DEMO_PASSWORD)
                user.save(update_fields=['password'])
                created += 1
            self.user_cache[data['email']] = user
        self.stdout.write(f'Users: {created} created, {len(USERS_DATA) - created} already existed')
        return len(USERS_DATA)

    # ── Languages ─────────────────────────────────────────────────────────

    def _create_languages(self):
        created = 0
        for data in USERS_DATA:
            user = self._get_user(data['email'])
            for code, name, is_native, proficiency in data.get('languages', []):
                _, was_created = UserLanguage.objects.get_or_create(
                    user=user,
                    language_code=code,
                    defaults=dict(
                        language_name=name,
                        is_native=is_native,
                        proficiency=proficiency,
                    ),
                )
                if was_created:
                    created += 1
        self.stdout.write(f'Languages: {created} created')
        return created

    # ── Follows ───────────────────────────────────────────────────────────

    def _create_follows(self):
        created = 0
        # Mutual
        for email_a, email_b in MUTUAL_FOLLOWS:
            user_a = self._get_user(email_a)
            user_b = self._get_user(email_b)
            for follower, followed in [(user_a, user_b), (user_b, user_a)]:
                _, was_created = Follow.objects.get_or_create(
                    follower=follower, followed=followed,
                )
                if was_created:
                    created += 1
        # Unidirectional
        for email_a, email_b in UNI_FOLLOWS:
            _, was_created = Follow.objects.get_or_create(
                follower=self._get_user(email_a),
                followed=self._get_user(email_b),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Follows: {created} created')
        return created

    # ── Friendships ───────────────────────────────────────────────────────

    def _create_friendships(self):
        created = 0
        for email_a, email_b in FRIENDSHIPS_DATA:
            _, was_created = Friendship.objects.get_or_create(
                user1=self._get_user(email_a),
                user2=self._get_user(email_b),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Friendships: {created} created')
        return created

    # ── Friend requests ───────────────────────────────────────────────────

    def _create_friend_requests(self):
        created = 0
        for from_email, to_email, status, message in FRIEND_REQUESTS_DATA:
            _, was_created = FriendRequest.objects.get_or_create(
                from_user=self._get_user(from_email),
                to_user=self._get_user(to_email),
                defaults=dict(status=status, message=message),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Friend requests: {created} created')
        return created

    # ── Posts & Hashtags ──────────────────────────────────────────────────

    def _create_posts(self):
        created = 0
        post_objects = []
        now = timezone.now()
        for i, data in enumerate(POSTS_DATA):
            author = self._get_user(data['author_email'])
            post, was_created = Post.objects.get_or_create(
                author=author,
                content=data['content'],
                defaults=dict(
                    post_type=data['post_type'],
                    title=data.get('title', ''),
                ),
            )
            if was_created:
                # Space out creation times so they appear in order
                Post.objects.filter(pk=post.pk).update(
                    created_at=now - timedelta(hours=len(POSTS_DATA) - i),
                )
                post.refresh_from_db()
                created += 1
                # Hashtags
                for tag_name in data.get('hashtags', []):
                    hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
                    PostHashtag.objects.get_or_create(post=post, hashtag=hashtag)
            post_objects.append(post)
        self.stdout.write(f'Posts: {created} created')
        return len(POSTS_DATA), post_objects

    def _count_hashtags(self):
        count = Hashtag.objects.count()
        self.stdout.write(f'Hashtags: {count} total')
        return count

    # ── Reactions ─────────────────────────────────────────────────────────

    def _create_reactions(self, post_objects):
        created = 0
        for post_idx, reactor_email, rtype in REACTIONS_DATA:
            if post_idx >= len(post_objects):
                continue
            _, was_created = Reaction.objects.get_or_create(
                user=self._get_user(reactor_email),
                post=post_objects[post_idx],
                defaults=dict(reaction_type=rtype),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Reactions: {created} created')
        return created

    # ── Comments ──────────────────────────────────────────────────────────

    def _create_comments(self, post_objects):
        created = 0
        comment_objects = []
        for post_idx, commenter_email, content, parent_idx in COMMENTS_DATA:
            if post_idx >= len(post_objects):
                comment_objects.append(None)
                continue
            parent = None
            if parent_idx is not None and parent_idx < len(comment_objects):
                parent = comment_objects[parent_idx]
            comment, was_created = Comment.objects.get_or_create(
                post=post_objects[post_idx],
                author=self._get_user(commenter_email),
                content=content,
                defaults=dict(parent=parent),
            )
            if was_created:
                created += 1
            comment_objects.append(comment)
        self.stdout.write(f'Comments: {created} created')
        return created

    # ── Groups ────────────────────────────────────────────────────────────

    def _create_groups(self):
        created_groups = 0
        created_memberships = 0
        created_posts = 0
        for data in GROUPS_DATA:
            creator = self._get_user(data['creator_email'])
            group, was_created = Group.objects.get_or_create(
                name=data['name'],
                defaults=dict(
                    group_type=data['group_type'],
                    description=data.get('description', ''),
                    country=data.get('country', ''),
                    created_by=creator,
                ),
            )
            if was_created:
                created_groups += 1
            # Members
            for member_email, role in data.get('members', []):
                _, mc = GroupMembership.objects.get_or_create(
                    group=group,
                    user=self._get_user(member_email),
                    defaults=dict(role=role),
                )
                if mc:
                    created_memberships += 1
            # Group posts
            for author_email, content in data.get('posts', []):
                _, pc = GroupPost.objects.get_or_create(
                    group=group,
                    author=self._get_user(author_email),
                    content=content,
                )
                if pc:
                    created_posts += 1
        self.stdout.write(
            f'Groups: {created_groups} created, '
            f'{created_memberships} memberships, '
            f'{created_posts} group posts'
        )
        return created_groups

    # ── Stories ───────────────────────────────────────────────────────────

    def _create_stories(self):
        created = 0
        story_objects = []
        now = timezone.now()
        for i, data in enumerate(STORIES_DATA):
            user = self._get_user(data['user_email'])
            story, was_created = Story.objects.get_or_create(
                user=user,
                text=data['text'],
                defaults=dict(
                    background_color=data.get('background_color', '#2EA3F2'),
                    expires_at=now + timedelta(hours=24),
                ),
            )
            if was_created:
                # Stagger creation times
                Story.objects.filter(pk=story.pk).update(
                    created_at=now - timedelta(hours=len(STORIES_DATA) - i),
                )
                story.refresh_from_db()
                created += 1
            story_objects.append(story)
        self.stdout.write(f'Stories: {created} created')
        return created, story_objects

    # ── Highlights ────────────────────────────────────────────────────────

    def _create_highlights(self, story_objects):
        created = 0
        for data in HIGHLIGHTS_DATA:
            user = self._get_user(data['user_email'])
            highlight, was_created = StoryHighlight.objects.get_or_create(
                user=user,
                name=data['name'],
            )
            if was_created:
                created += 1
                for order, idx in enumerate(data.get('story_indices', [])):
                    if idx < len(story_objects):
                        StoryHighlightItem.objects.get_or_create(
                            highlight=highlight,
                            story=story_objects[idx],
                            defaults=dict(order=order),
                        )
        self.stdout.write(f'Story highlights: {created} created')
        return created

    # ── Conversations & Messages ──────────────────────────────────────────

    def _create_conversations(self):
        created_convs = 0
        created_msgs = 0
        now = timezone.now()
        for data in CONVERSATIONS_DATA:
            user1 = self._get_user(data['user1_email'])
            user2 = self._get_user(data['user2_email'])
            # Ensure consistent ordering: lower pk first
            if user1.pk > user2.pk:
                user1, user2 = user2, user1
            conv, was_created = Conversation.objects.get_or_create(
                user1=user1, user2=user2,
            )
            if was_created:
                created_convs += 1
            # Messages
            for j, (sender_email, content) in enumerate(data['messages']):
                sender = self._get_user(sender_email)
                _, mc = Message.objects.get_or_create(
                    conversation=conv,
                    sender=sender,
                    content=content,
                )
                if mc:
                    # Space messages within a conversation
                    Message.objects.filter(pk=_.pk).update(
                        created_at=now - timedelta(
                            hours=len(data['messages']) - j,
                        ),
                    )
                    created_msgs += 1
        self.stdout.write(
            f'Conversations: {created_convs} created, {created_msgs} messages'
        )
        return created_convs

    # ── Events ────────────────────────────────────────────────────────────

    def _create_events(self):
        created_events = 0
        created_rsvps = 0
        now = timezone.now()
        for data in EVENTS_DATA:
            organizer = self._get_user(data['organizer_email'])
            start_date = now + timedelta(days=data['days_ahead'])
            event, was_created = Event.objects.get_or_create(
                title=data['title'],
                organizer=organizer,
                defaults=dict(
                    event_type=data['event_type'],
                    description=data['description'],
                    location=data.get('location', ''),
                    country=data.get('country', ''),
                    start_date=start_date,
                    end_date=start_date + timedelta(hours=3),
                    is_virtual=data.get('is_virtual', False),
                    meeting_link=data.get('meeting_link', ''),
                ),
            )
            if was_created:
                created_events += 1
            for rsvp_email, status in data.get('rsvps', []):
                _, rc = RSVP.objects.get_or_create(
                    event=event,
                    user=self._get_user(rsvp_email),
                    defaults=dict(status=status),
                )
                if rc:
                    created_rsvps += 1
        self.stdout.write(
            f'Events: {created_events} created, {created_rsvps} RSVPs'
        )
        return created_events

    # ── Proposals ─────────────────────────────────────────────────────────

    def _create_proposals(self):
        created_proposals = 0
        created_participants = 0
        now = timezone.now()
        for data in PROPOSALS_DATA:
            author = self._get_user(data['author_email'])
            group = Group.objects.filter(name=data['group_name']).first()
            proposal, was_created = Proposal.objects.get_or_create(
                title=data['title'],
                author=author,
                defaults=dict(
                    group=group,
                    proposal_type=data['proposal_type'],
                    description=data['description'],
                    date=(now + timedelta(days=data['days_ahead'])).date(),
                ),
            )
            if was_created:
                created_proposals += 1
            for p_email in data.get('participants', []):
                _, pc = ProposalParticipant.objects.get_or_create(
                    proposal=proposal,
                    user=self._get_user(p_email),
                )
                if pc:
                    created_participants += 1
        self.stdout.write(
            f'Proposals: {created_proposals} created, '
            f'{created_participants} participants'
        )
        return created_proposals

    # ── Job postings ──────────────────────────────────────────────────────

    def _create_job_postings(self):
        created = 0
        # Ensure categories exist
        cat_cache = {}
        for data in JOB_CATEGORIES_DATA:
            cat, _ = JobCategory.objects.get_or_create(
                name=data['name'],
                defaults=dict(icon=data.get('icon', ''), order=data.get('order', 0)),
            )
            cat_cache[data['name']] = cat
        for data in JOB_POSTINGS_DATA:
            author = self._get_user(data['author_email'])
            category = cat_cache.get(data.get('category_name'))
            _, was_created = JobPosting.objects.get_or_create(
                title=data['title'],
                author=author,
                defaults=dict(
                    description=data['description'],
                    category=category,
                    company_name=data.get('company_name', ''),
                    job_type=data.get('job_type', 'full_time'),
                    modality=data.get('modality', 'on_site'),
                    experience_level=data.get('experience_level', 'any'),
                    salary_type=data.get('salary_type', 'negotiable'),
                    salary_min=data.get('salary_min'),
                    salary_max=data.get('salary_max'),
                    salary_currency=data.get('salary_currency', 'USD'),
                    location_city=data.get('location_city', ''),
                    location_country=data.get('location_country', ''),
                    skills=data.get('skills', ''),
                    requirements=data.get('requirements', ''),
                    contact_email=data.get('contact_email', ''),
                ),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Job postings: {created} created ({len(JOB_CATEGORIES_DATA)} categories)')
        return created

    # ── Career tips ───────────────────────────────────────────────────────

    def _create_career_tips(self):
        created = 0
        tip_cat_cache = {}
        for data in TIP_CATEGORIES_DATA:
            cat, _ = TipCategory.objects.get_or_create(
                name=data['name'],
                defaults=dict(order=data.get('order', 0)),
            )
            tip_cat_cache[data['name']] = cat
        for data in CAREER_TIPS_DATA:
            author = self._get_user(data['author_email'])
            category = tip_cat_cache.get(data.get('category_name'))
            _, was_created = CareerTip.objects.get_or_create(
                title=data['title'],
                author=author,
                defaults=dict(
                    content=data['content'],
                    category=category,
                ),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Career tips: {created} created')
        return created

    # ── Professional profiles ─────────────────────────────────────────────

    def _create_professional_profiles(self):
        created = 0
        for data in PROFESSIONAL_PROFILES_DATA:
            user = self._get_user(data['user_email'])
            cat = None
            if data.get('category_name'):
                cat = JobCategory.objects.filter(name=data['category_name']).first()
            _, was_created = ProfessionalProfile.objects.get_or_create(
                user=user,
                defaults=dict(
                    headline=data['headline'],
                    summary=data.get('summary', ''),
                    availability=data.get('availability', 'available'),
                    years_of_experience=data.get('years_of_experience'),
                    education=data.get('education', ''),
                    skills=data.get('skills', ''),
                    services=data.get('services', ''),
                    category=cat,
                ),
            )
            if was_created:
                created += 1
        self.stdout.write(f'Professional profiles: {created} created')
        return created

    # ── Link real users to demo users ─────────────────────────────────────

    def _link_real_users(self):
        """
        Make all existing non-demo users mutually follow some demo users
        and join the main group, so they see demo content in their feed.
        """
        demo_emails = {d['email'] for d in USERS_DATA}
        real_users = User.objects.exclude(
            email__endswith=f'@{DEMO_DOMAIN}',
        ).exclude(is_superuser=True)

        if not real_users.exists():
            self.stdout.write('No real users found to link.')
            return 0

        # Key demo users that real users will follow (and be followed by)
        key_demo_emails = [
            'matias@demo.iddam.app',
            'david@demo.iddam.app',
            'daniela@demo.iddam.app',
            'lucas@demo.iddam.app',
            'pablo@demo.iddam.app',
            'facundo@demo.iddam.app',
            'sarah@demo.iddam.app',
            'genesis@demo.iddam.app',
            'camila@demo.iddam.app',
            'jose@demo.iddam.app',
            'ana@demo.iddam.app',
            'maria@demo.iddam.app',
        ]

        created_follows = 0
        created_memberships = 0
        created_friendships = 0
        created_conversations = 0
        created_messages = 0

        for real_user in real_users:
            for demo_email in key_demo_emails:
                demo_user = self._get_user(demo_email)
                # Mutual follow
                for follower, followed in [(real_user, demo_user), (demo_user, real_user)]:
                    _, was_created = Follow.objects.get_or_create(
                        follower=follower, followed=followed,
                    )
                    if was_created:
                        created_follows += 1

            # Add real user as friend of a couple demo users
            for demo_email in ['matias@demo.iddam.app', 'david@demo.iddam.app']:
                demo_user = self._get_user(demo_email)
                u1, u2 = (real_user, demo_user) if real_user.pk < demo_user.pk else (demo_user, real_user)
                _, was_created = Friendship.objects.get_or_create(user1=u1, user2=u2)
                if was_created:
                    created_friendships += 1

            # Add real user to the main general group
            general_group = Group.objects.filter(name='General COGWA Jóvenes').first()
            if general_group:
                _, was_created = GroupMembership.objects.get_or_create(
                    group=general_group, user=real_user,
                    defaults=dict(role='member'),
                )
                if was_created:
                    created_memberships += 1

            # Create a welcome chat conversation with matias
            matias = self._get_user('matias@demo.iddam.app')
            u1, u2 = (real_user, matias) if real_user.pk < matias.pk else (matias, real_user)
            conv, was_created = Conversation.objects.get_or_create(
                user1=u1, user2=u2,
            )
            if was_created:
                created_conversations += 1
                Message.objects.create(
                    conversation=conv,
                    sender=matias,
                    content='Hola! Bienvenido a IDDAM Chat. Soy Matías, si necesitas algo no dudes en escribirme!',
                )
                created_messages += 1

        self.stdout.write(
            f'Real user links: {created_follows} follows, '
            f'{created_friendships} friendships, '
            f'{created_memberships} group memberships, '
            f'{created_conversations} conversations'
        )
        return created_follows
