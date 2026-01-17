import os
import asyncio
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field, field_validator
import google.generativeai as genai
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

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
    allow_origins=["http://localhost:3000"],
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
    def validate_linkedin_url(cls, v: str) -> str:
        """Validate LinkedIn URL format"""
        if not v:
            raise ValueError("LinkedIn URL cannot be empty")
        if not ("linkedin.com" in v.lower() or v.startswith("http")):
            raise ValueError("Invalid LinkedIn URL format")
        return v


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
    
    url = f"{HUMANTIC_BASE_URL}/create-profile"
    headers = {
        "hm-api-key": HUMANTIC_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "linkedin_url": linkedin_url
    }
    
    try:
        logger.info(f"Creating Humantic profile for URL: {linkedin_url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "user_id" in data["data"]:
                user_id = data["data"]["user_id"]
                logger.info(f"Profile created successfully. User ID: {user_id}")
                return {"user_id": user_id, "status_code": response.status_code}
            else:
                logger.error(f"Unexpected response format: {data}")
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from Humantic API"
                )
        elif response.status_code in range(20, 41):
            error_detail = f"Humantic API error (code {response.status_code})"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_detail = error_data["message"]
            except:
                pass
            logger.error(f"Humantic API error: {error_detail}")
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            error_detail = f"Failed to create profile. Status: {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_detail = error_data["message"]
            except:
                pass
            logger.error(error_detail)
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
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
    
    url = f"{HUMANTIC_BASE_URL}/fetch-profile"
    headers = {
        "hm-api-key": HUMANTIC_API_KEY
    }
    params = {
        "user_id": user_id
    }
    
    try:
        logger.info(f"Fetching Humantic profile for User ID: {user_id}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Profile fetched successfully")
            return data
        elif response.status_code in range(20, 41):
            error_detail = f"Humantic API error (code {response.status_code})"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_detail = error_data["message"]
            except:
                pass
            logger.error(f"Humantic API error: {error_detail}")
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            error_detail = f"Failed to fetch profile. Status: {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_detail = error_data["message"]
            except:
                pass
            logger.error(error_detail)
            raise HTTPException(status_code=response.status_code, detail=error_detail)
            
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
        "openness": 0.0,
        "conscientiousness": 0.0,
        "extraversion": 0.0,
        "agreeableness": 0.0,
        "neuroticism": 0.0
    }
    
    try:
        # Navigate through the response structure to find personality analysis
        data = profile_data.get("data", {})
        personality = data.get("personality_analysis", {})
        
        # Big Five scores might be in different locations
        big_five = personality.get("big_five", {})
        
        if big_five:
            # Extract and normalize scores (assuming 0-1 range, convert to 0-100)
            scores["openness"] = float(big_five.get("openness", 0)) * 100
            scores["conscientiousness"] = float(big_five.get("conscientiousness", 0)) * 100
            scores["extraversion"] = float(big_five.get("extraversion", 0)) * 100
            scores["agreeableness"] = float(big_five.get("agreeableness", 0)) * 100
            scores["neuroticism"] = float(big_five.get("neuroticism", 0)) * 100
        else:
            # Alternative: try to extract from different structure
            for key in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
                if key in personality:
                    val = personality[key]
                    if isinstance(val, (int, float)):
                        scores[key] = float(val) * 100 if val <= 1.0 else float(val)
                    elif isinstance(val, dict) and "score" in val:
                        scores[key] = float(val["score"]) * 100 if val["score"] <= 1.0 else float(val["score"])
        
        # Ensure all scores are between 0 and 100
        for key in scores:
            scores[key] = max(0.0, min(100.0, scores[key]))
            
    except Exception as e:
        logger.warning(f"Error extracting Big Five scores: {str(e)}. Using default scores.")
        # If extraction fails, use neutral scores
        scores = {k: 50.0 for k in scores}
    
    return scores


