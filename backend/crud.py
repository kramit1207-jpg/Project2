"""
CRUD (Create, Read, Update, Delete) operations for database models.
Provides caching logic to reduce external API calls.
"""
import logging
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from models import HumanticProfile, GeminiAnalysis

# Configure logging
logger = logging.getLogger(__name__)

# Cache expiry configuration (in days)
CACHE_EXPIRY_DAYS = 30


def get_profile_by_linkedin_url(
    db: Session,
    linkedin_url: str
) -> Optional[HumanticProfile]:
    """
    Retrieve a Humantic profile by LinkedIn URL.
    
    Args:
        db: Database session
        linkedin_url: LinkedIn profile URL to search for
        
    Returns:
        HumanticProfile if found, None otherwise
    """
    try:
        profile = db.query(HumanticProfile).filter(
            HumanticProfile.linkedin_url == linkedin_url
        ).first()
        
        if profile:
            logger.info(f"Found cached profile for URL: {linkedin_url}")
        else:
            logger.info(f"No cached profile found for URL: {linkedin_url}")
            
        return profile
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return None


def create_humantic_profile(
    db: Session,
    linkedin_url: str,
    user_id: str,
    profile_data: Dict[str, Any],
    big_five_scores: Dict[str, float]
) -> Optional[HumanticProfile]:
    """
    Create a new Humantic profile in the database.
    
    Args:
        db: Database session
        linkedin_url: LinkedIn profile URL
        user_id: Humantic user ID
        profile_data: Full profile data from Humantic API
        big_five_scores: Extracted Big Five personality scores
        
    Returns:
        Created HumanticProfile or None if error
    """
    try:
        profile = HumanticProfile(
            linkedin_url=linkedin_url,
            user_id=user_id,
            profile_data=profile_data,
            big_five_scores=big_five_scores
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Created new profile: {profile.id} for URL: {linkedin_url}")
        return profile
        
    except IntegrityError as e:
        logger.warning(f"Profile already exists for URL: {linkedin_url}")
        db.rollback()
        # Return existing profile
        return get_profile_by_linkedin_url(db, linkedin_url)
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        db.rollback()
        return None


def create_gemini_analysis(
    db: Session,
    humantic_profile_id: str,
    summary: str,
    strengths: list,
    weaknesses: list,
    raw_response: Dict[str, Any]
) -> Optional[GeminiAnalysis]:
    """
    Create a new Gemini analysis linked to a Humantic profile.
    
    Args:
        db: Database session
        humantic_profile_id: UUID of parent Humantic profile
        summary: Summary text from Gemini
        strengths: List of strengths
        weaknesses: List of weaknesses
        raw_response: Full raw response from Gemini
        
    Returns:
        Created GeminiAnalysis or None if error
    """
    try:
        analysis = GeminiAnalysis(
            humantic_profile_id=humantic_profile_id,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            raw_response=raw_response
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Created new analysis: {analysis.id} for profile: {humantic_profile_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        db.rollback()
        return None


def get_latest_analysis(
    db: Session,
    humantic_profile_id: str
) -> Optional[GeminiAnalysis]:
    """
    Get the most recent Gemini analysis for a profile.
    
    Args:
        db: Database session
        humantic_profile_id: UUID of Humantic profile
        
    Returns:
        Latest GeminiAnalysis or None if not found
    """
    try:
        analysis = db.query(GeminiAnalysis).filter(
            GeminiAnalysis.humantic_profile_id == humantic_profile_id
        ).order_by(GeminiAnalysis.created_at.desc()).first()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        return None


def is_profile_expired(profile: HumanticProfile, expiry_days: int = CACHE_EXPIRY_DAYS) -> bool:
    """
    Check if a profile has expired based on creation date.
    
    Args:
        profile: HumanticProfile to check
        expiry_days: Number of days before expiry (default: CACHE_EXPIRY_DAYS)
        
    Returns:
        True if expired, False otherwise
    """
    if not profile:
        return True
        
    expiry_date = profile.created_at + timedelta(days=expiry_days)
    is_expired = datetime.utcnow() > expiry_date
    
    if is_expired:
        logger.info(f"Profile {profile.id} has expired (created: {profile.created_at})")
    
    return is_expired


def get_or_create_analysis(
    db: Session,
    linkedin_url: str,
    force_refresh: bool = False
) -> Tuple[Optional[HumanticProfile], Optional[GeminiAnalysis], bool]:
    """
    Main caching logic: Check if analysis exists in cache, return it if valid.
    
    Args:
        db: Database session
        linkedin_url: LinkedIn profile URL
        force_refresh: If True, ignore cache and return None (forces new API calls)
        
    Returns:
        Tuple of (HumanticProfile, GeminiAnalysis, cache_hit)
        - cache_hit=True means data was retrieved from cache
        - cache_hit=False means new API calls are needed
    """
    # If force refresh, skip cache
    if force_refresh:
        logger.info(f"Force refresh requested for: {linkedin_url}")
        return None, None, False
    
    # Check if profile exists in cache
    profile = get_profile_by_linkedin_url(db, linkedin_url)
    
    if not profile:
        logger.info(f"Cache miss (no profile): {linkedin_url}")
        return None, None, False
    
    # Check if profile has expired
    if is_profile_expired(profile):
        logger.info(f"Cache miss (expired): {linkedin_url}")
        return None, None, False
    
    # Check if Gemini analysis exists
    analysis = get_latest_analysis(db, str(profile.id))
    
    if not analysis:
        logger.info(f"Profile exists but no analysis: {linkedin_url}")
        # Return profile so we don't need to call Humantic again
        return profile, None, False
    
    # Cache hit - return cached data
    logger.info(f"Cache hit: {linkedin_url}")
    return profile, analysis, True


def update_profile_data(
    db: Session,
    profile_id: str,
    profile_data: Dict[str, Any],
    big_five_scores: Dict[str, float]
) -> Optional[HumanticProfile]:
    """
    Update an existing profile's data.
    
    Args:
        db: Database session
        profile_id: UUID of profile to update
        profile_data: New profile data
        big_five_scores: New Big Five scores
        
    Returns:
        Updated HumanticProfile or None if error
    """
    try:
        profile = db.query(HumanticProfile).filter(
            HumanticProfile.id == profile_id
        ).first()
        
        if not profile:
            logger.error(f"Profile not found: {profile_id}")
            return None
        
        profile.profile_data = profile_data
        profile.big_five_scores = big_five_scores
        profile.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated profile: {profile_id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.rollback()
        return None


def delete_profile(db: Session, linkedin_url: str) -> bool:
    """
    Delete a profile and all associated analyses (cascade delete).
    
    Args:
        db: Database session
        linkedin_url: LinkedIn URL of profile to delete
        
    Returns:
        True if deleted, False otherwise
    """
    try:
        profile = get_profile_by_linkedin_url(db, linkedin_url)
        
        if not profile:
            logger.warning(f"Profile not found for deletion: {linkedin_url}")
            return False
        
        db.delete(profile)
        db.commit()
        
        logger.info(f"Deleted profile: {profile.id} for URL: {linkedin_url}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting profile: {str(e)}")
        db.rollback()
        return False


def get_all_profiles(db: Session, limit: int = 100) -> list:
    """
    Retrieve all profiles (for admin/analytics purposes).
    
    Args:
        db: Database session
        limit: Maximum number of profiles to return
        
    Returns:
        List of HumanticProfile objects
    """
    try:
        profiles = db.query(HumanticProfile).order_by(
            HumanticProfile.created_at.desc()
        ).limit(limit).all()
        
        logger.info(f"Retrieved {len(profiles)} profiles")
        return profiles
        
    except Exception as e:
        logger.error(f"Error retrieving profiles: {str(e)}")
        return []


def get_stats(db: Session) -> Dict[str, Any]:
    """
    Get database statistics.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with statistics
    """
    try:
        total_profiles = db.query(HumanticProfile).count()
        total_analyses = db.query(GeminiAnalysis).count()
        
        # Get profiles created in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_profiles = db.query(HumanticProfile).filter(
            HumanticProfile.created_at >= week_ago
        ).count()
        
        stats = {
            "total_profiles": total_profiles,
            "total_analyses": total_analyses,
            "recent_profiles_7_days": recent_profiles,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Database stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
