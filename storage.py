import os
import json
import uuid
from datetime import datetime

class StoryStorage:
    def __init__(self, storage_dir='stories'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_story(self, story_data):
        """Save a generated story and return its ID"""
        story_id = str(uuid.uuid4())

        story_data['id'] = story_id
        story_data['created_at'] = datetime.now().isoformat()

        file_path = os.path.join(self.storage_dir, f"{story_id}.json")

        with open(file_path, 'w') as f:
            json.dump(story_data, f, indent=2)

        print(f"Story saved: {story_id}")
        return story_id

    def get_story(self, story_id):
        """Retrieve a story by ID"""
        file_path = os.path.join(self.storage_dir, f"{story_id}.json")

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            return json.load(f)

    def list_stories(self):
        """List all saved stories with metadata"""
        stories = []

        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)

                with open(file_path, 'r') as f:
                    story = json.load(f)

                    stories.append({
                        'id': story.get('id'),
                        'title': story.get('title'),
                        'genre': story.get('genre'),
                        'created_at': story.get('created_at')
                    })

        # Sort by creation date, newest first
        stories.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return stories
