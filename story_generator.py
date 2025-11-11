import os
import json
from openai import OpenAI
# from anthropic import Anthropic  # Uncomment if using Claude

class StoryGenerator:
    def __init__(self):
        # Initialize LLM client
        self.openai_client = None
        self.anthropic_client = None

        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.provider = 'openai'
        # elif os.getenv('ANTHROPIC_API_KEY'):
        #     self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        #     self.provider = 'anthropic'
        else:
            raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")

    def generate(self, preferences):
        """Generate a complete story based on user preferences"""

        genre = preferences.get('genre', 'fantasy')
        tone = preferences.get('tone', 'adventurous')
        setting = preferences.get('setting', 'medieval')

        prompt = self._build_prompt(genre, tone, setting)

        if self.provider == 'openai':
            return self._generate_openai(prompt)
        else:
            return self._generate_anthropic(prompt)

    def _build_prompt(self, genre, tone, setting):
        return f"""Create an interactive story with the following specifications:

Genre: {genre}
Tone: {tone}
Setting: {setting}

Requirements:
- 5-7 scenes total
- Each scene has narrative text (2-3 paragraphs)
- 2-3 scenes should have choices (2 options each)
- Choices should meaningfully affect the story
- Include 2 different endings based on choices
- Each scene needs a detailed image description for AI image generation

Return ONLY valid JSON in this exact format:
{{
  "title": "Story Title",
  "genre": "{genre}",
  "backstory": "Brief backstory paragraph setting up the story",
  "scenes": [
    {{
      "id": "scene_1",
      "text": "The narrative text for this scene...",
      "image_prompt": "Detailed visual description for AI image generation, include art style, mood, lighting, specific details",
      "choices": [
        {{"text": "Choice option 1", "next_scene": "scene_2"}},
        {{"text": "Choice option 2", "next_scene": "scene_3"}}
      ]
    }},
    {{
      "id": "scene_2",
      "text": "Continuation text...",
      "image_prompt": "Detailed visual description...",
      "next_scene": "scene_4"
    }}
  ]
}}

Important:
- Use consistent visual style in all image_prompts (e.g., "digital art, fantasy style" or "anime style illustration")
- Make image_prompts detailed: describe characters, setting, mood, lighting, composition
- Linear scenes (no choices) should have "next_scene" field
- Choice scenes should have "choices" array
- Final scenes (endings) should have neither
- Keep scene IDs unique and sequential
"""

    def _generate_openai(self, prompt):
        """Generate story using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a creative story writer who outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            story_data = json.loads(content)

            # Validate structure
            self._validate_story(story_data)

            return story_data

        except Exception as e:
            print(f"Error generating story with OpenAI: {e}")
            raise

    def _generate_anthropic(self, prompt):
        """Generate story using Claude"""
        # Implement if using Anthropic
        raise NotImplementedError("Anthropic support coming soon")

    def _validate_story(self, story_data):
        """Validate the story structure"""
        required_fields = ['title', 'backstory', 'scenes']
        for field in required_fields:
            if field not in story_data:
                raise ValueError(f"Missing required field: {field}")

        if not story_data['scenes']:
            raise ValueError("Story must have at least one scene")

        for scene in story_data['scenes']:
            if 'id' not in scene or 'text' not in scene or 'image_prompt' not in scene:
                raise ValueError(f"Scene missing required fields: {scene}")
