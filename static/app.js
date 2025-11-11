// Global state
let currentStory = null;
let currentSceneIndex = 0;
let sceneHistory = [];

// API base URL (change if needed)
const API_BASE = '';

// Screen management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showWelcome() {
    showScreen('welcome-screen');
}

function showPreferences() {
    showScreen('preferences-screen');
}

function showLoading() {
    showScreen('loading-screen');
    animateProgress();
}

function showGame() {
    showScreen('game-screen');
}

function showEnding() {
    showScreen('ending-screen');
}

async function showSavedStories() {
    showScreen('saved-stories-screen');
    await loadSavedStories();
}

// Progress bar animation
function animateProgress() {
    const progressFill = document.getElementById('progress-fill');
    let progress = 0;

    const interval = setInterval(() => {
        progress += 1;
        progressFill.style.width = progress + '%';

        if (progress >= 95) {
            clearInterval(interval);
        }
    }, 800);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Form submission
    document.getElementById('preferences-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const preferences = {
            genre: document.getElementById('genre').value,
            tone: document.getElementById('tone').value,
            setting: document.getElementById('setting').value
        };

        await generateStory(preferences);
    });
});

// Generate story
async function generateStory(preferences) {
    console.log('Generating story with preferences:', preferences);
    showLoading();

    try {
        console.log('Sending request to API...');
        const response = await fetch(`${API_BASE}/api/generate-story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ preferences })
        });

        console.log('Response received:', response.status);
        const data = await response.json();
        console.log('Data:', data);

        if (data.success) {
            console.log('Story generated successfully!');
            // Complete progress bar
            document.getElementById('progress-fill').style.width = '100%';

            setTimeout(() => {
                currentStory = data.story;
                startStory();
            }, 500);
        } else {
            console.error('Story generation failed:', data.error);
            alert('Error generating story: ' + data.error);
            showPreferences();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate story. Please check your API keys and try again.');
        showPreferences();
    }
}

// Start playing a story
function startStory() {
    currentSceneIndex = 0;
    sceneHistory = [];

    document.getElementById('story-title').textContent = currentStory.title;

    // Show backstory first
    const backstoryScene = {
        text: `<h3>Backstory</h3><p>${currentStory.backstory}</p>`,
        image_url: currentStory.scenes[0]?.image_url || ''
    };

    displayScene(backstoryScene, true);
}

// Display a scene
function displayScene(scene, isBackstory = false) {
    showGame();

    const sceneContent = document.getElementById('scene-content');
    const sceneImg = document.getElementById('scene-img');
    const imageLoading = document.getElementById('image-loading');
    const choicesContainer = document.getElementById('choices-container');
    const navigationContainer = document.getElementById('navigation-container');

    // Set text content
    sceneContent.innerHTML = scene.text;

    // Handle image loading
    if (scene.image_url) {
        imageLoading.style.display = 'block';
        sceneImg.style.display = 'none';

        sceneImg.onload = () => {
            imageLoading.style.display = 'none';
            sceneImg.style.display = 'block';
        };

        sceneImg.onerror = () => {
            imageLoading.textContent = 'Image failed to load';
        };

        sceneImg.src = scene.image_url;
    } else {
        imageLoading.style.display = 'block';
        imageLoading.textContent = 'No image available';
        sceneImg.style.display = 'none';
    }

    // Clear previous choices and navigation
    choicesContainer.innerHTML = '';
    navigationContainer.innerHTML = '';

    if (isBackstory) {
        // Show continue button for backstory
        navigationContainer.innerHTML = `
            <button class="btn btn-primary" onclick="nextScene()">
                Begin Story →
            </button>
        `;
    } else {
        const actualScene = currentStory.scenes[currentSceneIndex];

        if (actualScene.choices && actualScene.choices.length > 0) {
            // Show choices
            actualScene.choices.forEach((choice, index) => {
                const button = document.createElement('button');
                button.className = 'choice-btn';
                button.textContent = choice.text;
                button.onclick = () => makeChoice(choice);
                choicesContainer.appendChild(button);
            });
        } else if (actualScene.next_scene) {
            // Show continue button
            navigationContainer.innerHTML = `
                <button class="btn btn-primary" onclick="nextScene()">
                    Continue →
                </button>
            `;
        } else {
            // End of story
            showStoryEnding();
        }
    }
}

// Navigate to next scene
function nextScene() {
    const currentScene = currentStory.scenes[currentSceneIndex];

    if (currentSceneIndex === 0 && currentScene) {
        // Just finished backstory, show first scene
        displayScene(currentScene);
    } else if (currentScene && currentScene.next_scene) {
        // Linear progression
        const nextSceneId = currentScene.next_scene;
        const nextIndex = currentStory.scenes.findIndex(s => s.id === nextSceneId);

        if (nextIndex !== -1) {
            sceneHistory.push(currentSceneIndex);
            currentSceneIndex = nextIndex;
            displayScene(currentStory.scenes[currentSceneIndex]);
        } else {
            showStoryEnding();
        }
    } else {
        currentSceneIndex++;
        if (currentSceneIndex < currentStory.scenes.length) {
            displayScene(currentStory.scenes[currentSceneIndex]);
        } else {
            showStoryEnding();
        }
    }
}

// Handle choice selection
function makeChoice(choice) {
    const nextSceneId = choice.next_scene;
    const nextIndex = currentStory.scenes.findIndex(s => s.id === nextSceneId);

    if (nextIndex !== -1) {
        sceneHistory.push(currentSceneIndex);
        currentSceneIndex = nextIndex;
        displayScene(currentStory.scenes[currentSceneIndex]);
    } else {
        showStoryEnding();
    }
}

// Show story ending
function showStoryEnding() {
    const endingContent = document.getElementById('ending-content');

    // Get the last scene's text as ending
    const lastScene = currentStory.scenes[currentSceneIndex];

    if (lastScene) {
        endingContent.innerHTML = `
            <p>${lastScene.text}</p>
            <hr style="margin: 20px 0; border: none; border-top: 2px solid #ddd;">
            <p style="font-style: italic;">Thank you for playing!</p>
        `;
    } else {
        endingContent.innerHTML = `
            <p>Your journey has come to an end.</p>
            <p style="font-style: italic;">Thank you for playing!</p>
        `;
    }

    showEnding();
}

// Quit current story
function quitStory() {
    if (confirm('Are you sure you want to quit this story?')) {
        showWelcome();
    }
}

// Load saved stories
async function loadSavedStories() {
    const listContainer = document.getElementById('saved-stories-list');
    listContainer.innerHTML = '<p style="text-align: center; color: #999;">Loading...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/stories`);
        const data = await response.json();

        if (data.success) {
            listContainer.innerHTML = '';

            if (data.stories.length === 0) {
                return;
            }

            data.stories.forEach(story => {
                const card = document.createElement('div');
                card.className = 'story-card';
                card.onclick = () => loadStory(story.id);

                const date = new Date(story.created_at).toLocaleDateString();

                card.innerHTML = `
                    <h4>${story.title}</h4>
                    <p><strong>Genre:</strong> ${story.genre || 'Unknown'}</p>
                    <p><strong>Created:</strong> ${date}</p>
                `;

                listContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading stories:', error);
        listContainer.innerHTML = '<p style="text-align: center; color: #f44;">Error loading stories</p>';
    }
}

// Load a specific story
async function loadStory(storyId) {
    try {
        const response = await fetch(`${API_BASE}/api/stories/${storyId}`);
        const data = await response.json();

        if (data.success) {
            currentStory = data.story;
            startStory();
        }
    } catch (error) {
        console.error('Error loading story:', error);
        alert('Failed to load story');
    }
}
