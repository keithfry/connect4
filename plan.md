# Connect 4 Game Development Plan

## Game Rules

Connect 4 is a two-player connection game where players take turns dropping colored discs into a vertically suspended grid. The objective is to be the first to form a horizontal, vertical, or diagonal line of four of one's own discs.

**Rules:**
- Board: 6 rows × 7 columns (standard size)
- Players alternate turns, dropping one disc per turn
- Discs fall to the lowest available space in the selected column
- Win condition: First player to form a line of 4 discs (horizontal, vertical, or diagonal) wins
- Draw condition: If the board fills without a winner, the game is a draw
- **Colors:** Yellow board/grid background, Player 1 uses red discs, Player 2 uses black discs

## Architecture Overview

**Client-Server Architecture:**
- **Backend (Python/Django):** Handles all game logic, state management, move validation, win detection, and AI
- **Frontend (JavaScript):** Handles UI rendering, user interactions, and API communication

## Subsystems

### 1. Backend Game Engine (Python)
**Purpose:** Manage game state, validate moves, detect wins/draws

**Components:**
- Board representation (6×7 grid)
- Move validation (check column availability, prevent invalid moves)
- Win detection algorithm (check all 4-in-a-row possibilities)
- Draw detection (check if board is full)
- Game state management (current player, game status, game sessions)
- RESTful API endpoints for game operations

**Files:**
- `backend/game/board.py` - Board state and manipulation
- `backend/game/game_engine.py` - Core game logic and rules
- `backend/game/win_checker.py` - Win condition detection
- `backend/game/game_session.py` - Game session management
- `backend/game/views.py` - Django REST Framework API views

### 2. Backend AI System (Python)
**Purpose:** Provide computer opponent before neural network implementation

**Components:**
- Basic AI strategy (minimax algorithm)
- Difficulty levels (optional)
- Move selection algorithm
- Future: Neural network integration (TensorFlow/PyTorch)

**Files:**
- `backend/game/ai/basic_ai.py` - Simple AI implementation (minimax)
- `backend/game/ai/ai_strategy.py` - AI decision-making logic
- `backend/game/ai/neural_network.py` - Future neural network implementation
- `backend/game/ai/training_pipeline.py` - Future training pipeline

### 3. Game Recording System (Python)
**Purpose:** Record all game actions for neural network training data

**Components:**
- Unique game ID generation (timestamp-based)
- Move recording (board state, action taken, player)
- Game result recording (winner, draw, final state)
- Data storage (file-based JSON)
- Export functionality for training data

**Files:**
- `backend/game/game_recorder.py` - Game recording and logging system
- `backend/game/game_data.py` - Data models for recorded games (Pydantic)
- `backend/game/storage.py` - Storage layer for game records (JSON files)

### 4. Frontend User Interface / Rendering
**Purpose:** Display the game board and handle user interactions

**Components:**
- Visual board rendering (yellow grid with columns)
- Disc dropping animation (red and black discs)
- Column selection/hover effects
- Game status display (current player, winner, draw)
- Reset/new game functionality
- Player indicator
- API communication layer
- Win animations (fireworks, piece fading)

**Files:**
- `frontend/index.html` - Main HTML structure
- `frontend/styles/main.css` - Styling and animations
- `frontend/js/board_renderer.js` - DOM-based board rendering
- `frontend/js/game_ui.js` - UI state and event handling
- `frontend/js/api_client.js` - API communication with backend

### 5. Frontend Game Controller
**Purpose:** Coordinate UI updates and manage frontend game flow

**Components:**
- Initialize game connection
- Handle user interactions
- Coordinate UI updates with backend state
- Manage game modes (human vs human, human vs AI)
- Poll or receive updates from backend

**Files:**
- `frontend/js/game_controller.js` - Frontend game orchestration
- `frontend/js/main.js` - Application entry point

### 6. API Layer
**Purpose:** Define communication protocol between frontend and backend

**Endpoints:**
- `POST /api/game/new/` - Create new game session (returns game_id)
- `POST /api/game/{game_id}/move/` - Make a move (column selection, validated with Pydantic)
- `GET /api/game/{game_id}/state/` - Get current game state
- `POST /api/game/{game_id}/ai-move/` - Request AI move (if AI player)
- `POST /api/game/{game_id}/reset/` - Reset game

**Response Format:**
- Game state: `{board: [[...]], current_player: 1|2, status: 'playing'|'won'|'draw', winner: 1|2|null, game_id: string, winning_positions: [[row, col], ...]}`

## Technology Stack

### Backend Technologies
- **Python 3.8+** - Core language
- **Django** - Web framework and API server
- **Django REST Framework** - REST API framework for Django
- **Pydantic** - Data validation and settings management
- **Future:** TensorFlow/PyTorch - Neural network training and inference

### Frontend Technologies
- **HTML5** - Structure
- **CSS3** - Styling and animations (yellow board, red/black discs)
- **Vanilla JavaScript (ES6+)** - UI logic and API communication
- **Fetch API** - HTTP requests to backend

