let gameOver = false;  
let gameId = null;  
let rounds = 5
let flag = false
let lastClickTime = 0; 
let hintTimeout

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
    flag = false
    toggleBoard()
    let response = await fetch("/new_game_3");
    let data = await response.json();
    gameId = data.game_id;  
    score = data.score;
    updateBoard(data.board,score);
}

document.getElementById("hint-sprite").addEventListener("click", function () {
    let currentTime = Date.now();
    if (currentTime - lastClickTime < 500) {
        clickCount++;
    } else {
        clickCount = 0; 
    }
    lastClickTime = currentTime;
    if (flag === true) {
        if (clickCount > 4) {
            expression("blush");
            setTimeout(() => {
                clickCount = 0;
            }, 3000);
        }
        else{
        let pun = puns[Math.floor(Math.random() * puns.length)];
        spriteTalkSequence([pun]);  
        }} 
        else {
        if (clickCount < 5) {
            spriteTalkSequence(["Don't talk to me without scoring atleast 3"]);
        } else {
            expression("stop");
            spriteTalkSequence(["Stop harassing me!"]);
            setTimeout(() => {
                clickCount = 0;
            }, 3000);
        }
    }
});

function expression(mood){
    document.getElementById("hint-sprite").src = `static/${mood}.png`;
    setTimeout(() => {
        document.getElementById("hint-sprite").src = "static/tic-tac-hoe.png";
    }, 3000);
}

function spriteTalkSequence(messages, index = 0) {
    if (index >= messages.length) return;
    let hintText = document.getElementById("hint-text");
    clearTimeout(hintTimeout);
    
    hintText.textContent = messages[index];
    hintText.style.display = "block";
    hintText.style.opacity = "1";

    
    hintTimeout = setTimeout(() => {
        hintText.style.opacity = "0";

        
        hintTimeout = setTimeout(() => {
            hintText.style.display = "none";
            spriteTalkSequence(messages, index + 1); 
        }, 1000); 
    }, 2000);
}

async function handleMove(event) {
    if (gameOver) return;
    if (!gameId) return alert("Game not started!");    
    let cell = event.target;
    let row = cell.dataset.row;
    let col = cell.dataset.col;
    let response = await fetch("/move_3", {
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

    updateBoard(data.board,data.score);

    if (data.winner) {
        setTimeout(() => {
        alert(`${data.winner} wins!`);},500)

        if(data.score[0]+data.score[1] < rounds){
            setTimeout(() => {
                resetGame();},750)
        }
        else{
            setTimeout(() => {
                alert(`GAME OVER!!`);
                submit_score_3(gameId);
            },750)            
            gameOver = true;  
            toggleBoard();   
        }
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

function updateBoard(board,score) {
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
    
    document.getElementById("player").textContent = `Player:${score[0]}`
    document.getElementById("ai").textContent = `Ai:${score[1]}`
}

async function resetGame() {
    if (!gameId) return alert("Game not started!");
    gameOver = false; 
    toggleBoard();
    let response = await fetch("/reset_3", {
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


function submit_score_3(game_id) {
    let username = prompt("Enter your username:");
    if (username) {

        fetch("/submit_score_3", {  
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: game_id, username: username })
        })
        .then(response => {
            return response.json(); 
        })
        .then(data => {
            if (data.flag) {  
                flag= true
                spriteTalkSequence([`That's crazy man....`,`You can have my number: ${data.flag}`]);      
                puns.push(`${data.flag}`)
                setTimeout(() => {
                    spriteTalkSequence([`You can have my number: ${data.flag}`]);
                }, 3000);                
               
            }
            if(data.message){
                alert(data.message);
                expression("cringe");
                spriteTalkSequence([`you got some serious skill issue`]);
            }
            if(data.error){
                alert(data.error);
            }
            if(data.cringe){
                expression("cringe");
                spriteTalkSequence([`${data.cringe}`]);
            }
        })
    } else {
        alert("Username cannot be empty!");
    }
}

const puns = [
    "Are you an ‘X’? Because you’ve marked my heart ❤️.",
    "Are we playing Tic-Tac-Toe, or just falling for each other? 🥰",
    "I’d let you win just to see you smile. 🥺❤️",
    "You’re my winning move. Every. Single. Time. 😉",
    "Are you an ‘O’? Because I can’t seem to block you from my mind 😏.",
    "I’m not just aiming for four in a row… I’m aiming for forever. 💘",
    "Forget X’s and O’s, I just want you. 😍",
    "I’d love to go first… but I’d rather let you steal my heart. 😏",
    "Wanna play? Winner gets to plan our first date. 😉",
    "Your strategy is cute, but your smile is even better. 😍",
    "This game is Tic-Tac-Toe, but you’re a definite win for me. 😘",
    "I’d go for four in a row, but you’re the only one I see. 💖",
    "You must be my perfect move, because I can’t resist picking you! 😏",
    "X or O, it doesn’t matter—I just want to play with you. 😉",
    "You don’t need to strategize, you’ve already won me over! 😚",
    "You must be a diagonal win… because you caught me off guard. 😏",
    "If love was a game, I’d let you win every time. 😘",
    "I don’t need a turn—because I already know you’re the one. 💞",
    "The only thing better than winning? Playing with you. 😉",
    "I like my Tic-Tac-Toe games like my relationships—simple, fun, and full of X’s and O’s! 💋",
    "They say X’s and O’s are kisses and hugs… so let’s play a long game. 😘",
    "I’m not here to block your moves… I’m here to steal your heart. ❤️",
    "You keep making all the right moves… in my heart! 💖",
    "You’re like a perfect game—once in a lifetime. 😏",
    "Forget four in a row—I just need one date with you. 😏",
    "I may be playing Tic-Tac-Toe, but you’re the only one I’m chasing. 😍",
    "I’ll go first… straight into your heart. 💘",
    "Your turn? How about turning this into something special? 😉",
    "Checkmate! Oh wait… wrong game, but I still won your heart. 💖",
    "Are you undefeated? Because I can't seem to get over you. 😘",
    "I don’t mind losing, as long as I win you. ❤️",
    "I’d never block you… unless you’re stealing someone else’s heart. 😉",
    "One more game? Or do you just want to skip to the part where we’re together? 😏",
    "Tic-Tac-Toe? More like Tic-Tac-Oh-You’re-So-Cute. 😘"
];