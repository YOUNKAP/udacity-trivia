import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from dotenv import dotenv_values
from dotenv import load_dotenv


config = dotenv_values(".env") 
usr = config['USERNAME']
pwd = config['PASSWORD']



class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            usr , pwd , "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)
        #Sample question
        self.add_new_question = {"id": 14,
                               "question": "In which royal palace would you find the Hall of Mirrors?", 
                               "answer": "The Palace of Versailles", 
                                "category": 3, 
                                "difficulty": 3  
                            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data["total_categories"])



    def test_retrieve_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["categories"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000", json={"difficulty": 3})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")



    """
    def test_delete_question(self):
        res = self.client().delete("/questions/20")
        data = json.loads(res.data)

        question  = Question.query.filter(Question.id == 20).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 20)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(question, None)
    """

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_create_question(self):
        res = self.client().post("/questions", json=self.add_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["question"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(len(data["questions"]), 10)

    """
    def test_405_if_question_creation_not_allowed(self):
        #res = self.client().post("/questions", json=self.add_new_question)
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
    """

    """
    def test_search(self):

        request_data = {'searchTerm': 'this is the term the user is looking for '}

        res = self.client().post('/search', data=json.dumps(request_data),
                                 content_type='application/json')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['matching_questions'])
        self.assertTrue(data['total_questions'])
    """
    """
    def test_404_if_search_fails(self):
        response = self.client().post('/questions',
                                      json={'searchTerm': 'fkklzpzx'})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    """

    def test_retrieve_questions_by_category(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
    

    def test_400_if_retrieve_questions_by_category_fail(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)



    def test_retrieve_quizzes_question_randomly(self):
        request_data = {
            'previous_questions': [1, 4, 20, 15],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }
        res = self.client().post('/quizzes', data=json.dumps(request_data),
                                 content_type='application/json')
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        

    def test_retrieve_quizzes_question_randomly_fail(self):
        res = self.client().post('/quizzes', data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()