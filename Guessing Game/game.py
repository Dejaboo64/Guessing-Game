import random
import time 
import database
import getpass

def login_or_register():
    """Handle user login or registration"""
    while True:
        print("\n" + "="*50)
        print(" WELCOME TO GUESSING GAME ".center(50))
        print("="*50)
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        print("="*50)
        
        choice = input("Choose option (1-3): ").strip()
        
        if choice == "1":
            # Login
            username = input("Enter username: ").strip()
            password = getpass.getpass("Enter password: ")
            
            success, message = database.login_user(username, password)
            print(message)
            
            if success:
                return username
            else:
                input("\nPress Enter to continue...")
                
        elif choice == "2":
            # Register
            print("\n--- REGISTER NEW ACCOUNT ---")
            username = input("Choose username: ").strip()
            
            if not username:
                print("Username cannot be empty!")
                input("\nPress Enter to continue...")
                continue
            
            password = getpass.getpass("Choose password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                print("Passwords do not match!")
                input("\nPress Enter to continue...")
                continue
            
            if len(password) < 4:
                print("Password must be at least 4 characters long!")
                input("\nPress Enter to continue...")
                continue
            
            success, message = database.create_user(username, password)
            print(message)
            
            if success:
                print("You can now login with your new account!")
                input("\nPress Enter to continue...")
            else:
                input("\nPress Enter to continue...")
                
        elif choice == "3":
            print("Thanks for playing! Goodbye!")
            return None
        else:
            print("Invalid choice! Please try again.")
            input("\nPress Enter to continue...")

def show_main_menu(username):
    """Display the main menu with various options"""
    while True:
        print("\n" + "="*50)
        print(f" WELCOME, {username}! ".center(50))
        print("="*50)
        print("1. Play Game")
        print("2. View My Statistics")
        print("3. View Leaderboards")
        print("4. Logout")
        print("5. Exit Game")
        print("="*50)
        
        choice = input("Choose option (1-5): ").strip()
        
        if choice == "1":
            return "play"
        elif choice == "2":
            database.get_player_stats(username)
            input("\nPress Enter to continue...")
        elif choice == "3":
            view_leaderboards_menu()
        elif choice == "4":
            confirm = input("Are you sure you want to logout? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                print(f"Goodbye, {username}! Logging out...")
                return "logout"
        elif choice == "5":
            confirm = input("Are you sure you want to exit? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                print(f"Thanks for playing, {username}! Goodbye!")
                return "exit"
        else:
            print("Invalid choice! Please try again.")
            input("\nPress Enter to continue...")

def view_leaderboards_menu():
    """Display leaderboard viewing options"""
    while True:
        print("\n" + "="*50)
        print(" LEADERBOARD MENU ".center(50))
        print("="*50)
        print("1. View Normal Mode Leaderboard")
        print("2. View Hard Mode Leaderboard")
        print("3. View Both Leaderboards")
        print("4. Return to Main Menu")
        print("="*50)
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1":
            database.show_leaderboard_by_mode('normal')
            input("\nPress Enter to continue...")
        elif choice == "2":
            database.show_leaderboard_by_mode('hard')
            input("\nPress Enter to continue...")
        elif choice == "3":
            database.show_all_leaderboards()
            input("\nPress Enter to continue...")
        elif choice == "4":
            break
        else:
            print("Invalid choice! Please try again.")
            input("\nPress Enter to continue...")

def play_game(username):
    """Main game function"""
    try:
        print("\n" + "="*50)
        print(" LET'S PLAY! ".center(50))
        print("="*50)
        
        secret_number = random.randint(1, 100)
        print("\nSecret Number Has Been Generated (between 1 and 100).")
        
        # Add input validation for mode selection
        while True:
            mode = input("Choose difficulty (Normal / Hard): ").strip().lower()
            if mode in ["normal", "hard"]:
                break
            print("Invalid input. Please enter 'Normal' or 'Hard'.")

        if mode == "hard":
            max_attempts = 5
            time_limit = 60
            print("\n" + "-"*40)
            print(" HARD MODE ACTIVATED! ")
            print(f"• You have {max_attempts} guesses")
            print("• You have 1 minute")
            print("-"*40)
        else:
            max_attempts = None
            time_limit = 300
            print("\n" + "-"*40)
            print(" NORMAL MODE ACTIVATED! ")
            print("• Unlimited guesses")
            print("• You have 5 minutes")
            print("-"*40)

        # Start timing AFTER mode selection
        start_time = time.time()
        attempts = 0

        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time >= time_limit:
                print("\n" + "!"*40)
                print(" TIME IS UP!!! ".center(40))
                print("!"*40)
                print(f"The secret number was: {secret_number}")
                break

            # Show remaining time for hard mode
            if mode == "hard":
                remaining = int(time_limit - elapsed_time)
                print(f"\nTime remaining: {remaining} seconds")

            # Add input validation for guess
            try:
                guess = int(input("\nEnter your guess (1-100): "))
                if guess < 1 or guess > 100:
                    print("Please enter a number between 1 and 100.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            attempts += 1

            if guess < secret_number:
                print("Too Low!")
            elif guess > secret_number:
                print("Too High!")
            else:
                # Format time for display
                formatted_time = database.format_time(elapsed_time)
                
                print("\n" + "="*40)
                print(" CORRECT! ".center(40))
                print("="*40)
                print(f"The number was: {secret_number}")
                print(f"Attempts: {attempts}")
                print(f"Time taken: {formatted_time}")
                print("="*40)
                
                # Update score with mode information
                database.update_score(username, mode, attempts, elapsed_time)
                
                # Check if it's a new personal record
                database.check_personal_record(username, mode, attempts, elapsed_time)
                break

            if max_attempts and attempts >= max_attempts:
                print("\n" + "!"*40)
                print(" GAME OVER! ".center(40))
                print("!"*40)
                print(f"You ran out of guesses!")
                print(f"The secret number was: {secret_number}")
                break

            # Show remaining attempts for hard mode
            if max_attempts:
                remaining_attempts = max_attempts - attempts
                print(f"Attempts remaining: {remaining_attempts}")

    except Exception as e:
        print(f"An error occurred during gameplay: {e}")

def main():
    try:
        database.create_database()
        
        # Handle login/registration
        username = login_or_register()
        
        if username:
            while True:
                # Show main menu and get user choice
                action = show_main_menu(username)
                
                if action == "play":
                    play_game(username)
                    # After game, automatically show updated stats
                    print("\nYour updated statistics:")
                    database.get_player_stats(username)
                    input("\nPress Enter to return to main menu...")
                elif action == "logout":
                    # Return to login screen
                    username = login_or_register()
                    if not username:
                        break
                elif action == "exit":
                    break
                    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        print("\n" + "="*50)
        print(" THANKS FOR PLAYING! ".center(50))
        print("="*50)
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()