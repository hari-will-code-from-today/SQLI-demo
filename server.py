from flask import Flask, request, jsonify,send_file,send_from_directory
from flask_cors import CORS 
import uuid
import time
import threading
import random
import sqlite3

app = Flask(__name__)
CORS(app)
FLAG1="HTB{tw000_g00d_"
FLAG2="f0ur_r34l?_"
FLAG3="8784703363}"
MAX_GAMES = 1000
games={}
scores={}

# Create database
conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS scores (user TEXT, score INTEGER)")
conn.commit()

#PART 1
@app.route("/new_game_1", methods=["GET"])
def new_game_1():
    cleanup_old_games()
    game_id = str(uuid.uuid4())[:10]  # Generate a short unique ID
    games[game_id] = [[" " for _ in range(3)] for _ in range(3)]  # Create a new board for this game
    return jsonify({"game_id": game_id, "board": games[game_id]})  # Send ID to client
@app.route("/move_1", methods=["POST"])
def gameplay_1():
    data = request.json
    game_id = data.get("game_id")
    row, col = data["row"], data["col"]
    moveNo=data.get("moveNo")

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    board = games[game_id]  # Get the correct board

    if board[row][col] != " ":
        return jsonify({"error": "Cell is already occupied!"}), 400
    
    if moveNo>2:
        board[row][col] = "O"
        if check_win_1("O",board):
            return jsonify({"board": board, "winner": "AI"})
    else:
        board[row][col] = "X"
    # Check if the player won
        if check_win_1("X",board):
            response = jsonify({"board": board, "winner": "Player", "flag": FLAG1})  
            games.pop(game_id, None) 
            return response
    ai_move_1(board)

    # Check if AI won
    if check_win_1("O",board):
        return jsonify({"board": board, "winner": "AI"})

    return jsonify({"board": board, "winner": None})
def ai_move_1(board):
    RANDROW, RANDCOLUMN = random.randint(0, 3-1), random.randint(0,3-1)

    # Keep generating new random positions until an empty cell is found
    while board[RANDROW][RANDCOLUMN] != " ":
        RANDROW, RANDCOLUMN = random.randint(0, 3-1), random.randint(0, 3-1)
    board[RANDROW][RANDCOLUMN] = "O"
def check_win_1(player,board):
    """Checks if a player has won and modifies the board accordingly"""
    for i in range(3):
        for j in range(3):
            # Horizontal ---
            if j <= 3 - 3 and all(board[i][j + k] == player for k in range(3)):
                return True
            # Vertical |
            if i <= 3 - 3 and all(board[i + k][j] == player for k in range(3)):
                return True
            # Diagonal \
            if i <= 3 - 3 and j <= 3 - 3 and all(board[i + k][j + k] == player for k in range(3)):
                return True
            # Diagonal /
            if i >= 3 -1 and j <= 3 - 3 and all(board[i - k][j + k] == player for k in range(3)):
                return True
    return False
@app.route("/reset_1", methods=["POST"])
def reset_game_1():
    data = request.json
    game_id = data.get("game_id")
    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400
    games[game_id] = [[" " for _ in range(3)] for _ in range(3)] # Reset the board
    return jsonify({"message": "Game reset!", "board": games[game_id]})


#PART 2
@app.route("/new_game_2", methods=["GET"])
def new_game_2():
    cleanup_old_games()
    game_id = str(uuid.uuid4())[:10]  # Generate a short unique ID
    games[game_id] = [[" " for _ in range(10)] for _ in range(10)]  # Create a new board for this game
    return jsonify({"game_id": game_id, "board": games[game_id]})  # Send ID to client
@app.route("/move_2", methods=["POST"])
def gameplay_2():
    data = request.json
    game_id = data.get("game_id")
    row, col = data["row"], data["col"]

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    board = games[game_id]  # Get the correct board

    if board[row][col] != " ":
        return jsonify({"error": "Cell is already occupied!"}), 400

    board[row][col] = "X"
    # Check if the player won
    if check_win_2("X",board):
        games.pop(game_id, None)  # Avoid KeyError
        response = jsonify({"board": board, "winner": "Player", "flag": FLAG2})  

        return response

    def delayed_ai_move_2():
        time.sleep(0.015)  # Delay AI move by 100ms (time window for exploit)
        ai_move_2(row,col,board)
          # AI places its moves

    threading.Thread(target=delayed_ai_move_2).start()
    # AI moves twice


    # Check if AI won
    if check_win_2("O",board):
        return jsonify({"board": board, "winner": "AI"})

    return jsonify({"board": board, "winner": None})

