from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import openai
import hashlib

app = Flask(__name__)

# Database setup
def create_db():
    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS events
                 (id INTEGER PRIMARY KEY, name TEXT, location TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY, question TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS answers
                 (id INTEGER PRIMARY KEY, user_id INTEGER, question_id INTEGER, answer TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY, user1_id INTEGER, user2_id INTEGER, message TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS event_participants
                 (id INTEGER PRIMARY KEY, user_id INTEGER, event_id INTEGER)''')
    conn.commit()
    conn.close()

# Serve the frontend
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

# Serve static files (CSS, JS)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()

    # Check if username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return jsonify({"message": "Username already exists!"}), 400

    # Insert new user
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully!"})

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful!", "user_id": user[0]})
    else:
        return jsonify({"message": "Invalid credentials!"}), 401

# Create an event
@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.json
    name = data['name']
    location = data['location']
    date = data['date']

    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()

    # Check if event name already exists
    c.execute("SELECT * FROM events WHERE name = ?", (name,))
    if c.fetchone():
        conn.close()
        return jsonify({"message": "Event name already exists!"}), 400

    # Insert new event
    c.execute("INSERT INTO events (name, location, date) VALUES (?, ?, ?)", (name, location, date))
    conn.commit()
    conn.close()

    return jsonify({"message": "Event created successfully!"})

# Match users using AI
openai.api_key = "your_openai_api_key"  # Replace with your OpenAI API key

@app.route('/match_users', methods=['POST'])
def match_users():
    data = request.json
    user1_id = data['user1_id']
    user2_id = data['user2_id']

    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()

    # Get answers for both users
    c.execute("SELECT answer FROM answers WHERE user_id = ?", (user1_id,))
    user1_answers = c.fetchall()
    c.execute("SELECT answer FROM answers WHERE user_id = ?", (user2_id,))
    user2_answers = c.fetchall()

    conn.close()

    # Combine answers into a prompt for OpenAI
    prompt = f"User 1 answers: {user1_answers}\nUser 2 answers: {user2_answers}\nAre these users compatible? Why or why not?"

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )

    # Extract the AI's response
    match_result = response.choices[0].message.content

    return jsonify({"match_result": match_result})

# Send a message
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    user1_id = data['user1_id']
    user2_id = data['user2_id']
    message = data['message']

    conn = sqlite3.connect('matchbox.db')
    c = conn.cursor()

    # Check if users exist
    c.execute("SELECT * FROM users WHERE id = ?", (user1_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({"message": "User 1 does not exist!"}), 400

    c.execute("SELECT * FROM users WHERE id = ?", (user2_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({"message": "User 2 does not exist!"}), 400

    # Insert new message
    c.execute("INSERT INTO chats (user1_id, user2_id, message) VALUES (?, ?, ?)", (user1_id, user2_id, message))
    conn.commit()
    conn.close()

    return jsonify({"message": "Message sent successfully!"})

if __name__ == '__main__':
    create_db()
    app.run(debug=True)