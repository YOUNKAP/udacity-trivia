import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#Function to paginate question
def paginate_questions(request, selection):
    #Get page
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE 
    end = start + QUESTIONS_PER_PAGE 
    #Format question
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

    
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    def after_request(response):

        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])

    def retrieve_categories():

        categories  = Category.query.order_by(Category.id).all()

        category_available = dict()

        for category in categories :

            category_available[category.id] = category.type

            if list(category_available.keys()) == []:

                abort (404)

        return jsonify(
            {
                "success": True,

                "categories": category_available ,
                
               "total_categories": len(Category.query.all()),
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
   
    @app.route('/questions', methods=['GET'])

    def retrieve_questions():

        selection = Question.query.order_by(Question.id).all()

        current_questions  = paginate_questions(request, selection)

        if len(current_questions) == 0:

            abort(404)

        categories  = Category.query.order_by(Category.id).all()

        current_category = dict()

        for category in categories:

            current_category[category.id] = category.type

        return jsonify(
            {
                "success": True,
                'questions': current_questions  ,
                'total_questions': len(selection),
                'categories': current_category
            }
        )


    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    """

   


    @app.route("/questions/<int:question_id>", methods=["DELETE"])

    def delete_question(question_id):

        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:

                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()

            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )
        except :

            abort(422)
   

    """
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():

        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer=new_answer, category =new_category, difficulty =  new_difficulty )
            question.insert()

            selection = Question.query.order_by(Question.id).all()

            current_questions  = paginate_questions(request, selection)

            return jsonify(
                {   "success": True,
                    "created" : question.id ,
                    "questions" : current_questions,
                    "question": question.format(), 
                    "total_questions" : len(Question.query.all())
                }
            )

        except:
            abort(422)

    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
   

    @app.route('/search', methods=['POST'])

    def search():

        body = request.get_json()

        search = body.get("search", None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search)).all()
                )
               
                current_questions = paginate_books(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(selection),
                    }
                )
            else:

                abort(404)

        except:
            abort(422)


    """
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    """


    @app.route('/categories/<int:id>/questions')

    def retrieve_questions_by_category(id):

        category  = Category.query.filter_by(id=id).one_or_none()

        if  category is None :

            abort(400)

     
        selection = Question.query.filter_by(category=category.id).all()

   
        current_questions = paginate_questions(request, selection)


        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
        })

    """
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """

    @app.route('/quizzes', methods=['POST'])

    def retrieve_quizzes_question_randomly():

        body = request.get_json()

      
        previous_questions = body.get('previous_questions')

 
        given_category = body.get('quiz_category')


    
        if ((given_category is None) or ( previous_questions is None)):

            abort(400)

 
        if (given_category['id'] == 0):

            questions = Question.query.all()
    
        else:

            questions = Question.query.filter_by(category=given_category['id']).all()


        def retrieve_one_question_random():

            index = random.randint(0, len(questions) -1 )

            return questions[index]

  
        def check_available (question):

            available  = False

            for quest  in previous_questions :

                if (question.id == quest):

                    available  = True

            return available

        question = retrieve_one_question_random()

       
        while (check_available(question)):

            question = retrieve_one_question_random()

    
            if (len(previous_questions) == len(questions) ):

                return jsonify({
                    'success': True
                })

        
        return jsonify({

            'success': True,

            'question': question.format()
        })


    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
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



"""

#Retrieves categories
curl -X GET http://127.0.0.1:5000/categories

#Retrieve questions
curl -X GET http://127.0.0.1:5000/questions
curl -X GET http://127.0.0.1:5000/questions?page=1
curl -X GET http://127.0.0.1:5000/questions?page=1000

POST ''

curl -X POST http://127.0.0.1:5000/quizzes

#Delete a question

#curl -X DELETE http://127.0.0.1:5000/questions/1 
#curl -X DELETE http://127.0.0.1:5000/questions/1000


#Create a new Question
curl -X POST -H "Content-Type: application/json" -d '{"question":"What is your name", "answer":"My name is ", "category":"1", "difficulty": "4"}' http://127.0.0.1:5000/questions



curl -X POST -H "Content-Type: application/json" -d '{'previous_questions': [1, 4, 20, 15], quiz_category': 'current category'}' http://127.0.0.1:5000/quizzes

#5 Run yor app
# For Mac/Linux
export FLASK_APP=flaskr
export FLASK_ENV=development
# Make sure to run this command from the project directory (not from the flaskr)
flask run
"""




