from django.conf import settings
from django.db import models

HIGHLIGHT_COLORS = [
    ('#FDE047', 'Amarillo'), ('#93C5FD', 'Azul'), ('#86EFAC', 'Verde'),
    ('#FCA5A5', 'Rojo'), ('#C4B5FD', 'Morado'), ('#FDBA74', 'Naranja'),
    ('#F9A8D4', 'Rosa'), ('#5EEAD4', 'Turquesa'),
]


# ─── Read-Only Bible Data ────────────────────────────────────────────
class BibleBook(models.Model):
    TESTAMENT_CHOICES = [('AT', 'Antiguo Testamento'), ('NT', 'Nuevo Testamento')]

    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    slug = models.SlugField(unique=True)
    testament = models.CharField(max_length=2, choices=TESTAMENT_CHOICES)
    order = models.PositiveSmallIntegerField(unique=True)
    total_chapters = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class BibleChapter(models.Model):
    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE, related_name='chapters')
    number = models.PositiveSmallIntegerField()
    total_verses = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('book', 'number')
        ordering = ['book__order', 'number']

    def __str__(self):
        return f"{self.book.name} {self.number}"


class BibleVerse(models.Model):
    chapter = models.ForeignKey(BibleChapter, on_delete=models.CASCADE, related_name='verses')
    number = models.PositiveSmallIntegerField()
    text = models.TextField()

    class Meta:
        unique_together = ('chapter', 'number')
        ordering = ['chapter__book__order', 'chapter__number', 'number']

    def __str__(self):
        return f"{self.chapter.book.name} {self.chapter.number}:{self.number}"


# ─── User Bible Data ────────────────────────────────────────────────
class HighlightCategory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='highlight_categories',
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#FDE047')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.user})"


class VerseHighlight(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='verse_highlights',
    )
    start_verse = models.ForeignKey(
        BibleVerse, on_delete=models.CASCADE, related_name='highlights_start',
    )
    end_verse = models.ForeignKey(
        BibleVerse, on_delete=models.CASCADE, related_name='highlights_end',
    )
    color = models.CharField(max_length=7, default='#FDE047')
    category = models.ForeignKey(
        HighlightCategory, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='highlights',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Resaltado: {self.start_verse} - {self.end_verse}"


class VerseAnnotation(models.Model):
    highlight = models.OneToOneField(
        VerseHighlight, on_delete=models.CASCADE, related_name='annotation',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='verse_annotations',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BibleTag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bible_tags',
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#93C5FD')

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class HighlightTag(models.Model):
    highlight = models.ForeignKey(
        VerseHighlight, on_delete=models.CASCADE, related_name='tags',
    )
    tag = models.ForeignKey(BibleTag, on_delete=models.CASCADE, related_name='highlights')

    class Meta:
        unique_together = ('highlight', 'tag')


class FavoriteVerse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorite_verses',
    )
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']


class ReadingProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reading_progress',
    )
    book = models.ForeignKey(BibleBook, on_delete=models.CASCADE)
    chapter = models.ForeignKey(BibleChapter, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'book', 'chapter')


class StudyNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bible_study_notes',
    )
    category = models.ForeignKey(
        HighlightCategory, on_delete=models.SET_NULL, null=True, blank=True,
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


# ─── Study Folders ─────────────────────────────────────────────────

class StudyFolder(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='study_folders',
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#93C5FD')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.user})"


# ─── Study Books / PDF ─────────────────────────────────────────────

BOOK_CATEGORY_CHOICES = [
    ('teologia', 'Teología'),
    ('profecia', 'Profecía'),
    ('historia', 'Historia'),
    ('devocional', 'Devocional'),
    ('apologetica', 'Apologética'),
    ('biblia', 'Estudio Bíblico'),
    ('liderazgo', 'Liderazgo'),
    ('otro', 'Otro'),
]


class StudyBook(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='study_books',
    )
    title = models.CharField(max_length=300)
    author_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(
        max_length=20, choices=BOOK_CATEGORY_CHOICES, blank=True,
    )
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/covers/%Y/%m/', blank=True)
    pdf_key = models.CharField(max_length=500, blank=True)
    pdf_filename = models.CharField(max_length=255, blank=True)
    total_pages = models.PositiveIntegerField(default=0)
    current_page = models.PositiveIntegerField(default=0)
    daily_goal = models.PositiveIntegerField(default=10)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} ({self.user})"

    @property
    def progress_percent(self):
        if self.total_pages == 0:
            return 0
        return min(100, round(self.current_page / self.total_pages * 100))


class BookReadingLog(models.Model):
    book = models.ForeignKey(
        StudyBook, on_delete=models.CASCADE, related_name='reading_logs',
    )
    date = models.DateField(auto_now_add=True)
    page_start = models.PositiveIntegerField()
    page_end = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.book.title}: pp. {self.page_start}-{self.page_end}"

    @property
    def pages_read(self):
        return self.page_end - self.page_start


class BookPageNote(models.Model):
    book = models.ForeignKey(
        StudyBook, on_delete=models.CASCADE, related_name='page_notes',
    )
    page_number = models.PositiveIntegerField()
    content = models.TextField()
    category = models.ForeignKey(
        HighlightCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='book_page_notes',
    )
    folder = models.ForeignKey(
        StudyFolder, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='book_page_notes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_number', 'created_at']

    def __str__(self):
        return f"{self.book.title} p.{self.page_number}: {self.content[:50]}"


class BookHighlight(models.Model):
    book = models.ForeignKey(
        StudyBook, on_delete=models.CASCADE, related_name='highlights',
    )
    category = models.ForeignKey(
        HighlightCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='book_highlights',
    )
    folder = models.ForeignKey(
        StudyFolder, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='book_highlights',
    )
    page_number = models.PositiveIntegerField()
    selected_text = models.TextField()
    rect_data = models.JSONField(default=list)
    annotation = models.TextField(blank=True)
    title = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=7, default='#FDE047')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number', 'created_at']

    def __str__(self):
        return f"{self.book.title} p.{self.page_number}: {self.selected_text[:50]}"


class BookSubtitle(models.Model):
    book = models.ForeignKey(
        StudyBook, on_delete=models.CASCADE, related_name='subtitles',
    )
    page_number = models.PositiveIntegerField()
    y_position = models.FloatField(default=0.5)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['page_number', 'y_position']

    def __str__(self):
        return f"{self.book.title} p.{self.page_number}: {self.title}"
