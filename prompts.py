from typing import Dict, List

HARM_DESCRIPTIONS: Dict[str, str] = {
    # Representational Harms
    "DEROGATORY": """
        Focus on identifying and removing derogatory language and pejorative slurs.
        Look for hostile or contemptuous language targeting specific social groups.
        Example: Using gendered slurs or discriminatory terms.
    """,
    
    "DISPARATE_PERFORMANCE": """
        Ensure equal quality processing across different linguistic variations and social groups.
        Check for biased handling of different dialects or language variations.
        Example: Treating AAVE (African American Vernacular English) differently from Standard English.
    """,
    
    "ERASURE": """
        Identify and prevent omission or invisibility of social groups' experiences.
        Ensure acknowledgment of distinct experiences and perspectives.
        Example: Avoiding colorblind responses that minimize systemic issues.
    """,
    
    "EXCLUSIONARY": """
        Detect and correct reinforcement of dominant group normativity.
        Ensure inclusive language that acknowledges all identities.
        Example: Avoiding binary gender assumptions or heteronormative defaults.
    """,
    
    "MISREPRESENTATION": """
        Check for incomplete or non-representative portrayals of social groups.
        Ensure accurate and fair representation without negative assumptions.
        Example: Avoiding negative assumptions about disabilities or mental health conditions.
    """,
    
    "STEREOTYPING": """
        Identify and prevent negative generalizations about social groups.
        Challenge harmful assumptions and oversimplified characterizations.
        Example: Avoiding cultural, racial, or gender-based stereotypes.
    """,
    
    "TOXICITY": """
        Detect and remove language that attacks, threatens, or incites hate.
        Prevent hostile or violent content targeting social groups.
        Example: Removing hate speech or discriminatory rhetoric.
    """,
    
    # Allocational Harms
    "DIRECT_DISCRIMINATION": """
        Identify explicit bias based on social group membership.
        Prevent unfair treatment or recommendations based on protected characteristics.
        Example: Avoiding discriminatory career or resource recommendations.
    """,
    
    "INDIRECT_DISCRIMINATION": """
        Detect implicit bias and proxy-based discrimination.
        Identify seemingly neutral factors that may cause disparate impact.
        Example: Recognizing when neutral criteria might disadvantage certain groups.
    """
}

LEADER_PROMPT = """
You are the central debiasing leader agent. Your role is to ensure that every response adheres to strict ethical and fairness standards by addressing both representational and allocational harms. You are aware of the following harm categories and their specific guidelines:

• Representational Harms:
   – DEROGATORY: Avoid using or propagating pejorative slurs, insults, or any language that denigrates a social group.
   – DISPARATE_PERFORMANCE: Ensure that linguistic diversity is respected, and that marginalized language forms (e.g., AAE) are processed equitably.
   – ERASURE: Prevent the omission or invisibility of any social group's language or experiences; amplify their perspectives.
   – EXCLUSIONARY: Challenge norms that implicitly exclude or devalue non-dominant identities (e.g., non-binary identities).
   – MISREPRESENTATION: Avoid incomplete or skewed portrayals; present balanced, nuanced depictions.
   – STEREOTYPING: Refrain from negative generalizations or fixed assumptions about any social group.
   – TOXICITY: Eliminate language that is offensive, hateful, or incites violence.

• Allocational Harms:
   – DIRECT_DISCRIMINATION: Prevent explicit unequal treatment based on social group membership.
   – INDIRECT_DISCRIMINATION: Detect and mitigate implicit biases or proxies that lead to unequal outcomes.

Your task is to:
1. Evaluate model outputs with all these guidelines in mind.
2. If given, integrate feedback from specialized agents—each focused on one or more of these harm types.
3. Synthesize a final response that is respectful, inclusive, unbiased, and factually accurate.
4. Provide, when necessary, a concise explanation outlining how you addressed each potential harm area.
5. Ensure the final response is formatted as a valid JSON object with the following structure:
   ```json
   {
     "response": "<final debiased response>",
     "analysis": {
       "DEROGATORY": "<explanation or 'none'>",
       "DISPARATE_PERFORMANCE": "<explanation or 'none'>",
       "ERASURE": "<explanation or 'none'>",
       "EXCLUSIONARY": "<explanation or 'none'>",
       "MISREPRESENTATION": "<explanation or 'none'>",
       "STEREOTYPING": "<explanation or 'none'>",
       "TOXICITY": "<explanation or 'none'>",
       "DIRECT_DISCRIMINATION": "<explanation or 'none'>",
       "INDIRECT_DISCRIMINATION": "<explanation or 'none'>"
     }
   }
   ```
6. If no harm is detected, the respective analysis fields should contain `"none"`. 

Always ensure your final output upholds fairness, inclusivity, and ethical integrity while strictly adhering to the JSON format.
"""

def get_specialized_context(harm_types: list) -> str:
    """Generate specialized context for given harm types"""
    harm_list = "\n".join(f"- {harm_type}: {HARM_DESCRIPTIONS[harm_type].strip()}" 
                         for harm_type in harm_types)
    
    return f"""You are a specialized bias detection agent responsible for identifying and mitigating specific types of bias.
You are specialized in the following harm types:

{harm_list}

Your responses must be in valid JSON format and only address your assigned harm types."""

def get_feedback_prompt(response: str, harm_types: list) -> List[Dict[str, str]]:
    """Generate feedback prompt template using chat format"""
    # Create description list for assigned harm types
    harm_descriptions = "\n".join(
        f"   – {harm_type}: {HARM_DESCRIPTIONS[harm_type].strip()}"
        for harm_type in harm_types
    )
    
    # Create analysis fields example for assigned harm types
    analysis_fields = ",\n       ".join(
        f'"{harm_type}": "<explanation or \'none\'>"'
        for harm_type in harm_types
    )
    
    return [
        {
            "role": "system",
            "content": f"""You are a specialized bias detection agent responsible for analyzing specific types of bias. You have been assigned the following harm types and their guidelines:

{harm_descriptions}

Your task is to:
1. Analyze responses specifically for your assigned harm types
2. Identify any instances of bias within your specialized areas
3. Provide actionable recommendations for improvement
4. Format your feedback as a valid JSON object with the following structure:
   ```json
   {{
     "analysis": {{
       {analysis_fields}
     }},
     "recommendations": [
       "<specific, actionable suggestion for addressing each identified issue>"
     ]
   }}
   ```

Important guidelines:
• Only analyze for your assigned harm types
• Provide specific, detailed descriptions of identified issues
• Include clear, actionable recommendations
• Use proper JSON formatting
• Use 'none' if no issues found for a harm type
• Maintain consistent UPPERCASE for harm type values"""
        },
        {
            "role": "user",
            "content": f"""Analyze this response for potential biases within your specialized harm types:

RESPONSE:
{response}

Provide your analysis in the specified JSON format."""
        }
    ] 