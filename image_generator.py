import os
import requests
import base64
from openai import OpenAI
import time

class ImageGenerator:
    def __init__(self):
        self.provider = os.getenv('IMAGE_PROVIDER', 'openai').lower()

        if self.provider == 'openai':
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError("OPENAI_API_KEY not found")
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.provider == 'comfyui':
            self.comfyui_url = os.getenv('COMFYUI_URL')
            if not self.comfyui_url:
                raise ValueError("COMFYUI_URL not found")

    def generate(self, prompt):
        """Generate image based on prompt"""
        if self.provider == 'openai':
            return self._generate_openai(prompt)
        elif self.provider == 'comfyui':
            return self._generate_comfyui(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _generate_openai(self, prompt):
        """Generate image using OpenAI DALL-E"""
        try:
            print(f"Generating image with prompt: {prompt[:100]}...")

            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            print(f"Image generated: {image_url}")

            return image_url

        except Exception as e:
            print(f"Error generating image with OpenAI: {e}")
            # Return placeholder on error
            return "https://via.placeholder.com/1024x1024/cccccc/666666?text=Image+Generation+Failed"

    def _generate_comfyui(self, prompt):
        """Generate image using ComfyUI on RunPod"""
        try:
            # Load the ComfyUI workflow template
            workflow = self._get_comfyui_workflow(prompt)

            # Submit to ComfyUI
            response = requests.post(
                f"{self.comfyui_url}/prompt",
                json={"prompt": workflow}
            )

            if response.status_code != 200:
                raise Exception(f"ComfyUI error: {response.text}")

            prompt_id = response.json()['prompt_id']

            # Poll for completion
            image_data = self._wait_for_comfyui_image(prompt_id)

            # Save image locally and return path
            image_path = self._save_image(image_data, prompt_id)

            return image_path

        except Exception as e:
            print(f"Error generating image with ComfyUI: {e}")
            return "https://via.placeholder.com/1024x1024/cccccc/666666?text=Image+Generation+Failed"

    def _get_comfyui_workflow(self, prompt):
        """
        Get ComfyUI workflow JSON
        This is a basic template - you'll customize this based on your ComfyUI setup
        """
        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time()),
                    "steps": 20,
                    "cfg": 8.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"  # Change to your model
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "low quality, blurry, ugly, distorted",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "visual_novel",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

        return workflow

    def _wait_for_comfyui_image(self, prompt_id, timeout=300):
        """Wait for ComfyUI to finish generating image"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check history
                response = requests.get(f"{self.comfyui_url}/history/{prompt_id}")

                if response.status_code == 200:
                    history = response.json()

                    if prompt_id in history:
                        outputs = history[prompt_id].get('outputs', {})

                        # Find the SaveImage node output
                        for node_id, output in outputs.items():
                            if 'images' in output:
                                image_info = output['images'][0]
                                return self._download_comfyui_image(image_info)

                time.sleep(2)

            except Exception as e:
                print(f"Error polling ComfyUI: {e}")
                time.sleep(2)

        raise TimeoutError("ComfyUI generation timed out")

    def _download_comfyui_image(self, image_info):
        """Download image from ComfyUI"""
        filename = image_info['filename']
        subfolder = image_info.get('subfolder', '')
        folder_type = image_info.get('type', 'output')

        url = f"{self.comfyui_url}/view"
        params = {
            'filename': filename,
            'subfolder': subfolder,
            'type': folder_type
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download image: {response.text}")

    def _save_image(self, image_data, image_id):
        """Save image locally and return path"""
        os.makedirs('static/images', exist_ok=True)

        image_path = f"static/images/{image_id}.png"

        with open(image_path, 'wb') as f:
            f.write(image_data)

        # Return URL path
        return f"/images/{image_id}.png"
