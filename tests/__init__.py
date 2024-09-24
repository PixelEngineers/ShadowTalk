from django.test import TestCase

class Database(TestCase):
    def blank(self):
        self.assertEqual(True, True)