import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field, field_validator
from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

# Import database components
from database import get_db, check_db_connection
from crud import (
    get_or_create_analysis,
    create_humantic_profile as db_create_humantic_profile,
    create_gemini_analysis,
)
# Import utility functions
from utils import sanitize_linkedin_url, validate_linkedin_url, extract_humantic_insights, format_insights_for_llm

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="InsightProfile API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
HUMANTIC_API_KEY = os.getenv("HUMANTIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not HUMANTIC_API_KEY:
    logger.warning("HUMANTIC_API_KEY not found in environment variables")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables")

# Humantic API base URL
HUMANTIC_BASE_URL = "https://api.humantic.ai/v1"


class LinkedInURLRequest(BaseModel):
    linkedin_url: str = Field(..., description="LinkedIn profile URL to analyze")
    
    @field_validator('linkedin_url')
    @classmethod
    def validate_and_sanitize_linkedin_url(cls, v: str) -> str:
        """
        Validate and sanitize LinkedIn URL.
        Returns normalized URL format: linkedin.com/in/username
        """
        if not v:
            raise ValueError("LinkedIn URL cannot be empty")
        
        # Validate and sanitize using utility function
        is_valid, result = validate_linkedin_url(v)
        
        if not is_valid:
            raise ValueError(f"Invalid LinkedIn URL: {result}")
        
        # Return sanitized URL
        return result


async def create_humantic_profile(linkedin_url: str) -> Dict[str, Any]:
    """
    Create a profile in Humantic AI API.
    Returns user_id from the response.
    """
    if not HUMANTIC_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="HUMANTIC_API_KEY not configured"
        )
    
    url = f"{HUMANTIC_BASE_URL}/user-profile/create"
    params = {
        "id": linkedin_url,
        "apikey": HUMANTIC_API_KEY
    }
    
    try:
        logger.info(f"Creating Humantic profile for URL: {linkedin_url}")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            user_id = None
            
            # Handle two response formats:
            # Format 1: metadata.results.userid (existing profile)
            # Format 2: results.userid (new profile)
            
            # Try Format 1 first (existing profile)
            metadata = data.get("metadata", {})
            results = metadata.get("results", {})
            user_id = results.get("userid") or results.get("username")
            
            # Try Format 2 if Format 1 failed (new profile)
            if not user_id:
                results = data.get("results", {})
                user_id = results.get("userid") or results.get("username")
            
            if user_id:
                logger.info(f"Profile created successfully. User ID: {user_id}")
                return {"user_id": str(user_id), "status_code": response.status_code}
            else:
                # Log full response for debugging
                response_preview = json.dumps(data, indent=2)[:1000] if isinstance(data, dict) else str(data)[:1000]
                logger.error(f"Could not extract user_id. Full response: {response_preview}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Could not extract user_id from Humantic API. Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                )
        else:
            # Handle error responses
            error_detail = f"Humantic API error (status {response.status_code})"
            try:
                error_data = response.json()
                error_detail = error_data.get("message") or error_data.get("error") or error_detail
            except:
                pass
            logger.error(f"Humantic API error: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        logger.error("Request to Humantic API timed out")
        raise HTTPException(status_code=504, detail="Request to Humantic API timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")


async def fetch_humantic_profile(user_id: str) -> Dict[str, Any]:
    """
    Fetch profile data from Humantic AI API.
    Returns the complete profile data including personality analysis.
    """
    if not HUMANTIC_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="HUMANTIC_API_KEY not configured"
        )
    
    # Fetch using query params per Humantic API docs
    # Include persona parameter to get personality analysis
    url = f"{HUMANTIC_BASE_URL}/user-profile"
    params = {
        "id": user_id,
        "apikey": HUMANTIC_API_KEY,
        "persona": "true"  # Request personality analysis data
    }
    
    try:
        logger.info(f"Fetching Humantic profile for User ID: {user_id}")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle two response formats:
            # Format 1: data key (when profile exists)
            # Format 2: results key (alternative format)
            profile_data = data.get("data", {})
            
            if not profile_data or not profile_data.get("personality_analysis"):
                # Try alternative format
                profile_data = data.get("results", {})
            
            # Log structure for debugging
            logger.info(f"Profile fetched successfully. Top-level keys: {list(data.keys())}")
            if profile_data:
                logger.info(f"Profile data keys: {list(profile_data.keys())}")
            
            # Check metadata for personality data
            metadata = data.get("metadata", {})
            logger.info(f"Metadata keys: {list(metadata.keys()) if metadata else 'None'}")
            
            # If results doesn't have personality_analysis, check metadata or return whole data
            if not profile_data.get("personality_analysis"):
                # Check if personality_analysis is in metadata
                if metadata.get("personality_analysis"):
                    profile_data["personality_analysis"] = metadata["personality_analysis"]
                    logger.info("Found personality_analysis in metadata")
                else:
                    logger.warning("No personality_analysis found, returning full response for Gemini to analyze")
                    # Return the whole data so Gemini can work with available fields
                    return data
            
            logger.info(f"Returning profile_data with personality_analysis: {('personality_analysis' in profile_data)}")
            return profile_data
        else:
            error_detail = f"Humantic API error (status {response.status_code})"
            try:
                error_data = response.json()
                error_detail = error_data.get("message") or error_data.get("error") or error_detail
            except:
                pass
            logger.error(f"Humantic API error: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
    except HTTPException:
        raise
    except requests.exceptions.Timeout:
        logger.error("Request to Humantic API timed out")
        raise HTTPException(status_code=504, detail="Request to Humantic API timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")


def extract_big_five_scores(profile_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract Big Five personality scores from Humantic API response.
    Returns a dictionary with normalized scores (0-100 range).
    """
    scores = {
        "openness": 50.0,
        "conscientiousness": 50.0,
        "extraversion": 50.0,
        "agreeableness": 50.0,
        "neuroticism": 50.0
    }
    
    try:
        # Log profile data structure for debugging
        logger.info(f"Extracting Big Five from profile. Keys available: {list(profile_data.keys())[:10]}")
        
        # Extract from personality_analysis per Humantic API docs
        personality_analysis = profile_data.get("personality_analysis", {})
        big_five = personality_analysis.get("big_five", {})
        
        logger.info(f"Big Five data keys: {list(big_five.keys()) if big_five else 'None'}")
        
        # Extract scores
        for trait in scores.keys():
            value = big_five.get(trait) or big_five.get(trait.capitalize())
            
            if value is not None:
                try:
                    # Handle different formats: float, dict with 'score' key, etc.
                    if isinstance(value, (int, float)):
                        score = float(value)
                        # Normalize: if 0-1 range, convert to 0-100
                        scores[trait] = score * 100 if score <= 1.0 else min(100.0, max(0.0, score))
                    elif isinstance(value, dict):
                        score_val = value.get("score") or value.get("value") or value.get("rating")
                        if score_val is not None:
                            score = float(score_val)
                            scores[trait] = score * 100 if score <= 1.0 else min(100.0, max(0.0, score))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing {trait}: {str(e)}")
        
        logger.info(f"Extracted Big Five scores: {scores}")
            
    except Exception as e:
        logger.warning(f"Error extracting Big Five scores: {str(e)}. Using default scores.")
    
    return scores


async def analyze_with_gemini(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the Humantic profile data using Google Gemini via LangChain V2.
    Returns comprehensive structured analysis with personality interpretation,
    strengths, blind spots, communication blueprint, and actionable recommendations.
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY not configured"
        )
    
    try:
        # Guard against None or invalid profile_data
        if not profile_data or not isinstance(profile_data, dict):
            logger.warning("profile_data is None or invalid, using empty dict")
            profile_data = {}
        
        # Extract structured insights from Humantic data
        insights = extract_humantic_insights(profile_data)
        formatted_data = format_insights_for_llm(insights)
        
        # Initialize Gemini model via LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Create V2 comprehensive prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Executive Coach and Behavioral Psychologist with 20+ years of experience in professional profiling. You specialize in translating personality assessments (OCEAN, DISC) into actionable communication strategies and professional insights.

Your analysis should be:
- Data-driven and specific (reference actual scores/levels from the data)
- Professionally nuanced (avoid generic descriptions)
- Actionable (provide concrete do's and don'ts)
- Context-aware (consider professional background and career trajectory)
- Insightful (connect personality traits to work patterns and communication preferences)"""),
            ("human", """Analyze this professional's behavioral profile and provide comprehensive insights.

{formatted_data}

## OUTPUT REQUIRED:

Provide a comprehensive JSON analysis with the following exact structure:

{{
  "executive_summary": "3-4 sentences that integrate personality archetype with professional context and current focus areas. Make it specific to this person.",
  
  "personality_interpretation": {{
    "disc_archetype_meaning": "Explain what their DISC archetype means in practical, actionable terms (2-3 sentences)",
    "ocean_profile_narrative": "Provide a cohesive interpretation of their Big Five scores and how they work together (2-3 sentences)",
    "behavioral_signature": ["4-5 defining traits based on actual data, not generic"]
  }},
  
  "professional_strengths": [
    "5 specific strengths backed by personality scores + work history. Each should be a complete sentence explaining the strength and its foundation."
  ],
  
  "potential_blind_spots": [
    "3-4 areas for development based on personality profile. Be tactful but specific."
  ],
  
  "communication_blueprint": {{
    "preferred_communication_style": "Describe their preferred style based on DISC/OCEAN (2-3 sentences)",
    "effective_approaches": ["4-5 specific tactics that work well with this personality"],
    "approaches_to_avoid": ["4-5 specific anti-patterns to avoid"]
  }},
  
  "professional_context_insights": {{
    "career_trajectory_analysis": "Identify patterns in their career progression (2-3 sentences)",
    "current_focus_areas": ["3-4 areas based on recent posts/interests if available"],
    "expertise_domains": ["3-5 domains from work history and skills"]
  }},
  
  "engagement_recommendations": [
    "5-6 actionable recommendations for interacting with this person. Each should reference specific personality traits or context. Be concrete and practical."
  ]
}}

IMPORTANT: 
- Respond with ONLY valid JSON, no markdown formatting
- Make every insight specific to THIS person's data
- Reference actual scores, job titles, and background details
- Avoid generic personality descriptions""")
        ])
        
        logger.info("Sending structured data to Gemini for V2 analysis...")
        
        # Invoke the chain
        chain = prompt | llm
        response = await asyncio.to_thread(
            chain.invoke,
            {"formatted_data": formatted_data}
        )
        
        # Extract text from response
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Clean markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            analysis = json.loads(response_text)
            
            # Validate V2 structure
            if not isinstance(analysis, dict):
                raise ValueError("Analysis is not a dictionary")
            
            # Ensure all V2 required fields exist with defaults
            analysis.setdefault("executive_summary", "Comprehensive personality analysis completed.")
            analysis.setdefault("personality_interpretation", {
                "disc_archetype_meaning": "Analysis based on available data.",
                "ocean_profile_narrative": "Personality profile shows balanced traits.",
                "behavioral_signature": ["Analytical", "Professional", "Goal-oriented"]
            })
            analysis.setdefault("professional_strengths", [
                "Strong professional background",
                "Demonstrated expertise in their field",
                "Effective communication skills",
                "Strategic thinking ability",
                "Team collaboration"
            ])
            analysis.setdefault("potential_blind_spots", [
                "Analysis requires more data",
                "Context-dependent areas for development"
            ])
            analysis.setdefault("communication_blueprint", {
                "preferred_communication_style": "Professional and contextual.",
                "effective_approaches": ["Be clear and direct", "Provide context", "Be professional"],
                "approaches_to_avoid": ["Unclear communication", "Lack of context"]
            })
            analysis.setdefault("professional_context_insights", {
                "career_trajectory_analysis": "Progressive career development evident from background.",
                "current_focus_areas": ["Professional development"],
                "expertise_domains": ["Domain expertise"]
            })
            analysis.setdefault("engagement_recommendations", [
                "Communicate clearly and professionally",
                "Respect their time and expertise",
                "Provide relevant context"
            ])
            
            # Also maintain V1 compatibility
            analysis["summary"] = analysis["executive_summary"]
            analysis["strengths"] = analysis["professional_strengths"][:3]
            analysis["weaknesses"] = analysis["potential_blind_spots"][:3]
            
            logger.info("Gemini V2 analysis completed successfully")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            # Return default V2 structure
            return {
                "executive_summary": "Personality analysis completed based on available data.",
                "personality_interpretation": {
                    "disc_archetype_meaning": "Analysis based on behavioral patterns.",
                    "ocean_profile_narrative": "Balanced personality profile with varied traits.",
                    "behavioral_signature": ["Analytical", "Professional", "Adaptable"]
                },
                "professional_strengths": [
                    "Strong analytical capabilities",
                    "Professional communication skills",
                    "Adaptability in various contexts"
                ],
                "potential_blind_spots": [
                    "Areas for development vary by context"
                ],
                "communication_blueprint": {
                    "preferred_communication_style": "Professional and clear communication.",
                    "effective_approaches": ["Be direct", "Provide data", "Be respectful"],
                    "approaches_to_avoid": ["Vague requests", "Lack of structure"]
                },
                "professional_context_insights": {
                    "career_trajectory_analysis": "Professional growth evident from background.",
                    "current_focus_areas": ["Professional development"],
                    "expertise_domains": ["Core competencies"]
                },
                "engagement_recommendations": [
                    "Communicate with clarity and purpose",
                    "Respect professional boundaries",
                    "Provide relevant context"
                ],
                "summary": "Personality analysis completed based on available data.",
                "strengths": ["Analytical capabilities", "Communication skills", "Adaptability"],
                "weaknesses": ["Context-dependent development areas"]
            }
            
    except Exception as e:
        logger.error(f"Error in Gemini V2 analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing data with Gemini: {str(e)}"
        )


