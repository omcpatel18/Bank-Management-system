import sqlite3
import re
from datetime import datetime

DB_FILE = "bank.sqlite.db"

# ============ DATABASE SETUP ============
def setup_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            pin TEXT NOT NULL,
            balance REAL DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT,
            amount REAL,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!\n")

# ============ NEW USER REGISTRATION (Auto ID) ============
def new_user():
    """Register a new user - ID generated automatically"""
    print("\n" + "="*50)
    print("NEW USER REGISTRATION")
    print("="*50 + "\n")
    
    # 1. Get name
    while True:
        temp_name = input("Enter your Name:\n")
        if temp_name.isalpha():
            name = temp_name
            break
        else:
            print("Enter only characters. No numbers or special characters.\n")
    
    # 2. Get phone number
    while True:
        temp_phone = input("Enter your Phone Number (10 digits):\n")
        if temp_phone.isdigit() and len(temp_phone) == 10:
            phone = temp_phone
            break
        else:
            print("Enter a valid 10 digit number.\n")
    
    # 3. Get email
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    while True:
        temp_email = input("Enter your Email:\n")
        if re.match(email_pattern, temp_email):
            email = temp_email
            break
        else:
            print("Invalid email! Enter a valid email address.\n")
    
    # 4. Create PIN
    while True:
        temp_pin = input("Create a 4 digit PIN (no spaces):\n")
        if temp_pin.isdigit() and len(temp_pin) == 4:
            pin = temp_pin
            break
        else:
            print("Invalid PIN! Must be exactly 4 digits.\n")
    
    # 5. Save to database (ID auto-generated)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, phone, email, pin, balance)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, pin, 0))
        conn.commit()
        
        # Get the auto-generated ID
        generated_id = cursor.lastrowid
        conn.close()
        
        print("\n" + "="*50)
        print("✓ Account Created Successfully!")
        print("="*50)
        print(f"Your User ID: {generated_id}")
        print(f"Name: {name}")
        print(f"Phone: {phone}")
        print("Save your User ID - you need it to login!")
        print("="*50 + "\n")
        
    except sqlite3.IntegrityError as e:
        print(f"✗ Error: Phone or Email already registered!\n")

# ============ LOGIN WITH USER ID ============
def login():
    """
    Login using User ID and PIN
    No phone lookup - direct ID verification
    """
    attempt = 3
    
    while attempt > 0:
        print("\n" + "="*50)
        print("LOGIN")
        print("="*50 + "\n")
        
        try:
            user_id = int(input("Enter your User ID:\n"))
        except ValueError:
            print("Invalid User ID! Please enter a number.\n")
            continue
        
        # Get stored PIN for this user_id
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, pin FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            print(f"✗ No user found with ID: {user_id}\n")
            attempt -= 1
            if attempt > 0:
                print(f"Attempts left: {attempt}\n")
            continue
        
        stored_name, stored_pin = result
        
        # Get PIN input
        pin_input = input("Enter your 4 digit PIN:\n")
        
        # Verify PIN
        if pin_input == stored_pin:
            print(f"\n✓ Login successful!")
            print(f"Welcome, {stored_name}!\n")
            return user_id
        else:
            print("✗ Incorrect PIN!\n")
            attempt -= 1
            if attempt > 0:
                print(f"Attempts left: {attempt}\n")
            else:
                print("Too many failed attempts. Access denied.\n")
    
    return None

