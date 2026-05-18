from flask import Flask, render_template, request, jsonify
import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot import NLPChatbot

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize chatbot globally
chatbot = NLPChatbot('intents.json')

def initialize_chatbot():
    # pattern‑matching chatbot needs no training
    return True


@app.route('/')
def index():
    """Render the main chatbot interface."""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat requests from the frontend.

    Expected JSON format:
    {
        "message": "user message"
    }

    Returns:
    {
        "response": "chatbot response",
        "intent": "detected intent",
        "confidence": confidence score
    }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                'error': 'Empty message',
                'response': 'Please say something!'
            }), 400

        # Get prediction and response
        intent, confidence = chatbot.predict_intent(user_message)
        response = chatbot.chat(user_message)

        return jsonify({
            'response': response,
            'intent': intent,
            'confidence': round(float(confidence), 2),
            'success': True
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history."""
    try:
        history = chatbot.get_conversation_history()
        return jsonify({
            'history': history,
            'success': True
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history."""
    try:
        chatbot.clear_history()
        return jsonify({
            'message': 'History cleared',
            'success': True
        }), 200
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500


if __name__ == '__main__':
    print("Initializing chatbot...")
    if not initialize_chatbot():
        print("Failed to initialize chatbot!")
        sys.exit(1)

    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)