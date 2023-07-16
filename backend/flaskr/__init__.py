import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app) 

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    def paginate_questions(page, selection):
        
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories",methods=['GET'])
    def get_categories():
        categories=Category.query.all()
        if categories is None:
            abort(404)
        else:
            return (jsonify({
                'success':True,
                'categories': {category.id: category.type for category in categories}
            }))

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions",methods=['GET'])
    def get_questions():
        page = request.args.get("page", 1, type=int)
        all_questions=Question.query.all()
        
        if all_questions is None:
            abort(404)
        else:
            paginated_questions=paginate_questions(page,all_questions)
        categories=Category.query.all()

        if categories is None:
            abort(404)

        return jsonify(
            {
                'success':True,
                'questions':paginated_questions,
                'total_questions':len(all_questions),
                'categories': {category.id: category.type for category in categories},
                'current_category': None
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions",methods=['POST'])
    def save_question():
        request_body = request.get_json()
        question=request_body.get("question",None)
        answer=request_body.get("answer",None)
        difficulty=request_body.get("difficulty",None)
        category=request_body.get("category",None)

        try:
            question = Question(question=question, answer=answer,difficulty= difficulty,category=category )
            question.insert()

            all_questions = Question.query.order_by(Question.id).all()
            page = request.args.get("page", 1, type=int)
            current_questions = paginate_questions(page, all_questions)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(all_questions),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id:int):
        questions_for_category=Question.query.filter_by(category=category_id)
        if questions_for_category is None:
            abort(404)
        else:
            try:
                category=Category.query.get(category_id)
                if category is None:
                    abort(404)
                else:
                    return jsonify(
                        {
                            "questions":[question.format() for question in questions_for_category],
                            "totalQuestions": questions_for_category.count(),
                            "currentCategory": category.type
                        }
                    )
            except:
                abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