async def analyze_with_gemini(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the Humantic profile data using Google Gemini via LangChain.
    Returns structured analysis with strengths, weaknesses, and summary.
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_API_KEY not configured"
        )
    
    try:
        # Configure Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')
        
        # Create the prompt
        system_prompt_text = "You are an expert Psychologist. Analyze the provided behavioral JSON data. Output a structured JSON response containing: 3 key Strengths, 3 key Weaknesses, and a brief 2-sentence summary of the personality."
        
        human_prompt_text = """Analyze the following personality and behavioral data:
        
{profile_data}

Provide your analysis in the following JSON format:
{{
    "summary": "A brief 2-sentence summary of the personality",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"]
}}

Respond with ONLY valid JSON, no additional text or markdown formatting."""
        
        # Format the profile data as a readable string
        profile_json_str = json.dumps(profile_data, indent=2)
        
        # Combine prompts
        full_prompt = f"{system_prompt_text}\n\n{human_prompt_text}".format(profile_data=profile_json_str)
        
        logger.info("Sending data to Gemini for analysis...")
        # Use generate content (synchronous, but run in executor to avoid blocking)
        response = await asyncio.to_thread(
            model.generate_content,
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7)
        )
        
        # Extract content from response
        response_text = response.text if hasattr(response, 'text') else str(response)
        
        # Try to parse JSON from response
        # Remove markdown code blocks if present
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
            
            # Validate structure
            if not isinstance(analysis, dict):
                raise ValueError("Analysis is not a dictionary")
            
            # Ensure required fields exist
            if "summary" not in analysis:
                analysis["summary"] = "Personality analysis completed."
            if "strengths" not in analysis:
                analysis["strengths"] = ["Analysis pending", "Analysis pending", "Analysis pending"]
            if "weaknesses" not in analysis:
                analysis["weaknesses"] = ["Analysis pending", "Analysis pending", "Analysis pending"]
            
            # Ensure arrays have exactly 3 items
            if len(analysis["strengths"]) < 3:
                analysis["strengths"].extend(["Analysis pending"] * (3 - len(analysis["strengths"])))
            analysis["strengths"] = analysis["strengths"][:3]
            
            if len(analysis["weaknesses"]) < 3:
                analysis["weaknesses"].extend(["Analysis pending"] * (3 - len(analysis["weaknesses"])))
            analysis["weaknesses"] = analysis["weaknesses"][:3]
            
            logger.info("Gemini analysis completed successfully")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text}")
            # Return default analysis if JSON parsing fails
            return {
                "summary": "Personality analysis completed. The individual shows a balanced behavioral profile based on the provided data.",
                "strengths": ["Analytical thinking", "Adaptability", "Communication skills"],
                "weaknesses": ["Analysis pending", "Analysis pending", "Analysis pending"]
            }
            
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing data with Gemini: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "InsightProfile API is running", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_linkedin_profile(request: LinkedInURLRequest = Body(...)):
    """
    Analyze a LinkedIn profile using Humantic AI and Gemini.
    
    Workflow:
    1. Create profile in Humantic AI
    2. Wait 35 seconds for processing
    3. Fetch profile from Humantic AI
    4. Analyze with Gemini
    5. Return combined results
    """
    try:
        linkedin_url = request.linkedin_url
        
        # Step 1: Create profile in Humantic AI
        create_result = await create_humantic_profile(linkedin_url)
        user_id = create_result["user_id"]
        
        # Step 2: Wait 35 seconds for profile processing
        logger.info("Waiting 35 seconds for profile processing...")
        await asyncio.sleep(35)
        
        # Step 3: Fetch profile from Humantic AI
        profile_data = await fetch_humantic_profile(user_id)
        
        # Step 4: Extract Big Five scores
        big_five_scores = extract_big_five_scores(profile_data)
        
        # Step 5: Analyze with Gemini
        gemini_analysis = await analyze_with_gemini(profile_data)
        
        # Step 6: Return combined response
        return {
            "analysis": {
                "summary": gemini_analysis.get("summary", ""),
                "strengths": gemini_analysis.get("strengths", []),
                "weaknesses": gemini_analysis.get("weaknesses", [])
            },
            "raw_scores": big_five_scores
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
