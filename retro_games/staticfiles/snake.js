let snake;
let food;
let score = 0;
let gameOver = false;
let direction = { x: 1, y: 0 }; // Начальное направление (вправо)

function setup() {
  createCanvas(400, 400);
  frameRate(10);
  snake = [{ x: 10, y: 10 }]; // Начальная позиция змейки
  food = { x: floor(random(20)), y: floor(random(20)) }; // Случайная позиция еды
}

function draw() {
  background(0);
  if (!gameOver) {
    drawSnake();
    drawFood();
    updateSnake();
  } else {
    textSize(32);
    fill(255);
    text("Game Over", 100, 200);
  }
}

function keyPressed() {
  // Изменяем направление только если оно не противоположно текущему
  if (keyCode === LEFT_ARROW && direction.x === 0) {
    direction = { x: -1, y: 0 };
  } else if (keyCode === RIGHT_ARROW && direction.x === 0) {
    direction = { x: 1, y: 0 };
  } else if (keyCode === UP_ARROW && direction.y === 0) {
    direction = { x: 0, y: -1 };
  } else if (keyCode === DOWN_ARROW && direction.y === 0) {
    direction = { x: 0, y: 1 };
  }
}

function drawSnake() {
  fill(0, 255, 0);
  snake.forEach(segment => rect(segment.x * 20, segment.y * 20, 20, 20));
}

function drawFood() {
  fill(255, 0, 0);
  rect(food.x * 20, food.y * 20, 20, 20);
}

function updateSnake() {
  // Вычисляем новую позицию головы
  let newHead = { x: snake[0].x + direction.x, y: snake[0].y + direction.y };
  
  // Проверяем столкновения
  if (
    newHead.x < 0 || newHead.x >= 20 || 
    newHead.y < 0 || newHead.y >= 20 || 
    snake.some(segment => segment.x === newHead.x && segment.y === newHead.y)
  ) {
    gameOver = true;
    sendScore();
    return;
  }

  // Добавляем новую голову
  snake.unshift(newHead);

  // Если съели еду
  if (newHead.x === food.x && newHead.y === food.y) {
    score += 10;
    food = { x: floor(random(20)), y: floor(random(20)) }; // Новая еда
  } else {
    snake.pop(); // Удаляем хвост, если не съели еду
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
        body: JSON.stringify({ player_name: playerName, score: score, game: 'snake' }) // Используем slug
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