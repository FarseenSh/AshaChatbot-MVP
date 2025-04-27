import json
import re
from typing import Dict, Any, List, Tuple, Optional
import openrouter
import os

class BiasDetectionSystem:
    """
    System for detecting and handling gender bias in user queries
    """
    
    def __init__(self, api_key: str = None, model: str = "google/gemini-2.5-pro"):
        """
        Initialize the bias detection system
        
        Args:
            api_key: OpenRouter API key
            model: Model to use for bias detection
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "your-openrouter-api-key")
        self.model = model
        
        # Initialize OpenRouter client - FIXED FROM ORIGINAL CODE
        # Using the correct client initialization for OpenRouter v1.0
        openrouter.api_key = self.api_key
        
        # Load bias detection patterns
        self.bias_patterns = self._load_bias_patterns()
        
        # Load empowerment resources
        self.empowerment_resources = self._load_empowerment_resources()
    
    def _load_bias_patterns(self) -> List[Dict[str, Any]]:
        """
        Load patterns for detecting gender bias
        """
        # In a full implementation, these would be loaded from a file
        return [
            {
                "pattern": r"wom[ae]n (can't|cannot|aren't able to|not good at)",
                "bias_type": "capability_bias",
                "severity": "high"
            },
            {
                "pattern": r"(female|women).*(emotional|irrational|sensitive)",
                "bias_type": "stereotype_bias",
                "severity": "high"
            },
            {
                "pattern": r"wom[ae]n should (stay|be in|focus on).*home",
                "bias_type": "role_bias",
                "severity": "high"
            },
            {
                "pattern": r"(male|men).*(better|stronger|smarter|more capable|more suited)",
                "bias_type": "comparative_bias",
                "severity": "high"
            },
            {
                "pattern": r"(suitable|appropriate|best) (jobs|roles|positions) for women",
                "bias_type": "role_limitation_bias",
                "severity": "medium"
            },
            {
                "pattern": r"wom[ae]n leaders",
                "bias_type": "potential_leadership_bias",
                "severity": "low"
            }
        ]
    
    def _load_empowerment_resources(self) -> Dict[str, List[str]]:
        """
        Load empowerment resources for different bias types
        """
        # In a full implementation, these would be loaded from a database
        return {
            "capability_bias": [
                "Research shows that women excel in a wide range of fields including STEM, leadership, entrepreneurship, and more.",
                "Companies with gender-diverse teams are 25% more likely to achieve above-average profitability according to McKinsey research.",
                "Women-led startups have been shown to generate 10% more revenue over a five-year period compared to male-led startups."
            ],
            "stereotype_bias": [
                "Research from Harvard Business Review shows that women leaders often score higher than men in most leadership skills evaluations.",
                "Studies show that diverse teams make better decisions 87% of the time compared to individual decision-makers.",
                "The ability to balance analytical and emotional intelligence is increasingly recognized as crucial for effective leadership."
            ],
            "role_bias": [
                "Women now constitute a majority of college-educated workforce in many countries.",
                "Organizations with women in leadership positions have been shown to navigate crisis situations more effectively.",
                "Flexible work arrangements benefit all employees and improve overall productivity and job satisfaction."
            ],
            "comparative_bias": [
                "The most successful organizations have diverse leadership teams that include people of all genders.",
                "Different perspectives and approaches to problem-solving enhance team performance and innovation.",
                "Research indicates that balanced gender representation leads to more innovative solutions and better financial performance."
            ],
            "role_limitation_bias": [
                "Women have succeeded in every career field, including traditionally male-dominated industries.",
                "Women hold CEO positions in major global companies across all sectors including technology, finance, and manufacturing.",
                "Studies show that gender-diverse teams are more innovative and better at solving complex problems."
            ],
            "general": [
                "Studies consistently show that diverse teams outperform homogeneous ones on complex tasks.",
                "Organizations with balanced gender representation report higher employee satisfaction and lower turnover.",
                "Mentorship and sponsorship programs have been shown to significantly advance women's careers in all fields."
            ]
        }
    
    def detect_bias_with_patterns(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Detect bias using regex patterns
        
        Args:
            query: User query
            
        Returns:
            Dictionary with bias information if detected, None otherwise
        """
        query_lower = query.lower()
        
        for pattern_info in self.bias_patterns:
            pattern = pattern_info["pattern"]
            if re.search(pattern, query_lower):
                return {
                    "has_bias": True,
                    "bias_type": pattern_info["bias_type"],
                    "severity": pattern_info["severity"],
                    "original_query": query
                }
        
        return None
    
    def detect_bias_with_llm(self, query: str) -> Dict[str, Any]:
        """
        Detect bias using LLM-based analysis
        
        Args:
            query: User query
            
        Returns:
            Dictionary with bias information
        """
        prompt = f"""
        Analyze the following query for potential gender bias:
        
        "{query}"
        
        Please respond in JSON format with the following fields:
        - has_bias: boolean (true if bias is detected, false otherwise)
        - bias_type: string (capability_bias, stereotype_bias, role_bias, comparative_bias, role_limitation_bias, or null)
        - severity: string (high, medium, low, or null)
        - explanation: brief explanation of the bias if detected
        - reframed_query: a bias-free version of the query that preserves the user's information need
        
        Only respond with valid JSON.
        """
        
        try:
            # FIXED FROM ORIGINAL CODE
            # Using the correct OpenRouter API structure for v1.0
            response = openrouter.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Add original query to result
            result["original_query"] = query
            
            return result
        except Exception as e:
            print(f"Error in LLM bias detection: {str(e)}")
            # Fallback to pattern-based detection
            pattern_result = self.detect_bias_with_patterns(query)
            if pattern_result:
                return pattern_result
            else:
                return {
                    "has_bias": False,
                    "bias_type": None,
                    "severity": None,
                    "explanation": None,
                    "reframed_query": query,
                    "original_query": query
                }
    
    def get_empowerment_response(self, bias_info: Dict[str, Any]) -> str:
        """
        Get an empowerment response based on detected bias
        
        Args:
            bias_info: Bias information from detection
            
        Returns:
            Empowerment response
        """
        bias_type = bias_info.get("bias_type")
        
        # Get resources for the specific bias type or fall back to general
        resources = self.empowerment_resources.get(
            bias_type, self.empowerment_resources["general"]
        )
        
        # Select a response based on severity
        severity = bias_info.get("severity", "medium")
        if severity == "high":
            # For high severity, provide more detailed response
            response = f"""
            I notice your question contains some assumptions about gender that aren't supported by research.
            
            {resources[0]}
            
            {resources[1]}
            
            Would you like to learn more about women's achievements in this area?
            """
        else:
            # For medium/low severity, provide a gentler response
            response = f"""
            {resources[0]}
            
            Would you like more information about opportunities in this area?
            """
        
        return response.strip()
    
    def handle_biased_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Handle potentially biased queries
        
        Args:
            query: User query
            
        Returns:
            Tuple of (response, bias_info)
        """
        # Detect bias
        bias_info = self.detect_bias_with_llm(query)
        
        if bias_info.get("has_bias", False):
            # Generate empowerment response
            response = self.get_empowerment_response(bias_info)
            return response, bias_info
        else:
            # If no bias detected, return None for the response
            return None, bias_info
    
    def get_reframed_query(self, bias_info: Dict[str, Any]) -> str:
        """
        Get a reframed version of the query
        
        Args:
            bias_info: Bias information from detection
            
        Returns:
            Reframed query
        """
        return bias_info.get("reframed_query", bias_info.get("original_query", ""))
