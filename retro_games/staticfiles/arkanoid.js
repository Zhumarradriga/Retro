let paddle;
let ball;
let bricks;
let score = 0;
let gameOver = false;

function setup() {
  createCanvas(400, 400);
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
    let playerName = prompt("Game Over! Enter your name:");
    if (playerName) {
      fetch('/save_score/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ player_name: playerName, score: score, game: 'arkanoid' }) // Используем slug
      });
    }
  }

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}