let gameOver = false;  
let gameId = null;  
let BOARD_SIZE = 3
let move_no = 1

window.onload = startGame

const grid = document.getElementById("grid");
for (let i = 0; i < BOARD_SIZE; i++) {
    for (let j = 0; j < BOARD_SIZE; j++) {
        let cell = document.createElement("div");
        cell.classList.add("cell");
        cell.dataset.row = i;
        cell.dataset.col = j;
        cell.addEventListener("click", handleMove);
        grid.appendChild(cell);
    }
}

async function startGame() {
    gameOver = false
    move_no = 1
    let response = await fetch("/new_game_1");
    let data = await response.json();
    gameId = data.game_id;  
    updateBoard(data.board);
}

async function handleMove(event) {
    if (gameOver) return;
    if (!gameId) return alert("Game not started!");  

    
    let cell = event.target;
    let row = cell.dataset.row;
    let col = cell.dataset.col;

    

    let response = await fetch("/move_1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id:gameId, row: parseInt(row), col: parseInt(col) ,moveNo:move_no})
    });

    
    if (!response.ok) {
        console.error(`Error: ${response.status} ${response.statusText}`);
        return;
    }
    
    console.log("Response received");

    let data = await response.json();
    console.log(data);

    if (data.error) {
        alert(data.error);
        return;
    }

    updateBoard(data.board);
    move_no++


    if (data.winner) {
        setTimeout(() => {
        alert(`${data.winner} wins!`);},500)
        if (data.flag) {
        setTimeout(() => {
        alert(`${data.flag}`);
        },750)     
        }
        gameOver = true;  
        toggleBoard();   
    }
}


function toggleBoard() {
    let cells = document.querySelectorAll(".cell");

    if (gameOver === true) {
        cells.forEach(cell => {
            cell.removeEventListener("click", handleMove);  
            cell.onclick = () => alert("GAME OVER!");  
        });
    } else {
        cells.forEach(cell => {
            cell.onclick = null;  
            cell.addEventListener("click", handleMove);  
        });
    }
}

function updateBoard(board) {
    let cells = document.querySelectorAll(".cell");
    let aiMoves = []; 

    cells.forEach(cell => {
        let row = cell.dataset.row;
        let col = cell.dataset.col;
        let newValue = board[row][col];


        if (newValue === "O" && cell.textContent !== "O") {
            cell.setAttribute("data-mark", "O")
            aiMoves.push(cell);
        }   
        if (newValue === "X" && cell.textContent !== "X") {
            cell.setAttribute("data-mark", "X")
            cell.textContent = board[row][col];
        }    
        if (["/", "\\", "-", "|"].includes(newValue) && cell.textContent !== newValue) {
            cell.setAttribute("data-mark", "/")
            winMarks.push({ cell, value: newValue });
        }
        if (newValue === " ") {
            cell.textContent = board[row][col];
        }});


    aiMoves.forEach((cell, index) => {
        setTimeout(() => {
            cell.textContent = "O";
        }, index * 50);  
    });
}

async function resetGame() {
    if (!gameId) return alert("Game not started!");

    gameOver = false; 
    move_no=1
    toggleBoard();
    let response = await fetch("/reset_1", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id: gameId })  
    });

    if (!response.ok) {
        console.error(`Error: ${response.status} ${response.statusText}`);
        return;
    }

    let data = await response.json();
    console.log(data.message);  

    updateBoard(data.board);  
}
