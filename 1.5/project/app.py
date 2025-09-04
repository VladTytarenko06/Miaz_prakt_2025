from flask import Flask, render_template, request, jsonify
from db_config import get_connection

app = Flask(__name__)

# ---------------- API ---------------- #

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT book_id, title, author FROM books ORDER BY book_id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    books = [{'book_id': r[0], 'title': r[1], 'author': r[2]} for r in rows]
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({'error': 'Missing title or author'}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Book added successfully'}), 201

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': f'Book with ID {book_id} deleted'}), 200

# ---------------- UI ---------------- #

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
