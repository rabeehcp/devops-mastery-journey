from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Simple in-memory TODO list
todos = []

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>DevOps TODO App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        input { padding: 8px; width: 300px; }
        button { padding: 8px 16px; }
        li { margin: 8px 0; }
    </style>
</head>
<body>
    <h1>My DevOps TODO List</h1>
    
    <form method="POST" action="/add">
        <input type="text" name="task" placeholder="What needs to be done?" required>
        <button type="submit">Add Task</button>
    </form>

    <h3>Tasks:</h3>
    <ul>
    {% for todo in todos %}
        <li>
            {{ todo }} 
            <a href="/delete/{{ loop.index0 }}" style="color: red; margin-left: 15px;">[Delete]</a>
        </li>
    {% endfor %}
    </ul>

    <p><a href="/health">Health Check</a></p>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML, todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task and task.strip():
        todos.append(task.strip())
    return home()

@app.route('/delete/<int:index>')
def delete(index):
    if 0 <= index < len(todos):
        todos.pop(index)
    return home()

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "app": "DevOps TODO App", "version": "1.0"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
