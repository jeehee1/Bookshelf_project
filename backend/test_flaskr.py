import os
from typing import Union
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Book

class BookTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '1231', 'localhost:5432', self.database_name)
        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }

        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     self.db.create_all()

    def test_get_paginated_book(self):
        res = self.client().get('/books')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000', json={'rating':1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_update_book_rating(self):
        res = self.client().patch('/books/5', json={'rating':1})
        data = json.loads(res.data)
        book = Book.query.filter(Book.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(book.format()['rating'], 1)

    def test_400_for_failed_update(self):
        res = self.client().patch('/books/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Bad Request')

    def test_delete_book(self):
        res = self.client().delete('/books/15')
        data = json.loads(res.data)
        book = Book.query.filter(Book.id==15).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted_book'], 15)
        self.assertTrue(len(data['books']))
        self.assertTrue(data['total_books'])
        self.assertEqual(book, None)

    def test_422_if_book_does_not_exist(self):
        res = self.client().delete('/books/1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Unprocessable')

    def test_create_new_book(self):
        res = self.client().post('/books', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created_id'])
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/books/30', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'Method Not Allowed')

    def test_search_book_with_results(self):
        res = self.client().post('/books', json={'search':'Novel'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['books']), 4)
        self.assertTrue(data['total_books'])

    def test_search_book_without_results(self):
        res = self.client().post('/books', json={'search':'sjekj'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_books'], 0)
        self.assertEqual(len(data['books']), 0)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()