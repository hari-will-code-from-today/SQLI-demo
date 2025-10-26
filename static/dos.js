let gameOver = false;  
let gameId = null;  

window.onload = startGame

const grid = document.getElementById("grid");
for (let i = 0; i < 10; i++) {
    for (let j = 0; j < 10; j++) {
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
    let response = await fetch("/new_game_2");
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

    

    let response = await fetch("/move_2", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ game_id:gameId, row: parseInt(row), col: parseInt(col) })
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

    setTimeout(async () => {
        let aiResponse = await fetch(`/get_board_2?game_id=${gameId}`);
        let aiData = await aiResponse.json();
        updateBoard(aiData.board);

        if (aiData.winner) {  
            setTimeout(() => {
                alert(`${aiData.winner} wins!`);},500)
            gameOver = true;
        }
    }, 15);  

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


function updateBoard(board,) {
    let cells = document.querySelectorAll(".cell");
    let aiMoves = [];
    let winMarks = [];
    cells.forEach(cell => {
        let row = cell.dataset.row;
        let col = cell.dataset.col;
        let newValue = board[row][col];

        if (newValue === "O" && cell.textContent !== "O") {
            cell.setAttribute("data-mark", "O")
            aiMoves.push({ cell, row, col });
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
        }
    });
    aiMoves.forEach((move, index) => {
        setTimeout(() => {
            move.cell.textContent = "O";  
        }, index * 50);  
    });   
    winMarks.forEach((mark, index) => {
        setTimeout(() => {
            mark.cell.textContent = mark.value;  
        }, aiMoves.length * 50 + index * 50);  
    });   
    
}



async function resetGame() {
    if (!gameId) return alert("Game not started!");

    gameOver = false; 
    toggleBoard();
    let response = await fetch("/reset_2", {
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