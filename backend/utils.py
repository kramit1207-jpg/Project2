"""
Utility functions for InsightProfile application.
Includes URL validation, sanitization, and normalization.
"""
import re
from urllib.parse import urlparse, urlunparse
from typing import Optional


def sanitize_linkedin_url(url: str) -> str:
    """
    Sanitize and normalize a LinkedIn profile URL.
    
    Handles various LinkedIn URL formats:
    - linkedin.com/in/username
    - www.linkedin.com/in/username
    - https://linkedin.com/in/username
    - https://www.linkedin.com/in/username/
    - https://www.linkedin.com/in/username?param=value
    
    Returns normalized format: linkedin.com/in/username
    
    Args:
        url: LinkedIn profile URL in any format
        
    Returns:
        Sanitized URL in standard format
        
    Raises:
        ValueError: If URL is not a valid LinkedIn profile URL
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Remove whitespace
    url = url.strip()
    
    # Add https:// if no scheme provided
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError(f"Invalid URL format: {url}")
    
    # Validate domain
    domain = parsed.netloc.lower()
    if domain not in ['linkedin.com', 'www.linkedin.com', 'in.linkedin.com']:
        raise ValueError(f"Not a LinkedIn URL: {domain}")
    
    # Extract path
    path = parsed.path.strip('/')
    
    # Validate path format (must be /in/username or in/username)
    if not path:
        raise ValueError("LinkedIn profile URL must include profile identifier")
    
    # Match /in/username pattern
    match = re.match(r'^(?:in/)?([a-zA-Z0-9_-]+)(?:/.*)?$', path)
    if not match:
        raise ValueError(f"Invalid LinkedIn profile path: {path}")
    
    username = match.group(1)
    
    # Return normalized format: linkedin.com/in/username
    return f"linkedin.com/in/{username}"


def validate_linkedin_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a LinkedIn URL and return sanitized version.
    
    Args:
        url: LinkedIn URL to validate
        
    Returns:
        Tuple of (is_valid, sanitized_url or error_message)
    """
    try:
        sanitized = sanitize_linkedin_url(url)
        return True, sanitized
    except ValueError as e:
        return False, str(e)


def extract_linkedin_username(url: str) -> Optional[str]:
    """
    Extract username from LinkedIn URL.
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        Username or None if extraction fails
    """
    try:
        sanitized = sanitize_linkedin_url(url)
        # Extract username from linkedin.com/in/username
        match = re.match(r'^linkedin\.com/in/([a-zA-Z0-9_-]+)$', sanitized)
        if match:
            return match.group(1)
    except ValueError:
        pass
    return None


def are_same_linkedin_profile(url1: str, url2: str) -> bool:
    """
    Check if two LinkedIn URLs refer to the same profile.
    
    Args:
        url1: First LinkedIn URL
        url2: Second LinkedIn URL
        
    Returns:
        True if both URLs refer to the same profile, False otherwise
    """
    try:
        sanitized1 = sanitize_linkedin_url(url1)
        sanitized2 = sanitize_linkedin_url(url2)
        return sanitized1 == sanitized2
    except ValueError:
        return False


