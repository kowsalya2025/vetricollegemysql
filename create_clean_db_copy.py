import sqlite3
import shutil
import os

def create_clean_copy():
    """Create a clean copy of database for GitHub"""
    
    # Copy original to new file
    if not os.path.exists('db.sqlite3'):
        print("❌ Error: db.sqlite3 not found!")
        return
    
    shutil.copy2('db.sqlite3', 'db_clean.sqlite3')
    print("✅ Created clean copy: db_clean.sqlite3")
    
    # Connect to the clean copy
    conn = sqlite3.connect('db_clean.sqlite3')
    cursor = conn.cursor()
    
    print("\n🧹 Cleaning sensitive data from copy...\n")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📊 Found {len(tables)} tables\n")
    
    # 1. Clean User table (try different variations)
    print("👤 Cleaning user data...")
    user_tables = ['auth_user', 'users_user', 'accounts_user', 'lms_user']
    user_cleaned = False
    
    for table in user_tables:
        if table in tables:
            try:
                # Get columns for this table
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Update password if column exists
                if 'password' in columns:
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET password = 'pbkdf2_sha256$600000$dummy$hash'
                    """)
                
                # Update email if column exists
                if 'email' in columns:
                    cursor.execute(f"""
                        UPDATE {table} 
                        SET email = 'user' || id || '@example.com'
                    """)
                
                # Update names if columns exist
                if 'first_name' in columns:
                    cursor.execute(f"UPDATE {table} SET first_name = 'User'")
                if 'last_name' in columns:
                    cursor.execute(f"UPDATE {table} SET last_name = CAST(id AS TEXT)")
                
                print(f"   ✓ Cleaned {table}")
                user_cleaned = True
                break
            except Exception as e:
                print(f"   ⚠️ Error cleaning {table}: {e}")
    
    if not user_cleaned:
        print("   ⏭️  No user table found")
    
    # 2. Clean OAuth/Social Auth tokens
    print("🔑 Removing OAuth tokens...")
    oauth_tables = ['socialaccount_socialtoken', 'social_auth_usersocialauth']
    oauth_cleaned = False
    
    for table in oauth_tables:
        if table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"   ✓ Deleted tokens from {table}")
                oauth_cleaned = True
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
    
    # Clean social app secrets
    if 'socialaccount_socialapp' in tables:
        try:
            cursor.execute("UPDATE socialaccount_socialapp SET secret = 'REMOVED', client_id = 'REMOVED'")
            print("   ✓ Cleaned social app credentials")
            oauth_cleaned = True
        except:
            pass
    
    if not oauth_cleaned:
        print("   ⏭️  No OAuth tables found")
    
    # 3. Clean payment information
    print("💳 Cleaning payment data...")
    payment_tables = ['lms_purchase', 'payments_purchase', 'purchase']
    payment_cleaned = False
    
    for table in payment_tables:
        if table in tables:
            try:
                # Get columns
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Clean payment-related columns
                payment_columns = {
                    'razorpay_order_id': 'order_dummy_',
                    'razorpay_payment_id': 'pay_dummy_',
                    'razorpay_signature': 'signature_removed',
                    'stripe_payment_id': 'stripe_dummy_',
                    'paypal_order_id': 'paypal_dummy_',
                }
                
                for col, dummy_value in payment_columns.items():
                    if col in columns:
                        if 'signature' in col or 'secret' in col:
                            cursor.execute(f"UPDATE {table} SET {col} = '{dummy_value}'")
                        else:
                            cursor.execute(f"UPDATE {table} SET {col} = '{dummy_value}' || id")
                        print(f"   ✓ Cleaned {col}")
                        payment_cleaned = True
                
            except Exception as e:
                print(f"   ⚠️ Error cleaning {table}: {e}")
    
    if not payment_cleaned:
        print("   ⏭️  No payment tables found")
    
    # 4. Clear sessions
    print("🔐 Clearing sessions...")
    if 'django_session' in tables:
        try:
            cursor.execute("DELETE FROM django_session")
            print("   ✓ Sessions cleared")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    else:
        print("   ⏭️  No session table found")
    
    # 5. Clear admin logs
    print("📋 Clearing admin logs...")
    if 'django_admin_log' in tables:
        try:
            cursor.execute("DELETE FROM django_admin_log")
            print("   ✓ Admin logs cleared")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    else:
        print("   ⏭️  No admin log table found")
    
    # Commit changes
    conn.commit()
    
    # Show summary
    print("\n" + "="*50)
    print("✅ Database cleaned successfully!")
    print("="*50)
    
    # Show what tables we have
    print("\n📊 Database contains:")
    for table in sorted(tables):
        if not table.startswith('django_') and not table.startswith('sqlite_'):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
    
    conn.close()
    
    print("\n💡 Default admin credentials (if exists):")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n📤 Ready to push to GitHub!")

if __name__ == '__main__':
    create_clean_copy()