import connexion
from flask import render_template
from users import read_all, create, read_one, update, delete
from database import setup_database

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")

flask_app = app.app
flask_app.config['DEBUG'] = True

@app.route("/")
def home():
    return render_template("home.html")

# Initialize the database
setup_database()

# Define the routes
app.add_url_rule('/users', 'read_all', read_all, methods=['GET'])
app.add_url_rule('/users', 'create', create, methods=['POST'])
app.add_url_rule('/users/<int:userId>', 'read_one', read_one, methods=['GET'])
app.add_url_rule('/users/<int:userId>', 'update', update, methods=['PUT'])
app.add_url_rule('/users/<int:userId>', 'delete', delete, methods=['DELETE'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
