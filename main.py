from sqlalchemy import text
from db import Database
from repositories import UserRepository, WalletRepository, TransactionRepository

# ======= VULNERABLE VS SECURE IMPLEMENTATION EXAMPLES =======

# VULNERABLE: Direct string concatenation (DO NOT USE)
def vulnerable_get_user(db_conn, user_id):
    """
    VULNERABLE: Direct string conatenation - DO NOT USE
    Demonstrates what NOT to do
    """
    # DO NOT DO THIS
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor = db_conn.cursor()
    cursor.execute(query) # VULNERABLE TO SQL INJECTION
    return cursor.fetchone()

# SECURE Use of parameterized queries
def secure_get_user(db_conn, user_id):
    """
    SECURE: Parameterized query
    """
    query = f"SELECT * FROM users WHERE Id = ?"
    cursor = db_conn.cursor()
    cursor.execute(query, (user_id,)) # SAFE: Parameters properly escaped
    return cursor.fetchone()

# VULNERABLE: Dynamic table or column names (DO NOT USE)
def vulnerable_sort_results(db_conn, table_name, sort_column, sort_direction):
    """
    VULNERABLE: Dynamic SQL with user input - DO NOT USE
    Demonstrates what NOT to do
    """
    # DO NOT DO THIS
    query = f"SELECT * FROM {table_name} ORDER BY {sort_column} {sort_direction}"
    cursor = db_conn.cursor()
    cursor.execute(query)  # VULNERABLE TO SQL INJECTION
    return cursor.fetchall()


# SECURE: Whitelist-based approach for dynamic fields
def secure_sort_results(db_conn, table_name, sort_column, sort_direction):
    """
    SECURE: Whitelist validation for dynamic fields
    """
    # Validate table name against whitelist
    allowed_tables = {'users', 'wallets', 'transactions'}
    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")
    
    # Validate sort column against whitelist (per table)
    allowed_columns = {
        'users': {'id', 'email', 'username', 'created_at'},
        'wallets': {'id', 'user_id', 'currency', 'balance', 'created_at'},
        'transactions': {'id', 'user_id', 'amount', 'created_at', 'status'}
    }
    
    if sort_column not in allowed_columns[table_name]:
        raise ValueError("Invalid sort column")
    
    # Validate sort direction
    if sort_direction not in ('ASC', 'DESC'):
        sort_direction = 'ASC'  # Default to safe value
    
    # Use SQLAlchemy text with parameters for dynamic parts
    query = text(f"SELECT * FROM {table_name} ORDER BY {sort_column} :sort_direction")
    
    # Execute with parameters
    cursor = db_conn.cursor()
    cursor.execute(query, {'sort_direction': sort_direction})
    
    return cursor.fetchall()

# VULNERABLE: LIKE clause with unescaped wildcards (DO NOT USE)
def vulnerable_search(db_conn, search_term):
    """
    VULNERABLE: Unescaped LIKE parameters - DO NOT USE
    Demonstrates what NOT to do
    """
    # DO NOT DO THIS
    query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%'"
    cursor = db_conn.cursor()
    cursor.execute(query)  # VULNERABLE TO SQL INJECTION
    return cursor.fetchall()


# SECURE: Properly escaped LIKE clause
def secure_search(db_conn, search_term):
    """
    SECURE: Properly escaped LIKE parameters
    """
    # Escape wildcard characters in the search term
    search_term = search_term.replace('%', r'\%').replace('_', r'\_')
    
    # Use parameterized query
    query = "SELECT * FROM users WHERE username LIKE %s"
    cursor = db_conn.cursor()
    cursor.execute(query, (f"%{search_term}%",))  # SAFE: Parameters properly escaped
    
    return cursor.fetchall()


