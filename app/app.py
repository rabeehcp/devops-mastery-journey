import os
import redis
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
redis_host = os.getenv('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
TODOS_KEY = 'todos'

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 DevOps Todo App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        h1 i { color: #667eea; margin-right: 10px; }
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
        }
        input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.02);
        }
        .todo-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .todo-text {
            font-size: 16px;
            color: #333;
        }
        .delete-btn {
            background: linear-gradient(135deg, #ff6b6b, #c92a2a);
            padding: 8px 15px;
            font-size: 14px;
        }
        .stats {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #666;
        }
        .stats span {
            font-weight: bold;
            color: #667eea;
            font-size: 20px;
        }
        .badge {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-left: 10px;
        }
        .empty {
            text-align: center;
            color: #999;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <i class="fas fa-tasks"></i>
            DevOps Task Manager
            <span class="badge">Redis</span>
        </h1>
        
        <div class="input-group">
            <input type="text" id="taskInput" placeholder="What needs to be done?..." onkeypress="handleKeyPress(event)">
            <button onclick="addTask()">
                <i class="fas fa-plus"></i> Add
            </button>
        </div>

        <div id="todoList">
            {% for todo in todos %}
            <div class="todo-item">
                <span class="todo-text">{{ todo }}</span>
                <button class="delete-btn" onclick="deleteTask({{ loop.index0 }})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
            {% endfor %}
        </div>

        {% if todos|length == 0 %}
        <div class="empty">
            <i class="fas fa-clipboard-list" style="font-size: 48px; margin-bottom: 10px;"></i>
            <p>No tasks yet! Add your first task above.</p>
            <p style="font-size: 14px;">✨ Data persists in Redis</p>
        </div>
        {% endif %}

        <div class="stats">
            📊 Total tasks: <span>{{ todos|length }}</span>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/js/all.min.js"></script>
    <script>
        function addTask() {
            const input = document.getElementById('taskInput');
            const task = input.value.trim();
            if (!task) return;
            
            fetch('/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'task=' + encodeURIComponent(task)
            }).then(() => location.reload());
        }
        
        function deleteTask(index) {
            if (confirm('Delete this task?')) {
                fetch('/delete/' + index).then(() => location.reload());
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') addTask();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    todos = r.lrange(TODOS_KEY, 0, -1)
    return render_template_string(HTML, todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task and task.strip():
        r.rpush(TODOS_KEY, task.strip())
    return '', 200

@app.route('/delete/<int:index>')
def delete(index):
    todos = r.lrange(TODOS_KEY, 0, -1)
    if 0 <= index < len(todos):
        r.lset(TODOS_KEY, index, '__DELETED__')
        r.lrem(TODOS_KEY, 0, '__DELETED__')
    return '', 200

@app.route('/health')
def health():
    return {"status": "healthy", "app": "Todo App", "redis": redis_host}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
