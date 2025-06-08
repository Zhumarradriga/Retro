let paddle;
let ball;
let bricks;
let score = 0;
let gameOver = false;

function setup() {
  let canvas = createCanvas(400, 400);
  canvas.parent('gameContainer'); // Привязываем холст к div#gameContainer
  paddle = { x: 200, y: 380, w: 80, h: 10 };
  ball = { x: 200, y: 360, dx: 4, dy: -4 };
  bricks = [];
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 8; j++) {
      bricks.push({ x: j * 50 + 10, y: i * 20 + 50, w: 40, h: 10 });
    }
  }
}

function draw() {
  background(0);
  if (!gameOver) {
    drawPaddle();
    drawBall();
    drawBricks();
    updateBall();
  } else {
    textSize(32);
    fill(255);
    text("Game Over", 100, 200);
  }
}

function keyPressed() {
  if (keyCode === LEFT_ARROW) paddle.x -= 20;
  if (keyCode === RIGHT_ARROW) paddle.x += 20;
  paddle.x = constrain(paddle.x, 0, width - paddle.w);
  if (keyCode === 82 && gameOver) { // Клавиша R
    score = 0;
    gameOver = false;
    setup(); // Перезапуск игры
  }
}

function drawPaddle() {
  fill(255);
  rect(paddle.x, paddle.y, paddle.w, paddle.h);
}

function drawBall() {
  fill(255);
  ellipse(ball.x, ball.y, 10, 10);
}

function drawBricks() {
  fill(255, 0, 0);
  bricks.forEach(brick => rect(brick.x, brick.y, brick.w, brick.h));
}

function updateBall() {
  ball.x += ball.dx;
  ball.y += ball.dy;
  if (ball.x <= 0 || ball.x >= width) ball.dx *= -1;
  if (ball.y <= 0) ball.dy *= -1;
  if (ball.y >= paddle.y && ball.x >= paddle.x && ball.x <= paddle.x + paddle.w) {
    ball.dy *= -1;
  }
  bricks = bricks.filter(brick => {
    if (ball.x >= brick.x && ball.x <= brick.x + brick.w && ball.y >= brick.y && ball.y <= brick.y + brick.h) {
      ball.dy *= -1;
      score += 10;
      return false;
    }
    return true;
  });
  if (ball.y >= height) {
    gameOver = true;
    sendScore();
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
      body: JSON.stringify({ score: score, game: 'arkanoid' })
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