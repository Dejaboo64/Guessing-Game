import sqlite3
import os
import hashlib

db_path = os.path.join(os.path.expanduser("~"), "Documents", "game.db")

def hash_password(password):
    """Hash a password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_database():
    """Create the database and players table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table with NULL as default for best_guess
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            best_guess_normal INTEGER,
            best_time_normal REAL,
            games_played_normal INTEGER DEFAULT 0,
            best_guess_hard INTEGER,
            best_time_hard REAL,
            games_played_hard INTEGER DEFAULT 0
        )
        """)

        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")

def create_user(username, password):
    """Create a new user account with NULL values for best_guess"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT username FROM players WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists!"

        # Hash the password and create new user with NULL best_guess values
        hashed_password = hash_password(password)
        cursor.execute("""
        INSERT INTO players (
            username, password, 
            best_guess_normal, best_time_normal, games_played_normal,
            best_guess_hard, best_time_hard, games_played_hard
        )
        VALUES (?, ?, NULL, NULL, 0, NULL, NULL, 0)
        """, (username, hashed_password))

        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Error creating account: {e}"

def login_user(username, password):
    """Login an existing user"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if username exists and verify password
        cursor.execute("SELECT password FROM players WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_password = result[0]
            if stored_password == hash_password(password):
                return True, "Login successful!"
            else:
                return False, "Incorrect password!"
        else:
            return False, "Username not found!"
    except Exception as e:
        return False, f"Error logging in: {e}"

def update_score(username, mode, attempts, time_taken):
    """Update score after winning for specific mode - handles NULL values"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if mode == "normal":
            cursor.execute("""
            UPDATE players
            SET
                best_guess_normal = CASE
                                    WHEN best_guess_normal IS NULL THEN ?
                                    WHEN ? < best_guess_normal THEN ?
                                    ELSE best_guess_normal
                                END,
                best_time_normal = CASE
                                    WHEN best_time_normal IS NULL THEN ?
                                    WHEN ? < best_time_normal THEN ?
                                    ELSE best_time_normal
                                END,
                games_played_normal = games_played_normal + 1
            WHERE username = ?
            """, (attempts, attempts, attempts, time_taken, time_taken, time_taken, username))
        else:  # hard mode
            cursor.execute("""
            UPDATE players
            SET
                best_guess_hard = CASE
                                WHEN best_guess_hard IS NULL THEN ?
                                WHEN ? < best_guess_hard THEN ?
                                ELSE best_guess_hard
                            END,
                best_time_hard = CASE
                                WHEN best_time_hard IS NULL THEN ?
                                WHEN ? < best_time_hard THEN ?
                                ELSE best_time_hard
                            END,
                games_played_hard = games_played_hard + 1
            WHERE username = ?
            """, (attempts, attempts, attempts, time_taken, time_taken, time_taken, username))

        conn.commit()
        conn.close()
        print(f"Score updated successfully for {mode} mode.")
        return True
    except Exception as e:
        print(f"Error updating score: {e}")
        return False