def ai_move_2(ROW,COLUMN,board):
    x=0
    #1 from sides
    if ROW - 1 >=0 and ROW +1<10 :
        if board[ROW+1][COLUMN] == "X" and board[ROW-1][COLUMN] == " " and x <=4:
            board[ROW-1][COLUMN] = "O"
            x+=1
        if board[ROW-1][COLUMN] == "X" and board[ROW+1][COLUMN] == " " and x <=4: 
            board[ROW+1][COLUMN] = "O"
            x+=1
    if  COLUMN+1 <10 and COLUMN-1>=0: 
        if board[ROW][COLUMN-1] == "X" and board[ROW][COLUMN+1] == " " and x <=4: 
            board[ROW][COLUMN+1] = "O"
            x+=1
        if board[ROW][COLUMN+1] == "X" and board[ROW][COLUMN-1] == " " and x <=4:
            board[ROW][COLUMN-1] = "O"
            x+=1   
    
    #1 from diagonals
    if ROW -1 >= 0 and COLUMN-1>=0 and ROW +1 <10 and COLUMN+1<10 :
        if board[ROW-1][COLUMN -1] == "X" and board[ROW+1][COLUMN+1] == " " and x <=4:
            board[ROW+1][COLUMN+1] = "O"
            x+=1 
        if board[ROW-1][COLUMN +1] == "X" and board[ROW+1][COLUMN-1] == " " and x <=4:
            board[ROW+1][COLUMN-1] = "O"
            x+=1
        if board[ROW+1][COLUMN+1] == "X"and  board[ROW-1][COLUMN-1] == " " and x <=4:
            board[ROW-1][COLUMN -1]  = "O"
            x+=1 
        if board[ROW+1][COLUMN-1] == "X"and board[ROW-1][COLUMN +1] == " " and x <=4:
            board[ROW-1][COLUMN +1] = "O"
            x+=1
            
    #2 from sides
    if  ROW +2<10 :
        if board[ROW+2][COLUMN] == "X" and board[ROW+1][COLUMN] == " " and x <=4:
            board[ROW+1][COLUMN] = "O"
            x+=1
    if ROW - 2 >=0 :
        if board[ROW-2][COLUMN] == "X" and board[ROW-1][COLUMN] == " " and x <=4: 
            board[ROW-1][COLUMN] = "O"
            x+=1
    if COLUMN-2>=0: 
        if board[ROW][COLUMN-2] == "X" and board[ROW][COLUMN-1] == " " and x <=4: 
            board[ROW][COLUMN-1] = "O"
            x+=1
    if  COLUMN+2 <10 :
        if board[ROW][COLUMN+2] == "X" and board[ROW][COLUMN+1] == " " and x <=4:
            board[ROW][COLUMN+1] = "O"
            x+=1    

    #2 from diagonals
    if ROW -2 >= 0 and COLUMN-2>=0 and x <=4:
        if board[ROW-2][COLUMN -2] == "X" and board[ROW-1][COLUMN-1] == " " :
            board[ROW-1][COLUMN-1] = "O"
            x+=1 
    if ROW -2 <10 and COLUMN+2<10 and x <=4:
        if board[ROW-2][COLUMN +2] == "X" and board[ROW-1][COLUMN+1] == " " :
            board[ROW-1][COLUMN+1] = "O"
            x+=1
    if ROW +2 <10 and COLUMN+2<10 and x <=4:
        if board[ROW+2][COLUMN+2] == "X" and board[ROW+1][COLUMN +1] == " ":
            board[ROW+1][COLUMN +1]  = "O"
            x+=1 
    if ROW +2 <10 and COLUMN-2<10 and x <=4:
        if board[ROW+2][COLUMN-2] == "X" and board[ROW+1][COLUMN -1] == " " :
            board[ROW+1][COLUMN -1] = "O"
        return

