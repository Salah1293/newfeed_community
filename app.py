from flask import Flask, request, jsonify
from config import db_config
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)



#DB connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        return None



# Function to centralize database connection logic and query execution
def execute_query(query, params=None):
    conn = get_db_connection()
    if conn is None:
        return None  

    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()  
            return result
        else:
            conn.commit()  
            return cursor.rowcount  

    except Error as e:
        return None  
    finally:
        cursor.close() 
        conn.close()  


# List all posts
@app.route('/posts', methods=['GET'])
def get_all_posts():
    try:
        posts = execute_query('SELECT * FROM Posts')  
        if posts is None:  
            return jsonify({'error': 'No posts retrieved'}), 500  
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500
    


# Get a post by id
@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = execute_query('SELECT * FROM Posts WHERE id = %s', (post_id,))
        if post:
            return jsonify(post[0]), 200  
        else:
            return jsonify({'message': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500
    



# Update an existing post
@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        data = request.get_json()
        content = data.get('content')

        if content is None:
            return jsonify({'error': 'Content must be provided to update the post'}), 400

        query = 'UPDATE Posts SET content = %s WHERE id = %s'
        updated_posts = (content, post_id)

        result = execute_query(query, updated_posts)

        if result == 0:
            return jsonify({'message': 'Post not found'}), 404
            
        return jsonify({'message': 'Post updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500




# Create a new post
@app.route('/createPosts', methods=['POST'])
def create_post():
    try:
        data = request.get_json()  
        content = data.get('content')

        if not content:
            return jsonify({'error': 'Content is required'}), 400

        query = 'INSERT INTO Posts (content) VALUES (%s)'
        created_posts = execute_query(query, (content,))

        if created_posts is not None and created_posts > 0:
            return jsonify({'message': 'Post created successfully'}), 201
        else:
            return jsonify({'error': 'Failed to create post'}), 500
        
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