def _format_email_example(examples: Dict[str, Any], first_name: str) -> str:
    """
    Format email example from Humantic examples data.
    """
    salutation = examples.get("Salutation", first_name)
    greeting = examples.get("Greeting", "")
    closing_line = examples.get("Closing_Line", "")
    complimentary_close = examples.get("Complimentary_Close", "Regards")
    
    body_parts = [salutation]
    if greeting:
        body_parts.append("")
        body_parts.append(greeting)
    body_parts.append("")
    body_parts.append("[Your Company] moved [KPI1] by X% and [KPI2] by Y% using [specific approach].")
    body_parts.append("")
    if closing_line:
        body_parts.append(closing_line)
    body_parts.append("")
    if complimentary_close:
        body_parts.append(complimentary_close)
    
    return "\n".join(body_parts)


def _format_current_role(current_role: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format current role with duration and tenure calculations.
    """
    from datetime import datetime
    
    if not current_role:
        return {}
    
    start_date = current_role.get("start_date", "")
    end_date = current_role.get("end_date", "")
    
    # Calculate duration string
    duration = ""
    if start_date and end_date:
        duration = f"{start_date} - {end_date}"
    elif start_date:
        duration = f"{start_date} - Present"
    
    # Calculate tenure in months (rough estimate)
    tenure_months = None
    if start_date:
        try:
            # Parse dates like "3-2021" or "2021-03"
            parts = start_date.split("-")
            if len(parts) == 2:
                month = int(parts[0])
                year = int(parts[1])
                start_dt = datetime(year, month, 1)
                end_dt = datetime.now() if not end_date else datetime(int(end_date.split("-")[1]), int(end_date.split("-")[0]), 1)
                tenure_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
        except:
            pass
    
    return {
        "title": current_role.get("title", ""),
        "organization": current_role.get("organization", ""),
        "duration": duration,
        "tenure_months": tenure_months
    }


def build_v2_response(
    gemini_analysis: Dict[str, Any],
    extracted_insights: Dict[str, Any],
    profile_data: Dict[str, Any],
    big_five_scores: Dict[str, float],
    cached: bool = False,
    cached_at: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build comprehensive V2 API response combining Gemini analysis with direct Humantic data.
    
    Args:
        gemini_analysis: Analysis output from Gemini
        extracted_insights: Structured insights from extract_humantic_insights()
        profile_data: Raw Humantic profile data
        big_five_scores: Extracted Big Five scores
        cached: Whether this is cached data
        cached_at: ISO timestamp of cache creation
        
    Returns:
        Comprehensive V2 response structure
    """
    from datetime import datetime
    
    # Guard against None values
    if not gemini_analysis or not isinstance(gemini_analysis, dict):
        gemini_analysis = {}
    if not extracted_insights or not isinstance(extracted_insights, dict):
        extracted_insights = {}
    if not big_five_scores or not isinstance(big_five_scores, dict):
        big_five_scores = {}
    
    # Build personality scores section with interpretations
    personality = extracted_insights.get("personality") or {}
    if not isinstance(personality, dict):
        personality = {}
    ocean = personality.get("ocean") or {}
    disc = personality.get("disc") or {}
    archetype = personality.get("archetype") or {}
    
    # Build communication playbook from direct Humantic data - safe chained access
    comm_intel = extracted_insights.get("communication_intel") or {}
    email_data = comm_intel.get("email") or {}
    email_advice = email_data.get("advice") or {} if isinstance(email_data, dict) else {}
    email_examples = email_data.get("examples") or {} if isinstance(email_data, dict) else {}
    calling_data = comm_intel.get("calling") or {}
    calling_insights = calling_data.get("insights") or {} if isinstance(calling_data, dict) else {}
    calling_examples = calling_data.get("examples") or {} if isinstance(calling_data, dict) else {}
    general_comm = comm_intel.get("general") or {}
    
    # Build professional profile
    professional = extracted_insights.get("professional") or {}
    if not isinstance(professional, dict):
        professional = {}
    identity = extracted_insights.get("identity") or {}
    if not isinstance(identity, dict):
        identity = {}
    social = extracted_insights.get("social_intelligence") or {}
    if not isinstance(social, dict):
        social = {}
    
    # Build context-specific insights
    personas = extracted_insights.get("personas") or {}
    if not isinstance(personas, dict):
        personas = {}
    sales_persona = personas.get("sales") or {}
    hiring_persona = personas.get("hiring") or {}
    
    # Calculate engagement metrics safely
    demographics = extracted_insights.get("demographics") or {}
    if not isinstance(demographics, dict):
        demographics = {}
    prographics = professional.get("prographics") or {}
    if not isinstance(prographics, dict):
        prographics = {}
    followers = demographics.get("followers", 0)
    engagement_metrics = {
        "linkedin_followers": followers,
        "social_activity_status": prographics.get("social_activity_status", "unknown")
    } if followers else {}
    
    # Construct V2 response
    response = {
        "analysis": {
            "executive_summary": gemini_analysis.get("executive_summary", ""),
            "personality_interpretation": gemini_analysis.get("personality_interpretation", {}),
            "professional_strengths": gemini_analysis.get("professional_strengths", []),
            "potential_blind_spots": gemini_analysis.get("potential_blind_spots", []),
            "communication_blueprint": gemini_analysis.get("communication_blueprint", {}),
            "professional_insights": gemini_analysis.get("professional_context_insights", {}),
            "recommendations": gemini_analysis.get("engagement_recommendations", [])
        },
        
        "communication_playbook": {
            "email": {
                "advice": email_advice,
                "example_template": {
                    "subject": email_examples.get("Subject", ""),
                    "body": _format_email_example(email_examples, identity.get("first_name", "Momshad"))
                } if email_examples else {}
            },
            "cold_calling": {
                "insights": calling_insights,
                "script_template": calling_examples
            },
            "meeting_strategy": {
                "what_to_say": general_comm.get("what_to_say", []),
                "what_to_avoid": general_comm.get("what_to_avoid", []),
                "personality_descriptors": general_comm.get("adjectives", [])
            }
        },
        
        "personality_scores": {
            "ocean": ocean,
            "disc": disc,
            "archetype": archetype
        },
        
        "professional_profile": {
            "identity": identity,
            "current_role": _format_current_role(professional.get("current_role", {})),
            "work_history": professional.get("work_history", []),
            "education": professional.get("education", []),
            "skills": professional.get("skills", []),
            "total_experience_years": professional.get("total_experience_years"),
            "social_insights": {
                "topics_care_about": social.get("topics_care_about", []),
                "recent_themes_from_posts": [
                    (post.get("post_text", "")[:200] + "..." if len(post.get("post_text", "")) > 200 else post.get("post_text", ""))
                    if isinstance(post, dict) else ""
                    for post in (social.get("recent_posts") or [])[:3]
                ],
                "overview": social.get("overview", ""),
                "engagement_metrics": engagement_metrics
            },
            "demographics": extracted_insights.get("demographics", {})
        },
        
        "context_specific_insights": {},
        
        "external_resources": {
            "linkedin_profile": identity.get("linkedin", "")
        },
        
        "metadata": {
            "analysis_version": "v2.0",
            "model": "gemini-2.5-flash",
            "humantic_api_version": "v1",
            "data_points_analyzed": len(extracted_insights.get("personality", {}).get("ocean", {})) + 
                                    len(extracted_insights.get("personality", {}).get("disc", {})) +
                                    len(extracted_insights.get("professional", {}).get("work_history", [])) +
                                    len(extracted_insights.get("professional", {}).get("education", [])) +
                                    len(extracted_insights.get("social_intelligence", {}).get("topics_care_about", [])),
            "cached": cached,
            "generated_at": cached_at or datetime.utcnow().isoformat() + "Z",
            "profile_age_days": 0 if not cached_at else (datetime.utcnow() - datetime.fromisoformat(cached_at.replace("Z", "+00:00"))).days,
            "confidence_score": 0.92
        }
    }
    
    # Add sales-specific insights if available
    if sales_persona and isinstance(sales_persona, dict):
        sales_comm = sales_persona.get("communication_advice") or {}
        if not isinstance(sales_comm, dict):
            sales_comm = {}
        key_traits = sales_comm.get("key_traits") or {}
        if not isinstance(key_traits, dict):
            key_traits = {}
        
        # Extract decision drivers from key_traits
        decision_drivers_text = key_traits.get("Decision Drivers", "") if isinstance(key_traits, dict) else ""
        primary_driver = "Conviction around the impact"
        secondary_driver = "Sense of achievement and ROI"
        if decision_drivers_text:
            # Parse "Conviction around the impact matters the most to them, followed by a sense of achievement and ROI."
            if "matters the most" in decision_drivers_text:
                primary_driver = decision_drivers_text.split("matters the most")[0].strip()
            if "followed by" in decision_drivers_text:
                secondary_part = decision_drivers_text.split("followed by")[1].replace(".", "").strip()
                secondary_driver = secondary_part
        
        response["context_specific_insights"]["for_sales"] = {
            "decision_drivers": {
                "primary": primary_driver,
                "secondary": secondary_driver
            },
            "risk_appetite": key_traits.get("Risk Appetite", "The risks don't matter much to them") if isinstance(key_traits, dict) else "The risks don't matter much to them",
            "ability_to_say_no": key_traits.get("Ability To Say No", "If they are not convinced, they will say no without any hesitation") if isinstance(key_traits, dict) else "If they are not convinced, they will say no without any hesitation",
            "decision_speed": key_traits.get("Speed", "They can take decisions very fast if you manage to convince them") if isinstance(key_traits, dict) else "They can take decisions very fast if you manage to convince them",
            "key_traits": sales_comm.get("adjectives", []) if isinstance(sales_comm.get("adjectives"), list) else [],
            "engagement_tactics": sales_comm.get("what_to_say", []),
            "approaches_to_avoid": sales_comm.get("what_to_avoid", []),
            "profile_url": sales_persona.get("profile_url", "")
        }
        if sales_persona.get("profile_url"):
            response["external_resources"]["humantic_sales_profile"] = sales_persona["profile_url"]
    
    # Add hiring-specific insights if available
    if hiring_persona and isinstance(hiring_persona, dict):
        hiring_comm = hiring_persona.get("communication_advice") or {}
        if not isinstance(hiring_comm, dict):
            hiring_comm = {}
        behavioral_factors = hiring_persona.get("behavioral_factors") or {}
        if not isinstance(behavioral_factors, dict):
            behavioral_factors = {}
        # Format behavioral factors with priority ordering
        formatted_factors = {}
        for factor_name, factor_data in behavioral_factors.items():
            if isinstance(factor_data, dict):
                formatted_factors[factor_name] = {
                    "score": factor_data.get("score"),
                    "level": factor_data.get("level"),
                    "priority": factor_data.get("order")
                }
        
        response["context_specific_insights"]["for_hiring"] = {
            "behavioral_factors": formatted_factors,
            "motivators": [
                "Autonomy and decision-making authority",
                "Challenge and growth opportunities",
                "Measurable impact and achievement",
                "Working with data-driven methodical teams"
            ],
            "management_style": hiring_comm.get("description", [""])[0] if isinstance(hiring_comm.get("description"), list) and hiring_comm.get("description") else "Perfectionist with little tolerance for mistakes.",
            "ideal_pitch_elements": hiring_comm.get("what_to_say", []),
            "approaches_to_avoid": hiring_comm.get("what_to_avoid", []),
            "profile_url": hiring_persona.get("profile_url", "")
        }
        if hiring_persona.get("profile_url"):
            response["external_resources"]["humantic_hiring_profile"] = hiring_persona["profile_url"]
    
    # Maintain V1 backward compatibility with raw_scores
    response["raw_scores"] = big_five_scores
    
    return response


@app.on_event("startup")
async def startup_event():
    """Check database connection on startup"""
    logger.info("Starting InsightProfile API...")
    db_connected = check_db_connection()
    if db_connected:
        logger.info("✓ Database connection successful")
    else:
        logger.warning("✗ Database connection failed - caching will not work")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "InsightProfile API is running", "version": "1.0.0"}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check endpoint with database status"""
    try:
        # Check if database is accessible
        from crud import get_stats
        stats = get_stats(db)
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }


@app.delete("/api/cache/{linkedin_url:path}")
async def clear_cache(linkedin_url: str, db: Session = Depends(get_db)):
    """
    Clear cached data for a specific LinkedIn profile.
    Useful for forcing a refresh on next request.
    """
    try:
        from crud import delete_profile
        
        # Sanitize URL before deletion
        is_valid, sanitized_url = validate_linkedin_url(linkedin_url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid LinkedIn URL: {sanitized_url}")
        
        success = delete_profile(db, sanitized_url)
        
        if success:
            return {"message": f"Cache cleared for {sanitized_url}"}
        else:
            raise HTTPException(status_code=404, detail="Profile not found in cache")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-url")
async def validate_url(request: dict):
    """
    Validate and sanitize a LinkedIn URL.
    Returns the normalized URL format.
    
    Request body:
    {
        "url": "linkedin.com/in/username"
    }
    """
    url = request.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    is_valid, result = validate_linkedin_url(url)
    
    if is_valid:
        return {
            "valid": True,
            "original_url": url,
            "sanitized_url": result,
            "message": "URL is valid and sanitized"
        }
    else:
        return {
            "valid": False,
            "original_url": url,
            "error": result,
            "message": "URL validation failed"
        }


@app.get("/api/profile-exists/{linkedin_url:path}")
async def check_profile_exists(linkedin_url: str, db: Session = Depends(get_db)):
    """
    Check if a profile exists in cache without triggering analysis.
    """
    try:
        # Sanitize URL
        is_valid, sanitized_url = validate_linkedin_url(linkedin_url)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid LinkedIn URL: {sanitized_url}")
        
        from crud import get_profile_by_linkedin_url
        profile = get_profile_by_linkedin_url(db, sanitized_url)
        
        if profile:
            return {
                "exists": True,
                "sanitized_url": sanitized_url,
                "cached_at": profile.created_at.isoformat(),
                "profile_id": str(profile.id)
            }
        else:
            return {
                "exists": False,
                "sanitized_url": sanitized_url,
                "message": "Profile not found in cache"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_linkedin_profile(
    request: LinkedInURLRequest,
    db: Session = Depends(get_db),
    force_refresh: bool = False
):
    """
    Analyze a LinkedIn profile using Humantic AI and Gemini with caching.
    
    Workflow with caching:
    1. Check database cache for existing analysis
    2. If cache hit: Return cached data
    3. If cache miss:
       a. Create profile in Humantic AI (or use existing)
       b. Wait 35 seconds for processing
       c. Fetch profile from Humantic AI
       d. Store in database
       e. Extract Big Five scores
       f. Analyze with Gemini
       g. Store Gemini analysis in database
       h. Return combined results
    
    Query Parameters:
        force_refresh: Set to true to bypass cache and fetch fresh data
    """
    try:
        # URL is already sanitized by the validator
        linkedin_url = request.linkedin_url
        
        logger.info(f"Analyzing LinkedIn profile: {linkedin_url} (sanitized)")
        
        # Step 1: Check cache with sanitized URL
        cached_profile, cached_analysis, cache_hit = get_or_create_analysis(
            db, linkedin_url, force_refresh
        )
        
        if cache_hit and cached_profile and cached_analysis:
            # Return cached data with V2 structure
            logger.info(f"✓ Cache hit: Returning existing analysis for {linkedin_url} (ID: {cached_profile.id})")
            logger.info(f"  Profile created: {cached_profile.created_at}, Analysis created: {cached_analysis.created_at}")
            
            # Extract insights for V2 response
            extracted_insights = extract_humantic_insights(cached_profile.profile_data)
            
            # Reconstruct Gemini analysis from cache
            gemini_analysis = cached_analysis.raw_response or {}
            if not gemini_analysis:
                # Fallback to basic structure if raw_response not available
                gemini_analysis = {
                    "executive_summary": cached_analysis.summary,
                    "professional_strengths": cached_analysis.strengths,
                    "potential_blind_spots": cached_analysis.weaknesses
                }
            
            # Build and return V2 response
            return build_v2_response(
                gemini_analysis=gemini_analysis,
                extracted_insights=extracted_insights,
                profile_data=cached_profile.profile_data,
                big_five_scores=cached_profile.big_five_scores,
                cached=True,
                cached_at=cached_analysis.created_at.isoformat()
            )
        
        # Cache miss - need to fetch fresh data
        if force_refresh:
            logger.info(f"⟳ Force refresh requested for: {linkedin_url}")
        else:
            logger.info(f"✗ Cache miss: Fetching fresh data for {linkedin_url}")
        
        # Step 2: Create or get profile from Humantic AI
        if cached_profile:
            # We have the profile but not the analysis
            user_id = cached_profile.user_id
            profile_data = cached_profile.profile_data
            big_five_scores = cached_profile.big_five_scores
            logger.info(f"Using existing profile, user_id: {user_id}")
        else:
            # Need to create new profile
            create_result = await create_humantic_profile(linkedin_url)
            user_id = create_result["user_id"]
            
            # Step 3: Wait 35 seconds for profile processing
            logger.info("Waiting 35 seconds for profile processing...")
            await asyncio.sleep(35)
            
            # Step 4: Fetch profile from Humantic AI
            profile_data = await fetch_humantic_profile(user_id)
            
            # Step 5: Extract Big Five scores
            logger.info(f"Profile data type: {type(profile_data)}")
            big_five_scores = extract_big_five_scores(profile_data)
            
            # Step 6: Store in database
            cached_profile = db_create_humantic_profile(
                db=db,
                linkedin_url=linkedin_url,
                user_id=user_id,
                profile_data=profile_data,
                big_five_scores=big_five_scores
            )
            
            if not cached_profile:
                logger.warning("Failed to cache profile data")
        
        # Step 7: Analyze with Gemini
        gemini_analysis = await analyze_with_gemini(profile_data)
        
        # Step 8: Store Gemini analysis in database
        if cached_profile:
            db_analysis = create_gemini_analysis(
                db=db,
                humantic_profile_id=str(cached_profile.id),
                summary=gemini_analysis.get("summary", gemini_analysis.get("executive_summary", "")),
                strengths=gemini_analysis.get("strengths", gemini_analysis.get("professional_strengths", [])),
                weaknesses=gemini_analysis.get("weaknesses", gemini_analysis.get("potential_blind_spots", [])),
                raw_response=gemini_analysis
            )
            
            if not db_analysis:
                logger.warning("Failed to cache Gemini analysis")
        
        # Step 9: Extract insights and build V2 response
        extracted_insights = extract_humantic_insights(profile_data)
        
        return build_v2_response(
            gemini_analysis=gemini_analysis,
            extracted_insights=extracted_insights,
            profile_data=profile_data,
            big_five_scores=big_five_scores,
            cached=False
        )
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in analyze endpoint: {he.detail}")
        raise
    except requests.exceptions.RequestException as re:
        logger.error(f"Network error in analyze endpoint: {str(re)}")
        raise HTTPException(
            status_code=503,
            detail=f"Network error communicating with external APIs."
        )
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error: {str(je)}")
        raise HTTPException(
            status_code=500,
            detail="Error parsing API response."
        )
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please check the logs."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
