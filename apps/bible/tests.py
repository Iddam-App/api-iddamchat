from rest_framework import status

from apps.core.test_helpers import AuthenticatedTestCase

from .models import StudyBook, StudyFolder


class StudyFolderTest(AuthenticatedTestCase):
    def test_create_folder(self):
        response = self.client.post('/api/bible/folders/', {
            'name': 'Profecía',
            'color': '#FCA5A5',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_folders(self):
        StudyFolder.objects.create(user=self.user, name='Folder 1')
        StudyFolder.objects.create(user=self.user, name='Folder 2')
        response = self.client.get('/api/bible/folders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class StudyBookTest(AuthenticatedTestCase):
    def test_create_book(self):
        response = self.client.post('/api/bible/books-study/', {
            'title': 'Test Book',
            'author_name': 'Author',
            'category': 'teologia',
            'description': 'A test book',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Book')
        self.assertIn('progress_percent', response.data)

    def test_list_books(self):
        StudyBook.objects.create(user=self.user, title='Book 1')
        StudyBook.objects.create(user=self.user, title='Book 2')
        response = self.client.get('/api/bible/books-study/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_update_book(self):
        book = StudyBook.objects.create(user=self.user, title='Old Title')
        response = self.client.patch(f'/api/bible/books-study/{book.pk}/', {
            'title': 'New Title',
            'daily_goal': 20,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.assertEqual(response.data['daily_goal'], 20)

    def test_delete_book(self):
        book = StudyBook.objects.create(user=self.user, title='To Delete')
        response = self.client.delete(f'/api/bible/books-study/{book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StudyBook.objects.filter(pk=book.pk).exists())

    def test_other_user_cannot_access_book(self):
        other = self.create_user('other')
        book = StudyBook.objects.create(user=other, title='Private Book')
        response = self.client.get(f'/api/bible/books-study/{book.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_progress_percent(self):
        book = StudyBook.objects.create(
            user=self.user, title='Book', total_pages=100, current_page=50,
        )
        response = self.client.get(f'/api/bible/books-study/{book.pk}/')
        self.assertEqual(response.data['progress_percent'], 50)


class BookReadingLogTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.book = StudyBook.objects.create(
            user=self.user, title='Test Book', total_pages=100,
        )

    def test_create_reading_log(self):
        response = self.client.post(
            f'/api/bible/books-study/{self.book.pk}/reading-logs/',
            {'page_start': 1, 'page_end': 25, 'notes': 'Good chapter'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.current_page, 25)

    def test_list_reading_logs(self):
        from .models import BookReadingLog
        BookReadingLog.objects.create(
            book=self.book, page_start=1, page_end=10,
        )
        response = self.client.get(
            f'/api/bible/books-study/{self.book.pk}/reading-logs/',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class BookHighlightTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.book = StudyBook.objects.create(
            user=self.user, title='Test Book',
        )

    def test_create_highlight(self):
        response = self.client.post(
            f'/api/bible/books-study/{self.book.pk}/highlights/',
            {
                'page_number': 5,
                'selected_text': 'Important text',
                'color': '#FCA5A5',
                'rect_data': '[]',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_highlight_with_annotation(self):
        response = self.client.post(
            f'/api/bible/books-study/{self.book.pk}/highlights/',
            {
                'page_number': 3,
                'selected_text': 'Key passage',
                'annotation': 'This is very relevant',
                'title': 'Important',
                'rect_data': [],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['annotation'], 'This is very relevant')

    def test_delete_highlight(self):
        from .models import BookHighlight
        hl = BookHighlight.objects.create(
            book=self.book, page_number=5, selected_text='Test',
        )
        response = self.client.delete(
            f'/api/bible/books-study/highlights/{hl.pk}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class BookPageNoteTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.book = StudyBook.objects.create(
            user=self.user, title='Test Book',
        )

    def test_create_page_note(self):
        response = self.client.post(
            f'/api/bible/books-study/{self.book.pk}/page-notes/',
            {'page_number': 10, 'content': 'My note'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_page_note(self):
        from .models import BookPageNote
        note = BookPageNote.objects.create(
            book=self.book, page_number=10, content='Original',
        )
        response = self.client.patch(
            f'/api/bible/books-study/page-notes/{note.pk}/',
            {'content': 'Updated'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated')


class BookSubtitleTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.book = StudyBook.objects.create(
            user=self.user, title='Test Book',
        )

    def test_create_subtitle(self):
        response = self.client.post(
            f'/api/bible/books-study/{self.book.pk}/subtitles/',
            {'page_number': 5, 'title': 'Chapter 1', 'y_position': 0.3},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_subtitle(self):
        from .models import BookSubtitle
        sub = BookSubtitle.objects.create(
            book=self.book, page_number=5, title='To Delete',
        )
        response = self.client.delete(
            f'/api/bible/books-study/subtitles/{sub.pk}/',
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
