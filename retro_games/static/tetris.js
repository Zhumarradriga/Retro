

let grid;
let currentPiece;
let score = 0;
let gameOver = false;

function setup() {
  let canvas=createCanvas(300, 600);
  canvas.parent('gameContainer');
  grid = Array(20).fill().map(() => Array(10).fill(0));
  currentPiece = newPiece();
}

function draw() {
  background(0);
  drawGrid();
  if (!gameOver) {
    drawPiece(currentPiece);
    if (frameCount % 30 === 0) {
      movePieceDown();
    }
  } else {
    textSize(32);
    fill(255);
    text("Game Over", 50, 300);
  }
}

function keyPressed() {
  if (!gameOver) {
    if (keyCode === LEFT_ARROW) currentPiece.x--;
    if (keyCode === RIGHT_ARROW) currentPiece.x++;
    if (keyCode === DOWN_ARROW) movePieceDown();
    if (keyCode === UP_ARROW) rotatePiece();
  }
  if (keyCode === 82 && gameOver) { // Клавиша R
    score = 0;
    gameOver = false;
    setup(); // Перезапуск игры
  }
}

function newPiece() {
  const shapes = [
    [[1, 1, 1, 1]], // I
    [[1, 1], [1, 1]], // O
    [[1, 1, 1], [0, 1, 0]] // T
  ];
  return {
    shape: random(shapes),
    x: 4,
    y: 0
  };
}

function drawGrid() {
  for (let y = 0; y < 20; y++) {
    for (let x = 0; x < 10; x++) {
      if (grid[y][x]) {
        fill(255);
        rect(x * 30, y * 30, 30, 30);
      }
    }
  }
}

function drawPiece(piece) {
  fill(255, 0, 0);
  for (let y = 0; y < piece.shape.length; y++) {
    for (let x = 0; x < piece.shape[y].length; x++) {
      if (piece.shape[y][x]) {
        rect((piece.x + x) * 30, (piece.y + y) * 30, 30, 30);
      }
    }
  }
}

function movePieceDown() {
  currentPiece.y++;
  if (collides(currentPiece)) {
    currentPiece.y--;
    placePiece();
    clearLines();
    currentPiece = newPiece();
    if (collides(currentPiece)) {
      gameOver = true;
      sendScore();
    }
  }
}

function collides(piece) {
  for (let y = 0; y < piece.shape.length; y++) {
    for (let x = 0; x < piece.shape[y].length; x++) {
      if (piece.shape[y][x]) {
        let newX = piece.x + x;
        let newY = piece.y + y;
        if (newX < 0 || newX >= 10 || newY >= 20 || (newY >= 0 && grid[newY][newX])) {
          return true;
        }
      }
    }
  }
  return false;
}

function placePiece() {
  for (let y = 0; y < currentPiece.shape.length; y++) {
    for (let x = 0; x < currentPiece.shape[y].length; x++) {
      if (currentPiece.shape[y][x]) {
        grid[currentPiece.y + y][currentPiece.x + x] = 1;
      }
    }
  }
}

function clearLines() {
  for (let y = 19; y >= 0; y--) {
    if (grid[y].every(cell => cell)) {
      grid.splice(y, 1);
      grid.unshift(Array(10).fill(0));
      score += 100;
    }
  }
}

function rotatePiece() {
  let newShape = currentPiece.shape[0].map((_, i) => 
    currentPiece.shape.map(row => row[i]).reverse()
  );
  let tempShape = currentPiece.shape;
  currentPiece.shape = newShape;
  if (collides(currentPiece)) {
    currentPiece.shape = tempShape;
  }
}

function sendScore() {
  const accessToken = localStorage.getItem('access_token');
  if (!accessToken) {
      alert('Please log in to submit your score.');
      window.location.href = '/login/';
      return;
  }
  const options = {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ score: score, game: 'tetris' })
  };
  fetchWithAuth('/save_score/', options)
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              alert('Score submitted!');
          } else {
              alert('Error submitting score.');
          }
      })
      .catch(error => console.error('Error:', error));
}