def _parse_date(date_str: str) -> Optional[tuple]:
    """
    Parse date string in format "MM-YYYY" or "YYYY-MM" to (year, month).
    Returns None if parsing fails.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        parts = date_str.split("-")
        if len(parts) != 2:
            return None
        
        # Try MM-YYYY format first (most common in Humantic)
        try:
            month = int(parts[0])
            year = int(parts[1])
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                return (year, month)
        except ValueError:
            pass
        
        # Try YYYY-MM format
        try:
            year = int(parts[0])
            month = int(parts[1])
            if 1 <= month <= 12 and 1900 <= year <= 2100:
                return (year, month)
        except ValueError:
            pass
        
        return None
    except Exception:
        return None


def _calculate_total_experience(work_history: list) -> Optional[float]:
    """
    Calculate total years of experience from work history.
    
    Logic:
    1. Find earliest start_date across all roles
    2. Find latest end_date (or use current date if latest role has no end_date)
    3. Calculate difference in years (handling months)
    4. Handle edge cases: missing dates, invalid formats, overlapping roles
    
    Args:
        work_history: List of work history entries with start_date and end_date
        
    Returns:
        Total years of experience as float (rounded to 1 decimal), or None if calculation fails
    """
    from datetime import datetime
    
    if not work_history or not isinstance(work_history, list):
        return None
    
    valid_entries = []
    current_date = datetime.now()
    
    # Parse all valid work history entries
    for entry in work_history:
        if not isinstance(entry, dict):
            continue
        
        start_date = entry.get("start_date", "")
        end_date = entry.get("end_date", "")
        
        start_parsed = _parse_date(start_date)
        if not start_parsed:
            continue
        
        # If no end_date, assume current role (use current date)
        if not end_date:
            end_parsed = (current_date.year, current_date.month)
        else:
            end_parsed = _parse_date(end_date)
            if not end_parsed:
                continue
        
        # Store as (start_year, start_month, end_year, end_month)
        valid_entries.append({
            "start": start_parsed,
            "end": end_parsed
        })
    
    if not valid_entries:
        return None
    
    # Find earliest start and latest end
    earliest_start = min(valid_entries, key=lambda x: (x["start"][0], x["start"][1]))["start"]
    latest_end = max(valid_entries, key=lambda x: (x["end"][0], x["end"][1]))["end"]
    
    # Calculate total months
    start_year, start_month = earliest_start
    end_year, end_month = latest_end
    
    total_months = (end_year - start_year) * 12 + (end_month - start_month)
    
    # Convert to years (with decimal precision)
    total_years = total_months / 12.0
    
    # Round to 1 decimal place
    return round(total_years, 1)


def extract_humantic_insights(profile_data: dict) -> dict:
    """
    Extract and structure key insights from Humantic API response.
    This function organizes the raw Humantic data into a clean structure
    for both LLM consumption and direct API response inclusion.
    
    Args:
        profile_data: Raw Humantic API response
        
    Returns:
        Structured dictionary with categorized insights
    """
    # Guard against None profile_data
    if not profile_data or not isinstance(profile_data, dict):
        profile_data = {}
    
    insights = {
        "identity": {},
        "personality": {},
        "professional": {},
        "communication_intel": {},
        "social_intelligence": {},
        "personas": {}
    }
    
    # Extract identity information
    insights["identity"] = {
        "name": profile_data.get("display_name", ""),
        "first_name": profile_data.get("first_name", ""),
        "last_name": profile_data.get("last_name", ""),
        "location": profile_data.get("location", ""),
        "timezone": profile_data.get("timezone", ""),
        "linkedin": profile_data.get("user_name", ""),
        "headline": profile_data.get("user_description", ""),
        "profile_image": profile_data.get("user_profile_image", "")
    }
    
    # Extract personality data - safe access with None check
    personality_analysis = profile_data.get("personality_analysis") or {}
    if not isinstance(personality_analysis, dict):
        personality_analysis = {}
    
    # OCEAN assessment
    ocean = personality_analysis.get("ocean_assessment") or {}
    if not isinstance(ocean, dict):
        ocean = {}
    insights["personality"]["ocean"] = {}
    ocean_interpretations = {
        "openness": "Receptive to new ideas and innovation, particularly in technical domains",
        "conscientiousness": "Organized, disciplined, and reliable in execution",
        "extraversion": "Energized by interaction, comfortable in leadership visibility",
        "agreeableness": "Can collaborate but maintains high standards, not conflict-averse",
        "emotional_stability": "Resilient under pressure with measured emotional responses"
    }
    for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "emotional_stability"]:
        trait_data = ocean.get(trait) or {}
        if trait_data and isinstance(trait_data, dict):
            score = trait_data.get("score", 5.0)
            insights["personality"]["ocean"][trait] = {
                "score": score,
                "level": trait_data.get("level", ""),
                "percentile": round(score * 10, 1),
                "interpretation": ocean_interpretations.get(trait, "")
            }
    
    # DISC assessment
    disc = personality_analysis.get("disc_assessment") or {}
    if not isinstance(disc, dict):
        disc = {}
    insights["personality"]["disc"] = {}
    disc_interpretations = {
        "dominance": "Assertive, results-focused, comfortable with authority and challenge",
        "influence": "Not relationship-focused, prefers substance over social persuasion",
        "steadiness": "Balanced between consistency and adaptability",
        "calculativeness": "Highly analytical, data-driven, precision-oriented"
    }
    for factor in ["dominance", "influence", "steadiness", "calculativeness"]:
        factor_data = disc.get(factor) or {}
        if factor_data and isinstance(factor_data, dict):
            insights["personality"]["disc"][factor] = {
                "score": factor_data.get("score", 5.0),
                "level": factor_data.get("level", ""),
                "interpretation": disc_interpretations.get(factor, "")
            }
    
    # Summary and archetype - safe access with None check
    summary = personality_analysis.get("summary") or {}
    if not isinstance(summary, dict):
        summary = {}
    disc_summary = summary.get("disc") or {}
    if not isinstance(disc_summary, dict):
        disc_summary = {}
    insights["personality"]["archetype"] = {
        "name": disc_summary.get("archetype", ""),
        "group": disc_summary.get("group", ""),
        "color": disc_summary.get("color", ""),
        "primary_traits": disc_summary.get("description", []),
        "labels": disc_summary.get("label", []),
        "description": f"Combines analytical rigor with decisive action. Perfectionists with bias for action. Hard taskmasters with little tolerance for mistakes." if disc_summary.get("archetype") == "Sharpshooter" else ""
    }
    
    # Extract professional information
    work_history = profile_data.get("work_history", [])
    insights["professional"]["work_history"] = work_history[:3] if work_history else []
    insights["professional"]["education"] = profile_data.get("education", [])
    insights["professional"]["skills"] = profile_data.get("skills", [])
    
    # Calculate experience
    if work_history:
        insights["professional"]["current_role"] = work_history[0] if work_history else {}
    
    # Calculate total years of experience from work history
    total_experience_years = _calculate_total_experience(work_history)
    
    prographics = profile_data.get("prographics") or {}
    if not isinstance(prographics, dict):
        prographics = {}
    insights["professional"]["prographics"] = {
        "job_level": prographics.get("job_level"),
        "education_level": prographics.get("education_level"),
        "experience_in_years": prographics.get("experience_in_years") or total_experience_years,
        "social_activity_status": prographics.get("social_activity_status")
    }
    
    # Add calculated experience to professional insights
    insights["professional"]["total_experience_years"] = total_experience_years
    
    # Extract communication intelligence - safe chained access
    persona = profile_data.get("persona") or {}
    if not isinstance(persona, dict):
        persona = {}
    persona_true = persona.get("true") or {}
    if not isinstance(persona_true, dict):
        persona_true = {}
    
    insights["communication_intel"]["email"] = persona_true.get("email_personalization") or {}
    insights["communication_intel"]["calling"] = persona_true.get("cold_calling_advice") or {}
    insights["communication_intel"]["general"] = persona_true.get("communication_advice") or {}
    
    # Extract social intelligence - safe access
    social_activity = profile_data.get("social_activity") or {}
    if not isinstance(social_activity, dict):
        social_activity = {}
    linkedin_posts = social_activity.get("linkedin") or []
    if not isinstance(linkedin_posts, list):
        linkedin_posts = []
    insights["social_intelligence"]["recent_posts"] = linkedin_posts[:3] if linkedin_posts else []
    
    external_signals = profile_data.get("external_signals") or {}
    if not isinstance(external_signals, dict):
        external_signals = {}
    insights["social_intelligence"]["topics_care_about"] = external_signals.get("topics_they_care_about") or []
    insights["social_intelligence"]["overview"] = external_signals.get("overview") or ""
    
    # Extract demographics - safe access
    demographics = profile_data.get("demographics") or {}
    if not isinstance(demographics, dict):
        demographics = {}
    insights["demographics"] = {
        "age_range": demographics.get("age_range") or {},
        "followers": profile_data.get("followers", 0)
    }
    
    # Extract context-specific personas
    
    if isinstance(persona, dict) and "sales" in persona:
        sales_persona = persona.get("sales") or {}
        if isinstance(sales_persona, dict):
            insights["personas"]["sales"] = {
                "communication_advice": sales_persona.get("communication_advice") or {},
                "email_personalization": sales_persona.get("email_personalization") or {},
                "cold_calling_advice": sales_persona.get("cold_calling_advice") or {},
                "profile_url": sales_persona.get("profile_url") or ""
            }
    
    if isinstance(persona, dict) and "hiring" in persona:
        hiring_persona = persona.get("hiring") or {}
        if isinstance(hiring_persona, dict):
            insights["personas"]["hiring"] = {
                "behavioral_factors": hiring_persona.get("behavioral_factors") or {},
                "communication_advice": hiring_persona.get("communication_advice") or {},
                "email_personalization": hiring_persona.get("email_personalization") or {},
                "profile_url": hiring_persona.get("profile_url") or ""
            }
    
    return insights


def format_insights_for_llm(insights: dict) -> str:
    """
    Format extracted insights into a readable string for LLM prompt.
    
    Args:
        insights: Structured insights from extract_humantic_insights()
        
    Returns:
        Formatted string for LLM consumption
    """
    parts = []
    
    # Identity section
    identity = insights.get("identity", {})
    if identity:
        parts.append(f"## IDENTITY")
        parts.append(f"Name: {identity.get('name', 'N/A')}")
        parts.append(f"Location: {identity.get('location', 'N/A')}")
        parts.append(f"Headline: {identity.get('headline', 'N/A')}")
        parts.append("")
    
    # Personality section
    personality = insights.get("personality", {})
    if personality:
        parts.append("## PERSONALITY ASSESSMENT")
        
        # OCEAN
        ocean = personality.get("ocean", {})
        if ocean:
            parts.append("\n### OCEAN Profile:")
            for trait, data in ocean.items():
                parts.append(f"- {trait.capitalize()}: {data.get('score', 'N/A')} ({data.get('level', 'N/A')})")
        
        # DISC
        disc = personality.get("disc", {})
        if disc:
            parts.append("\n### DISC Assessment:")
            for factor, data in disc.items():
                parts.append(f"- {factor.capitalize()}: {data.get('score', 'N/A')} ({data.get('level', 'N/A')})")
        
        # Archetype
        archetype = personality.get("archetype", {})
        if archetype.get("name"):
            parts.append(f"\n### Archetype: {archetype.get('name', 'N/A')}")
            parts.append(f"Group: {archetype.get('group', 'N/A')}")
            traits = archetype.get("primary_traits", [])
            if traits:
                parts.append(f"Traits: {', '.join(traits)}")
        parts.append("")
    
    # Professional section
    professional = insights.get("professional", {})
    if professional:
        parts.append("## PROFESSIONAL BACKGROUND")
        
        # Current role
        current_role = professional.get("current_role", {})
        if current_role:
            parts.append(f"\nCurrent: {current_role.get('title', 'N/A')} at {current_role.get('organization', 'N/A')}")
        
        # Work history
        work_history = professional.get("work_history", [])
        if work_history:
            parts.append("\nRecent Experience:")
            for job in work_history[:3]:
                parts.append(f"- {job.get('title', 'N/A')} at {job.get('organization', 'N/A')} ({job.get('start_date', 'N/A')} to {job.get('end_date', 'Present')})")
        
        # Education
        education = professional.get("education", [])
        if education:
            parts.append("\nEducation:")
            for edu in education[:3]:
                parts.append(f"- {edu.get('degree', 'N/A')} from {edu.get('school', 'N/A')}")
        
        # Skills
        skills = professional.get("skills", [])
        if skills:
            parts.append(f"\nKey Skills: {', '.join(skills)}")
        parts.append("")
    
    # Social intelligence
    social = insights.get("social_intelligence", {})
    if social:
        topics = social.get("topics_care_about", [])
        if topics:
            parts.append("## CURRENT INTERESTS & FOCUS AREAS")
            for topic in topics:
                label = topic.get("label", "")
                desc = topic.get("description", "")
                if label:
                    parts.append(f"- {label}: {desc}")
            parts.append("")
        
        posts = social.get("recent_posts", [])
        if posts:
            parts.append("## RECENT SOCIAL ACTIVITY")
            for i, post in enumerate(posts[:2], 1):
                post_text = post.get("post_text", "")
                if post_text:
                    # Truncate long posts
                    preview = post_text[:300] + "..." if len(post_text) > 300 else post_text
                    parts.append(f"\nPost {i} Theme: {preview}")
            parts.append("")
    
    # Communication style from Humantic
    comm = insights.get("communication_intel", {})
    if comm:
        general = comm.get("general", {})
        if general:
            adjectives = general.get("adjectives", [])
            what_to_say = general.get("what_to_say", [])
            what_to_avoid = general.get("what_to_avoid", [])
            
            if adjectives or what_to_say or what_to_avoid:
                parts.append("## COMMUNICATION STYLE INDICATORS")
                if adjectives:
                    parts.append(f"Descriptors: {', '.join(adjectives)}")
                if what_to_say:
                    parts.append("\nEffective Approaches:")
                    for item in what_to_say[:3]:
                        parts.append(f"- {item}")
                if what_to_avoid:
                    parts.append("\nApproaches to Avoid:")
                    for item in what_to_avoid[:3]:
                        parts.append(f"- {item}")
                parts.append("")
    
    return "\n".join(parts)