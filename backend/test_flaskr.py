import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(setup_db_flag=False)
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "admin", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """    
    Write at least one test for each test for successful operation and for expected errors.
    """
    # def test_create_categories(self):

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]))

    def test_post_questions_and_check_counts(self):
        total_questions_before_Insert=len(Question.query.all())
        for counter in range(10):
            question=Question(question="Question " + str(counter), answer="Answer " + str(counter),category="1",difficulty="1")
            request=question.format()            
            res=self.client().post("/questions",json=request)
            data=json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertIsNotNone(data["questions"])
        total_questions_after_Insert=len(Question.query.all())
        self.assertEqual(total_questions_before_Insert,total_questions_after_Insert-10)
    
    def test_total_questions_and_categories(self):
        res = self.client().get("/questions")
        data=json.loads(res.data)
        self.assertEqual(data["total_categories"], len( Category.query.all()) )
        self.assertEqual(data["total_questions"],len(Question.query.all()))
    
    def test_get_paginated_questions(self):
        res = self.client().get("/questions?page=1")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(len(data["questions"]), 10)
        res = self.client().get("/questions?page=2")
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(len(data["questions"]), 10)         

    def test_get_paginated_questions_invalid_page(self):
        res = self.client().get("/questions?page=10000")
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        question=Question.query.first()
        if question is not None:
            res=self.client().delete("/questions/" + str(question.id))
            data=json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)
            self.assertIsNone(Question.query.get(question.id))

    def test_delete_invalid_question(self):       
        res=self.client().delete("/questions/999999")
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)        

    def test_search_question(self):  
        # Post a Question     
        question=Question(question="Hello World Question! ", answer="Hello World",category="1",difficulty="1")
        request=question.format()            
        res=self.client().post("/questions",json=request)
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)  
        # If Succesfully inserted, search for same question
        if res.status_code==200:
            res=self.client().post("/questions/search",json={"searchTerm": "Hello World"})
            data=json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data["success"], True)

    def test_questions_by_category(self):
        res=self.client().get("/categories/1/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])

    def test_questions_by_invalid_category(self):
        res=self.client().get("/categories/98899898/questions")
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)        

    def test_quizzes(self):
        res=self.client().post("/quizzes",json={"previous_questions": [], "quiz_category": {"type": "Science","id": "1" }})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
    
    def test_quizzes_invalid_request_type(self):
        res=self.client().get("/quizzes",json={"previous_questions": [], "quiz_category": {"type": "Science","id": "1" }})
        data=json.loads(res.data)
        self.assertEqual(res.status_code, 405)
           


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()