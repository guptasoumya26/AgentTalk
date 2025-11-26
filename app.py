from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from backend.orchestrator import Orchestrator

app = Flask(__name__,
            template_folder='frontend/templates',
            static_folder='frontend/static')
CORS(app)

orchestrator = Orchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        status = orchestrator.get_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/agents', methods=['GET'])
def get_agents():
    try:
        agents = orchestrator.get_available_agents()
        return jsonify({
            "success": True,
            "agents": agents
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/call-agent', methods=['POST'])
def call_agent():
    try:
        data = request.json
        agent_name = data.get('agent')
        prompt = data.get('prompt')

        if not agent_name or not prompt:
            return jsonify({
                "success": False,
                "error": "Missing 'agent' or 'prompt' in request"
            }), 400

        result = orchestrator.call_agent(agent_name, prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/workflow/sequential', methods=['POST'])
def run_sequential_workflow():
    try:
        data = request.json
        user_request = data.get('request')

        if not user_request:
            return jsonify({
                "success": False,
                "error": "Missing 'request' in request body"
            }), 400

        results = orchestrator.run_sequential_workflow(user_request)
        return jsonify({
            "success": True,
            "workflow": results,
            "conversation": orchestrator.get_conversation_history()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/workflow/sequential-stream', methods=['POST'])
def run_sequential_workflow_stream():
    try:
        data = request.json
        user_request = data.get('request')

        if not user_request:
            return jsonify({
                "success": False,
                "error": "Missing 'request' in request body"
            }), 400

        def generate():
            import json
            import time

            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting workflow...'})}\n\n"
            time.sleep(0.1)

            orchestrator.add_message("User", user_request)
            yield f"data: {json.dumps({'type': 'message', 'agent': 'User', 'role': 'User', 'message': user_request})}\n\n"

            agent_sequence = [
                ("chatgpt", f"As a Product Manager, analyze this request and create a detailed technical specification with key features and tech stack recommendations: {user_request}"),
                ("gemini", "As a Full-Stack Developer, based on the specification above, write actual code snippets for the key components. Include both frontend (HTML/JS) and backend (Python/Node.js) code. Keep each code block concise but functional."),
                ("groq", "As a QA Engineer, review the specification and code above. Suggest test cases, potential bugs to watch for, and quality improvements. Provide examples of unit tests if applicable.")
            ]

            for agent_name, task in agent_sequence:
                if agent_name in orchestrator.agents:
                    agent = orchestrator.agents[agent_name]
                    yield f"data: {json.dumps({'type': 'thinking', 'agent': agent_name, 'role': agent.role})}\n\n"

                    result = orchestrator.call_agent(agent_name, task)

                    if result['success']:
                        yield f"data: {json.dumps({'type': 'message', 'agent': agent_name, 'role': result['role'], 'message': result['response']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'agent': agent_name, 'error': result.get('error', 'Unknown error')})}\n\n"

            agent_count = len([name for name in ['chatgpt', 'gemini', 'groq'] if name in orchestrator.agents])
            completion_summary = f"✅ Build complete! All {agent_count} agents have finished their work on: '{user_request}'"
            yield f"data: {json.dumps({'type': 'message', 'agent': 'System', 'role': 'Orchestrator', 'message': completion_summary})}\n\n"

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        return app.response_class(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/workflow/discussion', methods=['POST'])
def run_discussion():
    try:
        data = request.json
        topic = data.get('topic')
        rounds = data.get('rounds', 2)

        if not topic:
            return jsonify({
                "success": False,
                "error": "Missing 'topic' in request body"
            }), 400

        results = orchestrator.run_round_robin_discussion(topic, rounds)
        return jsonify({
            "success": True,
            "discussion": results,
            "conversation": orchestrator.get_conversation_history()
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/workflow/discussion-stream', methods=['POST'])
def run_discussion_stream():
    try:
        data = request.json
        topic = data.get('topic')
        rounds = data.get('rounds', 2)

        if not topic:
            return jsonify({
                "success": False,
                "error": "Missing 'topic' in request body"
            }), 400

        def generate():
            import json
            import time

            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting discussion...'})}\n\n"
            time.sleep(0.1)

            orchestrator.add_message("User", f"Discussion topic: {topic}")
            yield f"data: {json.dumps({'type': 'message', 'agent': 'User', 'role': 'User', 'message': f'Discussion topic: {topic}'})}\n\n"

            available = orchestrator.get_available_agents()

            for round_num in range(rounds):
                for agent_name in available:
                    agent = orchestrator.agents[agent_name]
                    yield f"data: {json.dumps({'type': 'thinking', 'agent': agent_name, 'role': agent.role})}\n\n"

                    if round_num == 0:
                        prompt = f"Share your perspective on: {topic}"
                    else:
                        prompt = f"Respond to the previous comments and add your thoughts on round {round_num + 1}."

                    result = orchestrator.call_agent(agent_name, prompt)

                    if result['success']:
                        yield f"data: {json.dumps({'type': 'message', 'agent': agent_name, 'role': result['role'], 'message': result['response']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'agent': agent_name, 'error': result.get('error', 'Unknown error')})}\n\n"

            completion_summary = f"✅ Discussion complete! {len(available)} agents discussed '{topic}' over {rounds} rounds."
            yield f"data: {json.dumps({'type': 'message', 'agent': 'System', 'role': 'Orchestrator', 'message': completion_summary})}\n\n"

            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        return app.response_class(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    try:
        history = orchestrator.get_conversation_history()
        return jsonify({
            "success": True,
            "conversation": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    try:
        orchestrator.reset()
        return jsonify({
            "success": True,
            "message": "Conversation reset successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    import sys
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n" + "="*60)
    print("🤖 AgentTalk - Multi-Agent Collaboration Platform")
    print("="*60)
    print("\nAvailable agents:")
    status = orchestrator.get_status()
    for agent in status['available_agents']:
        print(f"  ✓ {agent['name'].upper():<10} - {agent['role']} ({agent['model']})")

    if not status['available_agents']:
        print("  ⚠️  No agents available! Please configure API keys in config.properties")

    print("\n" + "="*60)
    print("Server starting at: http://localhost:5000")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