def example_usage():
    """Example usage of the secure repository pattern"""
    
    # Initialize database connection
    db = Database("postgresql://user:pass@localhost/coinbase")
    
    # Create repositories
    user_repo = UserRepository(db)
    wallet_repo = WalletRepository(db)
    tx_repo = TransactionRepository(db)
    
    try:
        # Create a user (safely)
        user = user_repo.create_user(
            email="user@example.com",
            username="crypto_user",
            password_hash="$2b$12$abcdefghijklmnopqrstuv"  # Example hash
        )
        
        # Create a wallet (safely)
        wallet = wallet_repo.create_wallet(
            user_id=user.id,
            currency="BTC",
            address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
        )
        
        # Create a transaction (safely)
        tx = tx_repo.create_transaction(
            user_id=user.id,
            wallet_id=wallet.id,
            transaction_type="deposit",
            amount=0.1,
            fee=0.0001
        )
        
        # Get user transactions (safely)
        transactions = tx_repo.get_user_transactions(
            user_id=user.id,
            limit=10,
            transaction_type="deposit"
        )
        
        # Search transactions (safely)
        search_results = tx_repo.search_transactions(
            search_term="bc1q",  # Example search term
            user_id=user.id
        )
        
        print(f"Created user: {user.id}")
        print(f"Created wallet: {wallet.id}")
        print(f"Created transaction: {tx.id}")
        print(f"Found {len(transactions)} transactions")
        print(f"Search returned {len(search_results)} results")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# ======= BEST PRACTICES FOR SQL INJECTION PREVENTION =======

def sql_injection_prevention_guidelines():
    """SQL Injection prevention guidelines for Coinbase developers"""
    guidelines = """
SQL INJECTION PREVENTION GUIDELINES FOR COINBASE DEVELOPERS

1. NEVER use string concatenation or f-strings to build SQL queries with user input
   BAD:  query = f"SELECT * FROM users WHERE username = '{username}'"
   GOOD: query = "SELECT * FROM users WHERE username = %s"
         cursor.execute(query, (username,))

2. ALWAYS use parameterized queries or prepared statements
   - In Python with psycopg2: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
   - In Python with SQLAlchemy: session.query(User).filter(User.id == user_id).first()

3. Use ORM frameworks when possible
   - SQLAlchemy automatically handles parameter binding
   - ORM usage prevents direct SQL manipulation

4. Validate and sanitize all user inputs
   - Validate type (string, integer, UUID, etc.)
   - Validate format (email, username, crypto address)
   - Validate ranges for numeric values
   - Use whitelisting approaches for dynamic fields

5. Use whitelists for dynamic table/column names
   - Never allow direct table or column names from user input
   - Maintain approved lists of valid values

6. Implement proper error handling
   - Don't expose SQL errors to users
   - Log errors securely without exposing sensitive data
   - Return generic error messages to clients

7. Use the principle of least privilege
   - Database users should have minimal required permissions
   - Use different accounts for read vs. write operations
   - Don't use admin accounts for application connections

8. Implement query timeouts
   - Prevent long-running or resource-exhausting queries
   - Configure database connection pools properly

9. Regularly audit your code for SQL injection vulnerabilities
   - Use static analysis tools to detect potential issues
   - Conduct security code reviews
   - Perform penetration testing

10. Special considerations for cryptocurrency applications:
    - Extra care for balance/amount calculations
    - Crypto addresses must be validated thoroughly
    - Implement transaction rate limiting
    - Add double-checks for withdrawal operations
    """
    
    return guidelines


# ======= AUTOMATED SQL INJECTION TESTING =======
def test_sql_resistance(func, test_input):
    """Test function for SQL injection resistance"""
    try:
        # Try executing the function with malicious input
        result = func(test_input)
        return True, "Function executed without error"
    except Exception as e:
        # If an exception is thrown, the test passes
        # (assuming proper validation/escaping happening)
        return True, f"Function correctly rejected malicious input: {str(e)}"
    
def run_sqli_tests():
    """Run SQL injection tests on repository functions"""
    db = Database("postgres://user:pass@localhost/coinbase")
    user_repo = UserRepository(db)    
    
    # Malicious inputs to test
    malicious_inputs = [
        "x' OR '1'='1",                # Basic OR injection
        "x'; DROP TABLE users; --",     # Table deletion attempt
        "x' UNION SELECT * FROM users WHERE '1'='1", # UNION attack
        "x'); UPDATE users SET is_admin=TRUE WHERE username='victim'; --", # Data modification
        "x' OR username IS NOT NULL; --" # Mass data dump
    ]
    
    results = []
    for input_test in malicious_inputs:
        # Test user search function
        success, message = test_sql_resistance(
            lambda x: user_repo.search_users(x),
            input_test
        )
        results.append(f"Test with '{input_test}': {'PASSED' if success else 'FAILED'} - {message}")
        

if __name__ == "__main__":
    # Example usage
    example_usage()
    
    # Print guidelines
    print("\nSQL Injection Prevention Guidelines:")
    print(sql_injection_prevention_guidelines())
    
    # Run tests
    print("\nRunning SQL Injection Tests:")
    results = run_sqli_tests()
    for result in results:
        print(result)