### Development Tools
- **Git** - Version control
- **uv** - Fast Python package installer and resolver (virtual environment management)
- **Bruno** - API testing tool (alternative to Postman)
- **Playwright** - End-to-end testing framework for UI
- **Playwright MCP** - Model Context Protocol integration for Playwright
- **Modern browser** - Testing (Chrome, Firefox, Safari, Edge)

### Project Structure
```
connect4/
├── README.md
├── pyproject.toml (uv project file)
├── package.json
├── playwright.config.js
├── backend/
│   ├── manage.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── game/
│   │   ├── __init__.py
│   │   ├── views.py (API views)
│   │   ├── serializers.py (Pydantic models)
│   │   ├── urls.py
│   │   ├── board.py
│   │   ├── game_engine.py
│   │   ├── win_checker.py
│   │   ├── game_session.py
│   │   ├── game_recorder.py
│   │   ├── game_data.py
│   │   ├── storage.py
│   │   ├── tests.py
│   │   └── ai/
│   │       ├── __init__.py
│   │       ├── basic_ai.py
│   │       ├── ai_strategy.py
│   │       └── (future: neural_network.py, training_pipeline.py)
├── frontend/
│   ├── index.html
│   ├── favicon.ico
│   ├── styles/
│   │   └── main.css
│   └── js/
│       ├── main.js
│       ├── game_controller.js
│       ├── board_renderer.js
│       ├── game_ui.js
│       └── api_client.js
├── tests/
│   └── e2e/
│       └── game-flow.spec.js (Playwright tests)
├── bruno/
│   └── connect4-api.bru (Bruno API collection)
└── game_data/ (auto-created)
    └── *.json (recorded game data)
```

## Implementation Phases

### Phase 1: Backend Core Game Engine ✅
- Set up Django project structure with `uv` virtual environment
- Implement board representation (`backend/game/board.py`)
- Build move validation (`backend/game/game_engine.py`)
- Create win detection algorithm (`backend/game/win_checker.py`)
- Add draw detection
- Set up Django REST Framework
- Create Pydantic models for request/response validation (`backend/game/serializers.py`)
- Create basic API endpoints (new game, get state) in `backend/game/views.py`

### Phase 2: Backend API & Game Sessions ✅
- Implement game session management (`backend/game/game_session.py`)
- Complete API endpoints (move, reset, AI move)
- Add error handling and validation using Pydantic
- Create Bruno API collection (`bruno/connect4-api.bru`) for testing
- Test API endpoints with Bruno

### Phase 3: Frontend Basic UI ✅
- Create HTML structure (`frontend/index.html`)
- Style the board with yellow background (`frontend/styles/main.css`)
- Implement board rendering with red/black discs (`frontend/js/board_renderer.js`)
- Add disc drop animations
- Display game status

### Phase 4: Frontend-Backend Integration ✅
- Implement API client (`frontend/js/api_client.js`)
- Connect UI to backend API
- Add click handlers for column selection
- Update UI based on backend game state
- Add game reset functionality

### Phase 5: Basic AI (Backend) ✅
- Implement basic AI (minimax) in Python backend (`backend/game/ai/basic_ai.py`)
- Add AI move endpoint
- Integrate AI with game flow
- Add game mode selection UI (human vs human, human vs AI)

### Phase 6: Polish & Testing ✅
- Improve UI/UX
- Add visual feedback and animations
- Write Playwright E2E tests (`tests/e2e/game-flow.spec.js`)
- Test edge cases with Playwright MCP
- Optimize performance
- Handle error states
- Run full test suite (backend unit tests + E2E tests)
- Add win animations (fireworks, piece fading)
- Create favicon

### Phase 7: Neural Network (Future)
- Design model architecture
- Create training pipeline (Python backend)
- Implement model inference endpoint
- Replace or supplement basic AI

## Game Recording Details

All games are automatically recorded with:
- **Unique game ID**: Timestamp-based (e.g., `game_20240101_120000_123456`)
- **Board state**: For each move, the complete board state is recorded
- **Player actions**: Column selected, player number, move number
- **Game result**: Winner (player 1 or 2) or draw
- **Timestamps**: Start time, end time, and timestamp for each move

Game data is stored in `game_data/` directory as JSON files for future neural network training.

## Testing Strategy

### Backend Tests
- Unit tests for game engine components
- API endpoint tests
- Win detection tests
- Move validation tests

### E2E Tests (Playwright)
- Page load and initialization
- Game creation and mode selection
- Human vs Human gameplay
- Human vs AI gameplay
- Visual feedback and animations
- Game completion (win/draw)
- Game controls (reset, new game)
- Error handling
- Responsive design

## Notes

- All game logic is handled server-side for consistency and security
- Game recording happens automatically for all games
- Frontend is purely presentational and communicates via REST API
- Future neural network will use recorded game data for training

