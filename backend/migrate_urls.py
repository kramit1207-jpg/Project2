"""
One-time script to migrate existing LinkedIn URLs to sanitized format.
Run this once to normalize all existing URLs in the database.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from utils import sanitize_linkedin_url

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/insightprofile"
)

def migrate_urls():
    """Migrate all LinkedIn URLs to sanitized format"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Get all profiles
            result = conn.execute(text("SELECT id, linkedin_url FROM humantic_profiles"))
            profiles = result.fetchall()
            
            print(f"Found {len(profiles)} profiles to migrate")
            
            updated = 0
            for profile_id, linkedin_url in profiles:
                try:
                    # Sanitize URL
                    sanitized_url = sanitize_linkedin_url(linkedin_url)
                    
                    if sanitized_url != linkedin_url:
                        # Update the URL
                        conn.execute(
                            text("UPDATE humantic_profiles SET linkedin_url = :new_url WHERE id = :id"),
                            {"new_url": sanitized_url, "id": profile_id}
                        )
                        print(f"  [OK] Updated: {linkedin_url} -> {sanitized_url}")
                        updated += 1
                    else:
                        print(f"  [-] Already sanitized: {linkedin_url}")
                        
                except Exception as e:
                    print(f"  [ERROR] Error with {linkedin_url}: {str(e)}")
            
            # Commit transaction
            trans.commit()
            print(f"\n[SUCCESS] Migration complete: {updated} URLs updated")
            
        except Exception as e:
            trans.rollback()
            print(f"\n[FAILED] Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("LinkedIn URL Migration Script")
    print("=" * 50)
    migrate_urls()