# ============ GET USER DATA ============
def get_user_data(user_id):
    """Retrieve all data for a user using their ID"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, phone, email, balance 
        FROM users 
        WHERE id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_data = {
            "id": result[0],
            "name": result[1],
            "phone": result[2],
            "email": result[3],
            "balance": result[4]
        }
        return user_data
    else:
        return None

# ============ BANKING OPERATIONS ============
def credit(user_id):
    """Credit money to account"""
    try:
        amount = float(input("Enter amount to credit:\n"))
        if amount <= 0:
            print("Amount must be greater than 0.\n")
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Update balance for this user_id
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", 
                      (amount, user_id))
        
        # Record transaction with this user_id
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, "CREDIT", amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        
        # Get updated balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]
        conn.close()
        
        print(f"✓ Successfully credited: ${amount}")
        print(f"New balance: ${new_balance}\n")
    
    except ValueError:
        print("Invalid amount! Please enter a number.\n")

# ============ DEBIT ============
def debit(user_id):
    """Debit money from account"""
    try:
        amount = float(input("Enter amount to debit:\n"))
        if amount <= 0:
            print("Amount must be greater than 0.\n")
            return
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        current_balance = cursor.fetchone()[0]
        
        if amount > current_balance:
            print(f"✗ Insufficient balance! Available: ${current_balance}\n")
            conn.close()
            return
        
        # Update balance for this user_id
        cursor.execute("UPDATE users SET balance = balance - ? WHERE id = ?", 
                      (amount, user_id))
        
        # Record transaction with this user_id
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, "DEBIT", amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        
        # Get updated balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        new_balance = cursor.fetchone()[0]
        conn.close()
        
        print(f"✓ Successfully debited: ${amount}")
        print(f"New balance: ${new_balance}\n")
    
    except ValueError:
        print("Invalid amount! Please enter a number.\n")

# ============ Show balance ============
def show_balance(user_id):
    """Show current balance"""
    user_data = get_user_data(user_id)
    print(f"\n{'='*50}")
    print(f"Account Holder: {user_data['name']}")
    print(f"Current Balance: ${user_data['balance']}")
    print(f"{'='*50}\n")

# ============ transaction_history ============
def transaction_history(user_id):
    """Show transaction history for this user_id"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT transaction_type, amount, date FROM transactions 
        WHERE user_id = ? 
        ORDER BY date DESC LIMIT 10
    """, (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    
    print(f"\n{'='*60}")
    print("Transaction History (Last 10 Transactions)")
    print(f"{'='*60}")
    
    if transactions:
        for trans_type, amount, date in transactions:
            print(f"{date} | {trans_type:10} | ${amount}")
    else:
        print("No transactions yet.")
    
    print(f"{'='*60}\n")

# ============ DASHBOARD ============
def dashboard(user_id):
    """Main dashboard - user_id used to manage all operations"""
    user_data = get_user_data(user_id)
    print(f"\nWelcome to Dashboard, {user_data['name']}!")
    print(f"User ID: {user_id}\n")
    
    while True:
        print("="*50)
        print("1. View Profile")
        print("2. Credit Money")
        print("3. Debit Money")
        print("4. Check Balance")
        print("5. Transaction History")
        print("6. Send Money")
        print("7. Logout")
        print("="*50)
        
        choice = input("Enter your choice (1-7):\n")
        
        match choice:
            case "1":
                user_data = get_user_data(user_id)
                print(f"\n{'='*50}")
                print(f"User ID: {user_data['id']}")
                print(f"Name: {user_data['name']}")
                print(f"Phone: {user_data['phone']}")
                print(f"Email: {user_data['email']}")
                print(f"Balance: ${user_data['balance']}")
                print(f"{'='*50}\n")
            case "2":
                credit(user_id)
            case "3":
                debit(user_id)
            case "4":
                calculate_interest(user_id, annual_rate=10.0)
                show_balance(user_id)
            case "5":
                transaction_history(user_id)
            case "6":
                send_money(user_id)
            case "7":
                print("Logging out...\n")
                return
            case _:
                print("Invalid choice! Try again.\n")

# ============ SEND_MONEY ============
def send_money(sender_user_id):
    """
    Transfer money between user accounts
    Parameters: sender_user_id (the logged-in user's ID)
    Returns: True if successful, False if failed
    """
    try:
        # Get sender's information from database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, balance FROM users WHERE id = ?", (sender_user_id,))
        sender = cursor.fetchone()
        
        if not sender:
            print(f"❌ Sender account (ID: {sender_user_id}) not found.\n")
            conn.close()
            return False
        
        sender_id, sender_name, sender_balance = sender
        
        # Get receiver information from user
        print("\n" + "="*60)
        print("SEND MONEY".center(60))
        print("="*60)
        print(f"From: {sender_name} (ID: {sender_id})")
        print("-"*60)
        
        # Get receiver ID
        try:
            receiver_id = int(input("Enter Receiver's Account Number (User ID): "))
        except ValueError:
            print("❌ Invalid Account ID! Must be a number.\n")
            conn.close()
            return False
        
        # Validate receiver ID is not same as sender
        if sender_id == receiver_id:
            print("❌ Sender and receiver cannot be the same person.\n")
            conn.close()
            return False
        
        # Get receiver information from database
        cursor.execute("SELECT id, name, balance FROM users WHERE id = ?", (receiver_id,))
        receiver = cursor.fetchone()
        
        if not receiver:
            print(f"❌ Receiver account (ID: {receiver_id}) not found.\n")
            conn.close()
            return False
        
        receiver_id, receiver_name, receiver_balance = receiver
        
        # Get amount to transfer
        try:
            amount = float(input("Enter Amount to Transfer: ₹"))
        except ValueError:
            print("❌ Invalid amount! Must be a number.\n")
            conn.close()
            return False
        
        # Validate amount
        if amount <= 0:
            print("❌ Amount must be greater than 0.\n")
            conn.close()
            return False
        
        if sender_balance < amount:
            print(f"❌ Insufficient balance! Available: ₹{sender_balance:.2f}\n")
            conn.close()
            return False
        
        # Calculate new balances
        new_sender_balance = sender_balance - amount
        new_receiver_balance = receiver_balance + amount
        
        # Perform transfer
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                      (new_sender_balance, sender_id))
        cursor.execute("UPDATE users SET balance = ? WHERE id = ?", 
                      (new_receiver_balance, receiver_id))
        
        # Record transaction for sender
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, date)
            VALUES (?, ?, ?, ?)
        """, (sender_id, "SEND", amount, now))
        
        # Record transaction for receiver
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, date)
            VALUES (?, ?, ?, ?)
        """, (receiver_id, "RECEIVE", amount, now))
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        # Display success message
        print("\n" + "="*60)
        print("✅ TRANSFER SUCCESSFUL".center(60))
        print("="*60)
        print(f"From:          {sender_name} (ID: {sender_id})")
        print(f"To:            {receiver_name} (ID: {receiver_id})")
        print(f"Amount:        ₹{amount:.2f}")
        print(f"Time:          {now}")
        print("-"*60)
        print(f"Your Balance:  ₹{new_sender_balance:.2f}")
        print("="*60 + "\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error during transfer: {e}\n")
        try:
            conn.close()
        except:
            pass
        return False

# ============ INTEREST CALCULATION ============
def calculate_interest(user_id, annual_rate=10.0):
    """
    Calculate interest based on days since last transaction and update balance
    
    Parameters:
        user_id: User's ID
        annual_rate: Annual interest rate (default 4%)
    
    Returns: True if successful, False if failed
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ User ID {user_id} not found.\n")
            conn.close()
            return False
        
        current_balance = result[0]
        
        # Get last transaction date
        cursor.execute("""
            SELECT date FROM transactions 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        
        if not result:
            print("❌ No transactions found. Cannot calculate interest.\n")
            conn.close()
            return False
        
        last_transaction_date = result[0]
        
        # Calculate days elapsed
        last_date = datetime.strptime(last_transaction_date, "%Y-%m-%d %H:%M:%S")
        current_date = datetime.now()
        days_elapsed = (current_date - last_date).days
        
        if days_elapsed == 0:
            print("❌ Not enough time has passed. Interest calculated daily.\n")
            conn.close()
            return False
        
        # Calculate interest: (Balance × Rate × Days) / 36500
        interest = (current_balance * annual_rate * (days_elapsed / 365)) / 100
        interest = round(interest, 2)
        
        # Update balance
        new_balance = current_balance + interest
        
        cursor.execute(
            "UPDATE users SET balance = ? WHERE id = ?",
            (new_balance, user_id)
        )
        
        # Record interest transaction
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_type, amount, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, "INTEREST", interest, now))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Interest Applied Successfully!")
        print(f"Interest Earned: ₹{interest:.2f}")
        print(f"New Balance: ₹{new_balance:.2f}\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False
    
# ============ MAIN PROGRAM ============
def main():
    """Main program flow"""
    setup_database()
    
    while True:
        print("\n" + "="*50)
        print("Bank Management System")
        print("="*50)
        print("1. New User Registration")
        print("2. Login")
        print("3. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-3):\n")
        
        if choice == "1":
            new_user()
        
        elif choice == "2":
            user_id = login()
            
            if user_id is not None:
                dashboard(user_id)
        
        elif choice == "3":
            print("Thank you for using Bank Management System!")
            break
        
        else:
            print("Invalid choice!\n")


if __name__ == "__main__":
    main()
