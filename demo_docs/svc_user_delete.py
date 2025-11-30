import logging
from datetime import datetime, timedelta
from database import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_user_data(user_id):
    """
    Permanently deletes user data from the primary database.
    This function is triggered 90 days after account closure.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        logger.info(f"Starting deletion process for user: {user_id}")
        
        # 1. Delete from Users table
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        # 2. Delete from Audit Logs (if policy requires, usually retained)
        # cursor.execute("DELETE FROM audit_logs WHERE user_id = %s", (user_id,))
        
        conn.commit()
        logger.info(f"Successfully deleted data for user: {user_id}")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to delete user {user_id}: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # Example usage
    delete_user_data("550e8400-e29b-41d4-a716-446655440000")
