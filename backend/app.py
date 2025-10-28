import flask
# import database

app = flask.Flask(__name__, template_folder='templates')

# Home Page
@app.route('/', methods=['GET'])
def home_page():
    # NOTE: We probably want a list of dicts here
    # restaurants = database.get_restaurant_cards()
    restaurants = [True, []]  # Placeholder
    if restaurants[0] is False:
        html_code = flask.render_template('error.html',
            message=restaurants[1])
        response = flask.make_response(html_code)
        return response
    html_code = flask.render_template('home.html',
        restaurants=restaurants[1])
    response = flask.make_response(html_code)
    return response

@app.route('/search_form', methods=['GET'])
def search_form():
    html_code = flask.render_template('search_box.html')
    response = flask.make_response(html_code)
    return response

if __name__ == "__main__":
    app.run(debug=True)