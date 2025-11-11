# ComfyUI Setup Guide for Visual Novel Generator

This guide will help you set up ComfyUI on RunPod for generating images with better character consistency.

## Why ComfyUI?

- **Cost-effective**: Pay only for GPU time (~$0.30-0.50/hour vs $0.10/image with DALL-E)
- **Character consistency**: Use IP-Adapter or InstantID for consistent character faces
- **Customization**: Full control over models, LoRAs, and generation parameters
- **Quality**: Access to latest Stable Diffusion models and community fine-tunes

## Step 1: Deploy ComfyUI on RunPod

### Option A: Using ComfyUI Template (Easiest)

1. **Go to RunPod:**
   - Visit [runpod.io](https://runpod.io) and sign up
   - Add credits to your account ($10-20 recommended for testing)

2. **Deploy from template:**
   - Click "Deploy" → "Community Cloud"
   - Search for "ComfyUI" in templates
   - Select a template like "RunPod ComfyUI" or "ComfyUI + Custom Nodes"
   - Choose GPU: RTX 4090 (best), RTX 4080, or A4000 (cheaper)
   - Click "Deploy On-Demand"

3. **Access ComfyUI:**
   - Wait for pod to start (2-3 minutes)
   - Click "Connect" → "HTTP Service" → "ComfyUI"
   - Note the URL (e.g., `https://xxxxx-8188.proxy.runpod.net`)

### Option B: Manual Setup (Advanced)

```bash
# SSH into RunPod instance
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

## Step 2: Install Required Custom Nodes

### Using ComfyUI Manager (Recommended)

1. **Install ComfyUI Manager:**
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ltdrdata/ComfyUI-Manager.git
   cd ComfyUI-Manager
   pip install -r requirements.txt
   ```

2. **Restart ComfyUI and install nodes via UI:**
   - Open ComfyUI in browser
   - Click "Manager" button (bottom right)
   - Search and install:
     - **IP-Adapter-Plus** (for character consistency)
     - **InstantID** (alternative for character consistency)
     - **ControlNet Preprocessors**
     - **Image Saver** (if not included)

### Manual Installation

```bash
cd ComfyUI/custom_nodes

# IP-Adapter-Plus
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
cd ComfyUI_IPAdapter_plus && pip install -r requirements.txt && cd ..

# InstantID (optional)
git clone https://github.com/ZHO-ZHO-ZHO/ComfyUI-InstantID.git
cd ComfyUI-InstantID && pip install -r requirements.txt && cd ..
```

## Step 3: Download Models

### Base Model (Choose one)

For anime/illustration style (recommended for visual novels):
```bash
cd ComfyUI/models/checkpoints

# AnimagineXL (great for anime)
wget https://huggingface.co/cagliostrolab/animagine-xl-3.1/resolve/main/animagine-xl-3.1.safetensors

# Or DreamShaper (versatile)
wget https://civitai.com/api/download/models/128713 -O dreamshaper_8.safetensors
```

### IP-Adapter Models (for character consistency)

```bash
cd ComfyUI/models/ipadapter

# Download IP-Adapter models
wget https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors

# Download image encoders
cd ../clip_vision
wget https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors -O CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
```

### VAE (Optional but recommended)

```bash
cd ComfyUI/models/vae
wget https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors
```

## Step 4: Test Basic Workflow

1. **Open ComfyUI** in browser
2. **Load default workflow** (should auto-load)
3. **Test generation:**
   - Set positive prompt: "a beautiful fantasy castle, digital art"
   - Click "Queue Prompt"
   - Wait for image to generate

If successful, you're ready to integrate!

## Step 5: Update Visual Novel Generator Config

1. **Get your ComfyUI URL:**
   - From RunPod: looks like `https://xxxxx-8188.proxy.runpod.net`
   - Remove the `https://` prefix for internal access
   - Or use the direct IP if using VPN/SSH tunnel

2. **Update `.env` file:**
   ```env
   IMAGE_PROVIDER=comfyui
   COMFYUI_URL=https://your-runpod-url:8188
   ```

3. **Test connection:**
   ```bash
   python -c "import requests; print(requests.get('YOUR_COMFYUI_URL/system_stats').json())"
   ```

## Step 6: Customize Workflow for Character Consistency

### Basic Workflow (No Character Consistency)

The default workflow in `image_generator.py` works out of the box but doesn't maintain character consistency.

### Advanced Workflow (With IP-Adapter)

To maintain character consistency, you need to:

1. **Generate character reference images first**
2. **Use IP-Adapter to guide subsequent generations**

Here's a modified workflow structure:

```python
# In image_generator.py, update _get_comfyui_workflow()

def _get_comfyui_workflow(self, prompt, character_reference_path=None):
    workflow = {
        # ... base nodes (CheckpointLoader, KSampler, etc.)

        # Add IP-Adapter nodes
        "10": {
            "inputs": {
                "model": ["4", 0],
                "ipadapter": ["11", 0],
                "image": ["12", 0],  # Character reference image
                "weight": 0.8,  # Consistency strength (0-1)
                "weight_type": "linear"
            },
            "class_type": "IPAdapterApply"
        },
        "11": {
            "inputs": {
                "ipadapter_file": "ip-adapter_sdxl.safetensors"
            },
            "class_type": "IPAdapterModelLoader"
        },
        "12": {
            "inputs": {
                "image_path": character_reference_path
            },
            "class_type": "LoadImage"
        }
    }
    return workflow
```

### Character Reference Generation Flow

1. **At story start:**
   - Generate character description prompts
   - Generate reference images for each character
   - Save reference images with character IDs

2. **For each scene:**
   - Identify characters present
   - Pass character reference images to workflow
   - Generate scene with IP-Adapter guidance

## Step 7: Optimize Settings

### For Speed:
```python
"steps": 15,  # Reduce from 20
"cfg": 7.0,   # Lower guidance
"sampler_name": "dpmpp_2m",  # Faster sampler
```

### For Quality:
```python
"steps": 30,
"cfg": 8.5,
"sampler_name": "dpmpp_2m_sde_gpu",
"scheduler": "karras"
```

### For Character Consistency:
```python
# IP-Adapter settings
"weight": 0.8,  # Higher = more consistent, less variation
"weight_type": "ease in-out"  # Smoother application
```

## Troubleshooting

### Connection Errors

**Issue:** Can't connect to ComfyUI
```bash
# Check if ComfyUI is running
curl http://your-url:8188/system_stats

# Check RunPod logs
# In RunPod UI: Pod → View Logs
```

**Solution:**
- Ensure pod is running
- Check firewall settings
- Verify URL format (include http:// or https://)

### Generation Errors

**Issue:** "Model not found"
- Check model file names in `image_generator.py` match your actual files
- List models: `ls ComfyUI/models/checkpoints`

**Issue:** "Out of memory"
- Reduce image resolution: 768x768 instead of 1024x1024
- Lower batch size
- Use smaller model
- Upgrade GPU on RunPod

### Slow Generation

- **First generation is always slow** (model loading)
- Subsequent generations should be 5-15 seconds
- Check GPU utilization in RunPod dashboard
- Consider using a faster sampler

## Cost Management

### RunPod Pricing (approximate):
- **RTX 4090**: ~$0.69/hour (fastest)
- **RTX 4080**: ~$0.49/hour
- **RTX A4000**: ~$0.29/hour (slower but cheaper)

### Optimization Tips:
- Use "On-Demand" pods (stop when not in use)
- Generate multiple images in batch when possible
- Cache generated images aggressively
- Use "Spot" instances for 50% savings (may be interrupted)

### Cost Comparison:
- **OpenAI DALL-E 3**: $0.04-0.12 per image
- **ComfyUI on 4090**: ~$0.002-0.005 per image (if generating continuously)
- **Break-even point**: ~15-30 images

## Advanced: Character Consistency Strategies

### Strategy 1: IP-Adapter (Easiest)
- Generate 1 reference image per character
- Use IP-Adapter with 0.7-0.8 weight
- Works well for faces, less consistent for full body

### Strategy 2: InstantID (Better for faces)
- Requires face detection preprocessing
- More consistent facial features
- Slightly slower than IP-Adapter

### Strategy 3: LoRA Training (Best quality)
- Generate 20-30 character images
- Train LoRA on RunPod (30-60 minutes)
- Use trained LoRA for all character appearances
- Most consistent but requires setup time

### Strategy 4: Hybrid Approach (Recommended)
1. Generate character reference sheet (front, side, expressions)
2. Use IP-Adapter for face consistency
3. Apply style LoRA for visual consistency
4. Use ControlNet for pose control (optional)

## Next Steps

Once ComfyUI is working:

1. **Test basic generation** from visual novel app
2. **Implement character references** (save first character appearances)
3. **Add IP-Adapter workflow** for consistency
4. **Fine-tune weights** and settings
5. **Consider LoRA training** for main characters

## Resources

- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [IP-Adapter Plus](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- [ComfyUI Workflows](https://comfyworkflows.com/)
- [RunPod Documentation](https://docs.runpod.io/)
- [Civitai Models](https://civitai.com/) (more SD models)

## Support

If you run into issues:
1. Check ComfyUI console logs
2. Test workflow manually in ComfyUI UI first
3. Verify all models are downloaded
4. Check RunPod pod status and logs
