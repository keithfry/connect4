# Connect 4 Game

A web-based Connect 4 game with Django backend and JavaScript frontend, featuring game recording for neural network training.

## Features

- **Two-player mode**: Human vs Human gameplay
- **AI opponent**: Play against a minimax-based AI
- **Game recording**: All games are automatically recorded for training data
- **Modern UI**: Beautiful, responsive interface with animations
- **RESTful API**: Django REST Framework backend

## Setup

### Prerequisites

- Python 3.8+
- Node.js (for Playwright tests, optional)

### Backend Setup

1. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install django djangorestframework pydantic django-cors-headers
   ```

3. Run Django migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

4. Start the Django server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Serve the frontend files using a local server:
   ```bash
   # Using Python
   cd frontend
   python -m http.server 8080
   ```

2. Open `http://localhost:8080` in your browser

**Note**: Make sure the backend server is running before opening the frontend.

## API Endpoints

- `POST /api/game/new/` - Create new game session
  - Body: `{"has_ai": false, "ai_player": 2}`
  - Returns: Game state with `game_id`

- `POST /api/game/{game_id}/move/` - Make a move
  - Body: `{"column": 0}` (0-6)
  - Returns: Updated game state

- `GET /api/game/{game_id}/state/` - Get current game state
  - Returns: Current game state

- `POST /api/game/{game_id}/ai-move/` - Request AI move
  - Returns: Updated game state after AI move

- `POST /api/game/{game_id}/reset/` - Reset game
  - Returns: Reset game state

## Testing

### Backend Tests

```bash
cd backend
source ../.venv/bin/activate
python manage.py test
```

### E2E Tests (Playwright)

1. Install Playwright:
   ```bash
   npm install
   npx playwright install
   ```

2. Run tests:
   ```bash
   npm run test:e2e
   ```

**Note**: Make sure both backend and frontend servers are running, or use the Playwright config which starts them automatically.

## API Testing with Bruno

Import the Bruno collection from `bruno/connect4-api.bru` to test the API endpoints.

## Game Recording

All games are automatically recorded with:
- Unique game ID (timestamp-based, e.g., `game_20240101_120000_123456`)
- Board state for each move
- Player actions (column, player, move number)
- Game result (winner or draw)

Game data is stored in `game_data/` directory as JSON files for future neural network training.

## Project Structure

```
connect4/
├── backend/          # Django backend
│   ├── game/         # Game app
│   │   ├── board.py
│   │   ├── game_engine.py
│   │   ├── win_checker.py
│   │   ├── game_session.py
│   │   ├── game_recorder.py
│   │   ├── ai/       # AI implementations
│   │   └── views.py  # API views
│   └── manage.py
├── frontend/         # JavaScript frontend
│   ├── index.html
│   ├── styles/
│   └── js/
├── tests/           # E2E tests
├── bruno/           # Bruno API collection
└── game_data/       # Recorded game data (auto-created)
```

## Technology Stack

- **Backend**: Django, Django REST Framework, Pydantic
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Testing**: Django TestCase, Playwright
- **API Testing**: Bruno
- **Package Management**: uv (Python)

