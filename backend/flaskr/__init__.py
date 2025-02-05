import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None, setup_db_flag=True):
    # create and configure the app
    app = Flask(__name__)
    # added this setup_db_flag because test class was also setting up the db 
    # and was throwing exception A 'SQLAlchemy' instance has already been registered on this Flask app. 
    # Import and use that instance instead.
    if setup_db_flag==True:
        setup_db(app) 

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    Use the after_request decorator to set Access-Control-Allow
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
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        return response

    def paginate_questions(page, selection):
        
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        return current_questions
    
    """    
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
            if len(paginated_questions) == 0:
                abort(404)
        
        categories=Category.query.all()

        if categories is None:
            abort(404)

        return jsonify(
            {
                'success':True,
                'questions':paginated_questions,
                'total_questions':len(all_questions),
                'categories': {category.id: category.type for category in categories},
                'current_category': "",
                'total_categories':len(categories)
            }
        )

    """    
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>",methods=['DELETE'])
    def delete_question(question_id:int):
        question_to_be_deleted=Question.query.get(question_id)
        if question_to_be_deleted is None:
            abort(404)
        else:
            try:
                question_to_be_deleted.delete()
                return jsonify(
                    {
                        'success':True
                    }
                )
            except:
                abort(422)       

    """    
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
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.   

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search",methods=['POST'])
    def search_question():
        try:
            request_body=request.get_json();
            searchTerm=request_body.get('searchTerm')
            searchResults=Question.query.filter(Question.question.ilike('%'+ searchTerm +'%'))

            return jsonify(
                {
                    "success":True,
                    "questions":[question.format() for question in searchResults],
                    "totalQuestions": len(Question.query.all()),
                    "currentCategory": ""
                }
            )
        except:
            abort(422)

    """    
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
                            "success":True,
                            "questions":[question.format() for question in questions_for_category],
                            "totalQuestions": questions_for_category.count(),
                            "currentCategory": category.type
                        }
                    )
            except:
                abort(422)

    """    
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes",methods=['POST'])
    def get_questions_for_quiz():
        request_body = request.get_json()
        quiz_category=request_body.get("quiz_category",None)
        category_id=quiz_category.get("id","None")
        previous_questions=request_body.get("previous_questions",None)
        if category_id is None:
            abort(404)
        else:
            try:
                if category_id!=0:
                    questions=Question.query.filter(Question.category==int(category_id)).filter(~Question.id.in_(previous_questions)).all()
                else:
                    questions=Question.query.filter(~Question.id.in_(previous_questions)).all()   
                
                if len(questions)!=0:
                    list_of_question_ids=[q.id for q in questions]
                    random_question_id=random.choice(list_of_question_ids)
                    return jsonify(
                        {
                            "success":True,
                            "question":[q.format() for q in questions if q.id==random_question_id][0]
                        }
                    )
                else:
                    return jsonify(
                        {
                            "success":True,
                            "question":""
                        }                
                    )
            except:
                abort(422)

    """    
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    
    return app