def check_win_2(player,board):
    """Checks if a player has won and modifies the board accordingly"""
    for i in range(10):
        for j in range(10):
            # Horizontal ---
            if j <= 10 - 4 and all(board[i][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i][j + k] = "-"
                return True
            # Vertical |
            if i <= 10 - 4 and all(board[i + k][j] == player for k in range(4)):
                for k in range(4):
                    board[i + k][j] = "|"
                return True
            # Diagonal \
            if i <= 10 - 4 and j <= 10 - 4 and all(board[i + k][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i + k][j + k] = "\\"
                return True
            # Diagonal /
            if i >= 3 and j <= 10 - 4 and all(board[i - k][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i - k][j + k] = "/"
                return True
    return False
@app.route("/get_board_2", methods=["GET"])
def get_board_2():
    game_id = request.args.get("game_id")

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    board = games[game_id]

    # Check if AI won after its move
    if check_win_2("O",board):
        return jsonify({"board": board, "winner": "AI"})

    return jsonify({"board": board, "winner": None})
@app.route("/reset_2", methods=["POST"])
def reset_game_2():
    data = request.json
    game_id = data.get("game_id")

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    games[game_id] = [[" " for _ in range(10)] for _ in range(10)]  # Reset the board
    return jsonify({"message": "Game reset!", "board": games[game_id]})


#PART 3
@app.route("/new_game_3", methods=["GET"])
def new_game_3():
    game_id = str(uuid.uuid4())[:10]  # Generate a short unique ID
    games[game_id] = [[" " for _ in range(10)] for _ in range(10)]  # Create a new board for this game
    scores[game_id]=[0,0]
    return jsonify({"game_id": game_id, "board": games[game_id],"score":scores[game_id]})  # Send ID to client
@app.route("/move_3", methods=["POST"])
def gameplay_3():
    data = request.json
    game_id = data.get("game_id")
    row, col = data["row"], data["col"]

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    board = games[game_id]  # Get the correct board
    score=scores[game_id]

    if board[row][col] != " ":
        return jsonify({"error": "Cell is already occupied!"}), 400

    board[row][col] = "X"
    # Check if the player won
    if check_win_3("X",board):
        scores[game_id][0]+=1
        return jsonify({"board": board, "winner": "Player","score":score})

    ai_move_3(row,col,board,score[0])
          # AI places its moves

    # Check if AI won
    if check_win_3("O",board):
        scores[game_id][1]+=1
        return jsonify({"board": board, "winner": "AI","score":score})

    return jsonify({"board": board, "winner": None})

def ai_move_3(ROW,COLUMN,board,score):
    if score == 0:
        x = 5
    elif score==1:
        x = 4
    else:
        x=0
    print(x)
    if ROW - 1 >=0 and ROW +1<10 :
        if board[ROW+1][COLUMN] == "X" and board[ROW-1][COLUMN] == " " and x <=4:
            board[ROW-1][COLUMN] = "O"
            x+=1
        if board[ROW-1][COLUMN] == "X" and board[ROW+1][COLUMN] == " " and x <=4: 
            board[ROW+1][COLUMN] = "O"
            x+=1
    if  COLUMN+1 <10 and COLUMN-1>=0: 
        if board[ROW][COLUMN-1] == "X" and board[ROW][COLUMN+1] == " " and x <=4: 
            board[ROW][COLUMN+1] = "O"
            x+=1
        if board[ROW][COLUMN+1] == "X" and board[ROW][COLUMN-1] == " " and x <=4:
            board[ROW][COLUMN-1] = "O"
            x+=1   
    
    #1 from diagonals
    if ROW -1 >= 0 and COLUMN-1>=0 and ROW +1 <10 and COLUMN+1<10 :
        if board[ROW-1][COLUMN -1] == "X" and board[ROW+1][COLUMN+1] == " " and x <=4:
            board[ROW+1][COLUMN+1] = "O"
            x+=1 
        if board[ROW-1][COLUMN +1] == "X" and board[ROW+1][COLUMN-1] == " " and x <=4:
            board[ROW+1][COLUMN-1] = "O"
            x+=1
        if board[ROW+1][COLUMN+1] == "X"and  board[ROW-1][COLUMN-1] == " " and x <=4:
            board[ROW-1][COLUMN -1]  = "O"
            x+=1 
        if board[ROW+1][COLUMN-1] == "X"and board[ROW-1][COLUMN +1] == " " and x <=4:
            board[ROW-1][COLUMN +1] = "O"
            x+=1
            
    #2 from sides
    if  ROW +2<10 :
        if board[ROW+2][COLUMN] == "X" and board[ROW+1][COLUMN] == " " and x <=4:
            board[ROW+1][COLUMN] = "O"
            x+=1
    if ROW - 2 >=0 :
        if board[ROW-2][COLUMN] == "X" and board[ROW-1][COLUMN] == " " and x <=4: 
            board[ROW-1][COLUMN] = "O"
            x+=1
    if COLUMN-2>=0: 
        if board[ROW][COLUMN-2] == "X" and board[ROW][COLUMN-1] == " " and x <=4: 
            board[ROW][COLUMN-1] = "O"
            x+=1
    if  COLUMN+2 <10 :
        if board[ROW][COLUMN+2] == "X" and board[ROW][COLUMN+1] == " " and x <=4:
            board[ROW][COLUMN+1] = "O"
            x+=1    

    #2 from diagonals
    if ROW -2 >= 0 and COLUMN-2>=0 and x <=4:
        if board[ROW-2][COLUMN -2] == "X" and board[ROW-1][COLUMN-1] == " " :
            board[ROW-1][COLUMN-1] = "O"
            x+=1 
    if ROW -2 <10 and COLUMN+2<10 and x <=4:
        if board[ROW-2][COLUMN +2] == "X" and board[ROW-1][COLUMN+1] == " " :
            board[ROW-1][COLUMN+1] = "O"
            x+=1
    if ROW +2 <10 and COLUMN+2<10 and x <=4:
        if board[ROW+2][COLUMN+2] == "X" and board[ROW+1][COLUMN +1] == " ":
            board[ROW+1][COLUMN +1]  = "O"
            x+=1 
    if ROW +2 <10 and COLUMN-2<10 and x <=4:
        if board[ROW+2][COLUMN-2] == "X" and board[ROW+1][COLUMN -1] == " " :
            board[ROW+1][COLUMN -1] = "O"
        return

def check_win_3(player,board):
    """Checks if a player has won and modifies the board accordingly"""
    for i in range(10):
        for j in range(10):
            # Horizontal ---
            if j <= 10 - 4 and all(board[i][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i][j + k] = "-"
                return True
            # Vertical |
            if i <= 10 - 4 and all(board[i + k][j] == player for k in range(4)):
                for k in range(4):
                    board[i + k][j] = "|"
                return True
            # Diagonal \
            if i <= 10 - 4 and j <= 10 - 4 and all(board[i + k][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i + k][j + k] = "\\"
                return True
            # Diagonal /
            if i >= 3 and j <= 10 - 4 and all(board[i - k][j + k] == player for k in range(4)):
                for k in range(4):
                    board[i - k][j + k] = "/"
                return True
    return False
@app.route("/reset_3", methods=["POST"])
def reset_game():
    data = request.json
    game_id = data.get("game_id")

    if game_id not in games:
        return jsonify({"error": "Invalid game ID"}), 400

    games[game_id] = [[" " for _ in range(10)] for _ in range(10)]   # Reset the board
    return jsonify({"message": "Game reset!", "board": games[game_id],"score":scores[game_id]})

@app.route("/submit_score_3", methods=["POST"])  # 🔥 Use POST instead of GET!
def submit_score():
    data = request.json  # Accept only JSON data, not URL params
    game_id = data.get("game_id")
    username = data.get("username") 
    if game_id not in games:
            return jsonify({"error": "Invalid game ID"}), 400
    blocked_keywords = ["DROP", "DELETE", "ALTER", "TRUNCATE", "RENAME", "UPDATE",]
    if any(keyword.lower() in username.lower() for keyword in blocked_keywords):
        return jsonify({"cringe": "What is that cringe name bro?"})    
    
    query = f"INSERT INTO scores VALUES ('{username}', {scores[game_id][0]})"
    print(query)
    try:
        # Save the score to the database
        conn.execute(query)
        conn.commit()

        query2 = "SELECT user, score FROM scores ORDER BY ROWID DESC LIMIT 1"
        cursor = conn.execute(query2)
        result = cursor.fetchone()

        if result:
            print(f"Last inserted user: {result[0]}, Score: {result[1]}")

        if result[1] > 2:
            games.pop(game_id, None)
            return jsonify({"flag": FLAG3})
        
        return jsonify({"message": "Score submitted!"})
    
    except Exception as e:
        return jsonify({"error": str(e)})

#HOMEPAGE
@app.route('/')
def serve_html():
    level = request.cookies.get("level","uno")
    if level == "tres":
        return send_file("tres.html")
    if level == "dos":
        return send_file("dos.html")
    else:
        return send_file("uno.html")
    
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

def cleanup_old_games():
    trash = 0
    while len(games) > MAX_GAMES:
        trash = len(games) - MAX_GAMES
        games.pop(next(iter(games)))
    
    print("Clearing ",trash,"games") 

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,threaded=True)
