# AI Visual Novel Generator

An interactive web-based visual novel generator that creates unique stories with AI-generated images.

## Features

- 🎮 **Interactive Stories**: User choices affect the narrative
- 🎨 **AI-Generated Images**: Each scene has a unique illustration
- 📚 **Story Replay**: Save and replay generated stories
- 🎯 **Multiple Genres**: Fantasy, Sci-Fi, Mystery, Horror, Romance, Adventure
- 🔀 **Branching Paths**: Multiple endings based on player choices
- ⚡ **Quick Setup**: Easy to configure and run

## Demo

1. User selects story preferences (genre, tone, setting)
2. AI generates a 5-10 scene story with choices
3. Each scene includes narrative text and an AI-generated image
4. Player makes choices that affect the story outcome
5. Stories are saved for replay

## Tech Stack

**Backend:**
- Python 3.10+
- Flask (web server)
- OpenAI API (story + image generation)
- JSON file storage

**Frontend:**
- Vanilla JavaScript
- HTML5/CSS3
- Responsive design

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Anthropic Claude API key)
- (Optional) ComfyUI instance on RunPod for advanced image generation

### Quick Start

1. **Clone the repository:**
```bash
git clone <repository-url>
cd visual-novel-generator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
IMAGE_PROVIDER=openai
```

4. **Run the application:**
```bash
python app.py
```

5. **Open browser:**
Navigate to `http://localhost:5000`

## Configuration

### Using OpenAI (Default - Easiest)

```env
OPENAI_API_KEY=your_key_here
IMAGE_PROVIDER=openai
```

**Cost estimate:** ~$0.50-1.00 per story (GPT-4 + DALL-E 3)

### Using ComfyUI on RunPod (Advanced)

1. **Set up RunPod ComfyUI:**
   - Deploy a ComfyUI instance on RunPod with a GPU
   - Install required custom nodes (see below)
   - Note your instance URL

2. **Update `.env`:**
```env
OPENAI_API_KEY=your_key_here  # Still needed for story generation
IMAGE_PROVIDER=comfyui
COMFYUI_URL=http://your-runpod-url:8188
```

3. **Required ComfyUI Custom Nodes:**
   - ComfyUI-Manager
   - IP-Adapter-Plus (for character consistency)
   - InstantID (optional, better character consistency)

4. **Customize workflow:**
   - Edit `image_generator.py` → `_get_comfyui_workflow()` method
   - Adjust model names to match your ComfyUI setup
   - Configure sampler settings as needed

### Using Claude for Story Generation

```env
ANTHROPIC_API_KEY=your_claude_key_here
# Comment out OPENAI_API_KEY
```

Then update `story_generator.py` to uncomment Anthropic support.

## Project Structure

```
visual-novel-generator/
├── app.py                 # Flask application
├── story_generator.py     # LLM story generation
├── image_generator.py     # Image generation (OpenAI/ComfyUI)
├── storage.py            # Story persistence
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── static/              # Frontend files
│   ├── index.html       # Main UI
│   ├── style.css        # Styling
│   ├── app.js           # Frontend logic
│   └── images/          # Generated images (created automatically)
└── stories/             # Saved stories (created automatically)
```

## API Endpoints

### `POST /api/generate-story`
Generate a new story with images.

**Request:**
```json
{
  "preferences": {
    "genre": "fantasy",
    "tone": "dramatic",
    "setting": "medieval"
  }
}
```

**Response:**
```json
{
  "success": true,
  "story": {
    "id": "uuid",
    "title": "Story Title",
    "backstory": "...",
    "scenes": [...]
  }
}
```

### `GET /api/stories`
List all saved stories.

### `GET /api/stories/<id>`
Get a specific story by ID.

## Customization

### Adjusting Story Length

Edit `story_generator.py` → `_build_prompt()`:
```python
# Change "5-7 scenes total" to desired length
"5-7 scenes total"  # Make it "10-15 scenes total" for longer stories
```

### Changing Image Style

Edit the prompt in `story_generator.py`:
```python
# Add style preferences to image_prompt instructions
"Use consistent visual style: anime style, watercolor, photorealistic, etc."
```

### Adding More Genres/Settings

Edit `static/index.html` to add more options to the dropdown menus.

## Troubleshooting

### "No API key found" error
- Make sure `.env` file exists and contains valid API keys
- Check that `python-dotenv` is installed

### Images not loading
- Check API key permissions
- Verify IMAGE_PROVIDER setting in `.env`
- Check console logs for specific errors

### Story generation is slow
- OpenAI DALL-E 3: ~10-30 seconds per image
- ComfyUI: depends on your GPU, typically 5-15 seconds per image
- Total generation time: 1-3 minutes for full story

### ComfyUI connection errors
- Verify COMFYUI_URL is correct
- Check if RunPod instance is running
- Test ComfyUI endpoint: `curl http://your-url:8188/system_stats`

## Advanced: ComfyUI Setup for Character Consistency

For best character consistency across scenes:

1. **Install these custom nodes in ComfyUI:**
   ```
   - ComfyUI-IP-Adapter-Plus
   - ComfyUI-InstantID
   - ComfyUI-PhotoMaker (alternative)
   ```

2. **Use a character-focused workflow:**
   - Generate character reference at story start
   - Use IP-Adapter to maintain face consistency
   - Apply same style LoRA to all generations

3. **Update `image_generator.py` workflow:**
   - Add character reference inputs
   - Configure IP-Adapter nodes
   - Adjust weights for consistency vs variety

## Performance Optimization

- **Caching**: Generated stories and images are cached automatically
- **Parallel Generation**: Images could be generated in parallel (TODO)
- **Model Selection**: Use GPT-3.5-turbo for faster (cheaper) story generation

## Future Enhancements

- [ ] Character consistency system (reference images)
- [ ] Background music and sound effects
- [ ] Save/load game state mid-playthrough
- [ ] User accounts and story sharing
- [ ] More complex branching (variables, conditions)
- [ ] Export story as standalone HTML

## Cost Estimates

**Per story with OpenAI:**
- Story generation (GPT-4): ~$0.10-0.20
- Images (DALL-E 3, 5-7 images): ~$0.40-0.70
- **Total: ~$0.50-1.00 per story**

**With ComfyUI:**
- Story generation (GPT-4): ~$0.10-0.20
- Images (free, RunPod GPU costs): ~$0.10-0.30/hour
- More cost-effective for high volume

## License

MIT License - feel free to modify and use as needed.

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For issues or questions, please open a GitHub issue.