def format_time(seconds):
    """Format time in minutes and seconds"""
    if seconds is None:
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def show_leaderboard_by_mode(mode):
    """Display the leaderboard for a specific mode - handles NULL values"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if mode == "normal":
            cursor.execute("""
            SELECT username, best_guess_normal, best_time_normal, games_played_normal
            FROM players
            WHERE best_guess_normal IS NOT NULL
            ORDER BY best_guess_normal ASC, best_time_normal ASC
            LIMIT 10
            """)
        else:  # hard mode
            cursor.execute("""
            SELECT username, best_guess_hard, best_time_hard, games_played_hard
            FROM players
            WHERE best_guess_hard IS NOT NULL
            ORDER BY best_guess_hard ASC, best_time_hard ASC
            LIMIT 10
            """)

        players = cursor.fetchall()
        conn.close()

        mode_display = mode.upper()
        print("\n" + "="*80)
        print(f" {mode_display} MODE LEADERBOARD ".center(80))
        print("="*80)
        print(f"{'Rank':<6} {'Username':<20} {'Best Guess':<15} {'Best Time':<15} {'Games':<10}")
        print("-"*80)
        
        if players:
            rank = 1
            for player in players:
                username, best_guess, best_time, games_played = player
                formatted_time = format_time(best_time)
                print(f"{rank:<6} {username:<20} {best_guess:<15} {formatted_time:<15} {games_played:<10}")
                rank += 1
        else:
            print("No scores yet. Play a game to appear on the leaderboard!".center(80))
        
        print("="*80)

    except Exception as e:
        print(f"Error displaying leaderboard: {e}")

def show_all_leaderboards():
    """Display both Normal and Hard mode leaderboards"""
    print("\n" + "="*80)
    print(" GAME LEADERBOARDS ".center(80))
    print("="*80)
    
    show_leaderboard_by_mode('normal')
    print("\n")
    show_leaderboard_by_mode('hard')

def get_player_stats(username):
    """Get individual player statistics - handles NULL values"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            best_guess_normal, best_time_normal, games_played_normal,
            best_guess_hard, best_time_hard, games_played_hard
        FROM players 
        WHERE username = ?
        """, (username,))

        stats = cursor.fetchone()
        conn.close()

        if stats:
            print("\n" + "="*50)
            print(f" STATISTICS FOR: {username} ".center(50))
            print("="*50)
            print("\nNORMAL MODE:")
            if stats[0] is not None:
                print(f"  Best Guess: {stats[0]}")
                print(f"  Best Time: {format_time(stats[1])}")
            else:
                print("  No games played yet in Normal mode")
            print(f"  Games Played: {stats[2]}")
            
            print("\nHARD MODE:")
            if stats[3] is not None:
                print(f"  Best Guess: {stats[3]}")
                print(f"  Best Time: {format_time(stats[4])}")
            else:
                print("  No games played yet in Hard mode")
            print(f"  Games Played: {stats[5]}")
            print("="*50)
        else:
            print("No statistics found for this user.")

    except Exception as e:
        print(f"Error getting player stats: {e}")

def check_personal_record(username, mode, attempts, time_taken):
    """Check if the player beat their personal record - handles NULL values"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if mode == "normal":
            cursor.execute("""
            SELECT best_guess_normal, best_time_normal 
            FROM players 
            WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result:
                best_guess, best_time = result
                
                # First game in this mode
                if best_guess is None:
                    print("\n" + "*"*50)
                    print("FIRST GAME IN NORMAL MODE!".center(50))
                    print("*"*50)
                    print(f"Your first guess count: {attempts}")
                    print("*"*50)
                elif attempts < best_guess:
                    print("\n" + "*"*50)
                    print("NEW PERSONAL RECORD!".center(50))
                    print("*"*50)
                    print(f"Previous best guess: {best_guess}")
                    print(f"New best guess: {attempts}")
                    print("*"*50)
                elif attempts == best_guess and (best_time is None or time_taken < best_time):
                    print("\n" + "*"*50)
                    print("NEW PERSONAL BEST TIME!".center(50))
                    print("*"*50)
                    print(f"You matched your best guess ({best_guess}) with a faster time!")
                    print("*"*50)
        
        else:  # hard mode
            cursor.execute("""
            SELECT best_guess_hard, best_time_hard 
            FROM players 
            WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result:
                best_guess, best_time = result
                
                # First game in this mode
                if best_guess is None:
                    print("\n" + "*"*50)
                    print("FIRST GAME IN HARD MODE!".center(50))
                    print("*"*50)
                    print(f"Your first guess count: {attempts}")
                    print("*"*50)
                elif attempts < best_guess:
                    print("\n" + "*"*50)
                    print("NEW PERSONAL RECORD!".center(50))
                    print("*"*50)
                    print(f"Previous best guess: {best_guess}")
                    print(f"New best guess: {attempts}")
                    print("*"*50)
                elif attempts == best_guess and (best_time is None or time_taken < best_time):
                    print("\n" + "*"*50)
                    print("NEW PERSONAL BEST TIME!".center(50))
                    print("*"*50)
                    print(f"You matched your best guess ({best_guess}) with a faster time!")
                    print("*"*50)

        conn.close()
    except Exception as e:
        print(f"Error checking personal record: {e}")