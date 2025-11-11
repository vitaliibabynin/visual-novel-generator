from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import uuid
from datetime import datetime

from story_generator import StoryGenerator
from image_generator import ImageGenerator
from storage import StoryStorage

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize services
story_gen = StoryGenerator()
image_gen = ImageGenerator()
storage = StoryStorage()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/generate-story', methods=['POST'])
def generate_story():
    """Generate a new story based on user preferences"""
    try:
        data = request.json
        preferences = data.get('preferences', {})

        # Generate story structure
        print("Generating story...")
        story_data = story_gen.generate(preferences)

        # Generate images for each scene
        print("Generating images...")
        for scene in story_data['scenes']:
            if 'image_prompt' in scene:
                image_url = image_gen.generate(scene['image_prompt'])
                scene['image_url'] = image_url

        # Save story
        story_id = storage.save_story(story_data)
        story_data['id'] = story_id

        return jsonify({
            'success': True,
            'story': story_data
        })

    except Exception as e:
        print(f"Error generating story: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stories', methods=['GET'])
def list_stories():
    """List all saved stories"""
    try:
        stories = storage.list_stories()
        return jsonify({
            'success': True,
            'stories': stories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story by ID"""
    try:
        story = storage.get_story(story_id)
        if story:
            return jsonify({
                'success': True,
                'story': story
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Story not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
