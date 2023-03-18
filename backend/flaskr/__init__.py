import os
from flask import Flask, request, abort, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def load_categories():
        try: 
            return jsonify(
                categories = [category.type for category in Category.query.all()]

                ,success = True)
        except Exception:
            abort(405)

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
    def paginate(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        paginated_questions = [question.format() for question in questions]

        return paginated_questions[start:end]

    @app.route('/questions', methods=['GET'])
    def index():

        try:
            formatted_questions = paginate(request, Question.query.all())
            category_list = [category.format() for category in Category.query.all()]
            
            if len(formatted_questions) == 0:
                abort(404)
        except Exception:
            abort(404)

        return jsonify(
            questions=formatted_questions,
            total_questions=len(formatted_questions),
            categories=category_list

            ,success = True
        )
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id: int):
        
        question = Question.query.filter_by(id=id).one_or_none()
        if question is None:
            abort(404)
        question.delete()
        db.session.commit()
        
        return jsonify(success = True), 201

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()
        new_question = Question(
            question=data['question'], 
            answer=data['answer'], 
            difficulty=data['difficulty'], 
            category=data['category'])
        db.session.add(new_question)
        db.session.commit()
        return jsonify(success = True)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    # TODO: Not working yet, troubleshoot
    @app.route('/search', methods=['POST'])
    def search():
        data = request.get_json()
        question_list = Question.query.all()
        result_list = []

        for question in question_list:
            if data['searchTerm'].lower() in question.question.lower():
                result_list.append(question.format())

        if len(result_list) > 0:
            return jsonify(
                questions = result_list,
                total_questions = len(result_list)

                ,success = True
            )
        else:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_category(id: int):
        formatted_questions = paginate(request, Question.query.filter_by(category=id))
        formatted_categories = [category.format() for category in Category.query.all()]
        if len(formatted_categories) == 0:
            abort(404)
        
        return jsonify(
            questions = formatted_questions,
            total_questions = len(formatted_questions),
            categories = formatted_categories,
            current_category = id

            ,success = True
        )

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
    @app.route('/quizzes', methods=['POST'])
    def play():
        
        data = request.get_json()
        quiz_category = data['quiz_category']
        prev_question = data['previous_questions']
        
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()

        # How to keep track of which indexes have been checked?        
        rand_index = random.randint(0, len(questions)-1)
        next_question = questions[rand_index]

        return jsonify({
            'question': next_question.format(),
            'previousQuestion': prev_question

            ,'success': True
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400
    
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Method not allowed"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable entity"
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500
    
    return app