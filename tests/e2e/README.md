# E2E Test Suite

Comprehensive Playwright end-to-end tests for the Connect 4 game, organized by feature area.

## Test Structure

```
tests/e2e/
├── helpers/
│   └── test-helpers.js          # Shared test utilities and helpers
├── ui/
│   ├── page-load.spec.js        # Page load and initialization tests
│   └── game-controls.spec.js    # Game control UI tests
├── gameplay/
│   ├── human-vs-human.spec.js   # Human vs Human gameplay tests
│   ├── win-conditions.spec.js   # Win detection and handling tests
│   └── draw-condition.spec.js  # Draw condition tests
├── ai/
│   └── ai-gameplay.spec.js      # AI opponent tests
├── animations/
│   └── visual-feedback.spec.js  # Visual feedback and animation tests
├── api/
│   └── api-integration.spec.js  # API integration tests
├── responsive/
│   └── responsive-design.spec.js # Responsive design tests
└── error-handling.spec.js        # Error handling tests
```

## Running Tests

### Run all tests
```bash
npm run test:e2e
```

### Run specific test file
```bash
npx playwright test tests/e2e/ui/page-load.spec.js
```

### Run tests in a specific folder
```bash
npx playwright test tests/e2e/ui/
```

### Run tests in headed mode (see browser)
```bash
npx playwright test --headed
```

### Run tests with specific browser
```bash
npx playwright test --project=chromium
```

## Test Categories

### UI Tests (`ui/`)
- Page load and initialization
- Game controls (New Game, Reset, Mode Selection)
- UI element visibility and functionality

### Gameplay Tests (`gameplay/`)
- Human vs Human gameplay flow
- Turn alternation
- Disc placement and stacking
- Win condition detection (horizontal, vertical, diagonal)
- Draw condition detection
- Winning piece highlighting

### AI Tests (`ai/`)
- AI move generation
- AI thinking status
- Human vs AI gameplay flow
- AI move validation

### Animation Tests (`animations/`)
- Disc drop animations
- Visual feedback (colors, highlighting)
- Win animations (fireworks, piece fading)
- Animation performance

### API Tests (`api/`)
- API endpoint testing
- Request/response validation
- Error handling
- Game state management via API

### Responsive Tests (`responsive/`)
- Mobile viewport (375x667)
- Tablet viewport (768x1024)
- Desktop viewport (1920x1080)
- Touch interactions

### Error Handling Tests
- API error handling
- Network delay handling
- Invalid input handling
- Edge case scenarios

## Test Helpers

The `helpers/test-helpers.js` file provides reusable utilities:
- `createNewGame()` - Create a new game session
- `makeMove()` - Make a move in a specific column
- `getGameStatus()` - Get current game status text
- `getDiscCount()` - Get number of discs on board
- `waitForAIMove()` - Wait for AI to complete move
- `createHorizontalWin()` - Helper to create a win scenario
- `createDraw()` - Helper to create a draw scenario

## Server Startup

The Playwright config (`playwright.config.js`) automatically starts both servers:
- Django backend on `http://localhost:8000`
- Frontend server on `http://localhost:8080`

Servers are started before tests run and stopped after tests complete.

## Requirements Coverage

All requirements from the plan are covered:
- ✅ Page load and initialization
- ✅ Game creation and mode selection
- ✅ Human vs Human gameplay
- ✅ Human vs AI gameplay
- ✅ Win detection (all directions)
- ✅ Draw detection
- ✅ Visual feedback and animations
- ✅ Game controls (reset, new game)
- ✅ Error handling
- ✅ Responsive design
- ✅ API integration

