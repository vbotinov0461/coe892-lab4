/* =========================================================================
   DATA — this is the local JSON your Python backend will eventually supply.
   Swap INITIAL_DIMENSIONS / INITIAL_MINES for whatever your backend exports,
   or fetch() them in and call initGame(dimensions, mines) with the result.
   ========================================================================= */

// Map size: two integers, x = columns, y = rows.
const INITIAL_DIMENSIONS = { x: 10, y: 8 };

// Mine data: rows of { serial, x, y }. This is the source of truth —
// the 0/1 grid below is always derived FROM this, never edited directly.
const INITIAL_MINES = [
  { serial: "MN-0001", x: 2, y: 1 },
  { serial: "MN-0002", x: 5, y: 1 },
  { serial: "MN-0003", x: 7, y: 2 },
  { serial: "MN-0004", x: 1, y: 4 },
  { serial: "MN-0005", x: 4, y: 4 },
  { serial: "MN-0006", x: 8, y: 4 },
  { serial: "MN-0007", x: 3, y: 6 },
  { serial: "MN-0008", x: 6, y: 6 },
  { serial: "MN-0009", x: 9, y: 0 },
];

/* =========================================================================
   STATE
   ========================================================================= */

let dimensions = null;   // { x, y }
let mines = [];          // live, mutable copy of mine rows
let clearedTiles = [];   // { x, y } tiles that used to hold a mine
let rover = { x: 0, y: 0 };

/* =========================================================================
   GRID DERIVATION
   Build the basic 0/1 grid object purely by reflecting the mine list.
   grid[row][col] -> 1 if a mine sits at (col, row), else 0.
   ========================================================================= */

function buildGridFromMines(dims, mineRows) {
  const grid = [];
  for (let row = 0; row < dims.y; row++) {
    grid.push(new Array(dims.x).fill(0));
  }
  for (const mine of mineRows) {
    if (mine.y >= 0 && mine.y < dims.y && mine.x >= 0 && mine.x < dims.x) {
      grid[mine.y][mine.x] = 1;
    }
  }
  return grid;
}

function isCleared(x, y) {
  return clearedTiles.some((t) => t.x === x && t.y === y);
}

function mineAt(x, y) {
  return mines.find((m) => m.x === x && m.y === y) || null;
}

/* =========================================================================
   RENDERING
   ========================================================================= */

const gridEl = document.getElementById("grid");
const minesRemainingEl = document.getElementById("mines-remaining");
const gridDimsEl = document.getElementById("grid-dims");
const roverPosEl = document.getElementById("rover-pos");
const logEl = document.getElementById("log");

function renderGrid() {
  const grid = buildGridFromMines(dimensions, mines);

  gridEl.style.setProperty("--grid-aspect", dimensions.x / dimensions.y);
  gridEl.style.gridTemplateColumns = `repeat(${dimensions.x}, 1fr)`;
  gridEl.style.gridTemplateRows = `repeat(${dimensions.y}, 1fr)`;
  gridEl.innerHTML = "";

  for (let y = 0; y < dimensions.y; y++) {
    for (let x = 0; x < dimensions.x; x++) {
      const tile = document.createElement("div");
      tile.className = "tile";
      tile.dataset.x = x;
      tile.dataset.y = y;
      tile.setAttribute("role", "gridcell");

      if (grid[y][x] === 1) {
        tile.classList.add("mine");
        tile.title = mineAt(x, y)?.serial ?? "mine";
      } else if (isCleared(x, y)) {
        tile.classList.add("cleared");
      }

      if (rover.x === x && rover.y === y) {
        const marker = document.createElement("div");
        marker.className = "rover-marker";
        tile.appendChild(marker);
      }

      tile.addEventListener("click", () => handleTileClick(x, y));
      gridEl.appendChild(tile);
    }
  }

  minesRemainingEl.textContent = mines.length;
  gridDimsEl.textContent = `${dimensions.x} x ${dimensions.y}`;
  roverPosEl.textContent = `(${rover.x}, ${rover.y})`;
}

function logMessage(text, isDetonation = false) {
  const entry = document.createElement("div");
  entry.className = "log-entry" + (isDetonation ? " detonation" : "");
  const time = new Date().toLocaleTimeString([], { hour12: false });
  entry.innerHTML = `<span class="log-time">${time}</span>${text}`;
  logEl.prepend(entry);
}

/* =========================================================================
   MOVEMENT + DEMINING
   ========================================================================= */

function moveRover(dx, dy) {
  const nx = rover.x + dx;
  const ny = rover.y + dy;

  if (nx < 0 || nx >= dimensions.x || ny < 0 || ny >= dimensions.y) {
    return; // out of bounds, ignore
  }

  rover = { x: nx, y: ny };
  logMessage(`Rover moved to (${nx}, ${ny}).`);

  const hit = mineAt(nx, ny);
  if (hit) {
    demineTile(hit);
  }

  renderGrid();
}

function handleTileClick(x, y) {
  const dx = x - rover.x;
  const dy = y - rover.y;
  // Only allow moving to an orthogonally adjacent tile, one step at a time.
  const isAdjacent = Math.abs(dx) + Math.abs(dy) === 1;
  if (isAdjacent) {
    moveRover(dx, dy);
  }
}

function demineTile(mine) {
  // Remove the mine from the source-of-truth list...
  mines = mines.filter((m) => m.serial !== mine.serial);
  // ...and remember the tile so it renders as "cleared" rather than plain blank.
  clearedTiles.push({ x: mine.x, y: mine.y });

  logMessage(`Mine ${mine.serial} demined at (${mine.x}, ${mine.y}).`, true);

  // This is the hook point for your backend: once mines/clearedTiles are
  // updated here, you'd POST the change (e.g. mine.serial) to Python so the
  // server-side state stays in sync with what's rendered client-side.
}

/* =========================================================================
   INIT
   ========================================================================= */

function initGame(dims, mineRows) {
  dimensions = { x: dims.x, y: dims.y };
  mines = mineRows.map((m) => ({ ...m }));
  clearedTiles = [];
  rover = { x: 0, y: 0 };
  logEl.innerHTML = "";
  logMessage("Mission started.");
  renderGrid();
}

document.addEventListener("keydown", (e) => {
  const moves = {
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
  };
  if (moves[e.key]) {
    e.preventDefault();
    moveRover(...moves[e.key]);
  }
});

document.getElementById("reset-btn").addEventListener("click", () => {
  initGame(INITIAL_DIMENSIONS, INITIAL_MINES);
});

initGame(INITIAL_DIMENSIONS, INITIAL_MINES);
