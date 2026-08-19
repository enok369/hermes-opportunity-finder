#!/usr/bin/env python3
"""
Hermes Skill: Opportunity Filter
Evaluates scraped items against criteria and learns over time.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re


@dataclass
class OpportunityCriteria:
    """Define what counts as a match."""
    keywords: List[str]  # Must contain one of these
    exclude_keywords: List[str]  # Must NOT contain these
    domains: List[str]  # Acceptable domains (empty = all)
    min_relevance_score: float  # 0.0 - 1.0
    max_age_days: int  # How old is too old
    require_action_url: bool  # Must have a clickable link


class OpportunityFilter:
    """Filter and score opportunities based on criteria."""
    
    def __init__(self, criteria: Optional[Dict] = None):
        self.criteria = criteria or self._default_criteria()
        self.seen_urls = set()  # Prevent duplicates
        self.matched_history = []  # Track what matched
    
    def _default_criteria(self) -> OpportunityCriteria:
        """Default criteria — customize for your use case."""
        return OpportunityCriteria(
            keywords=[
                "startup", "funding", "seed", "growth",
                "partnership", "acquisition", "collaboration",
                "open source", "grant", "opportunity"
            ],
            exclude_keywords=[
                "scam", "fake", "spam", "crypto", "blockchain",
                "mlm", "recruitment spam", "job board"
            ],
            domains=["ycombinator.com", "producthunt.com", "news.ycombinator.com"],
            min_relevance_score=0.6,
            max_age_days=30,
            require_action_url=True
        )
    
    def filter_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """
        Filter list of opportunities, keeping only matches.
        Returns: List of (opportunity, score, reason) tuples.
        """
        matched = []
        
        for opp in opportunities:
            # Skip duplicates
            url = opp.get("link") or opp.get("source", "")
            if url in self.seen_urls:
                continue
            self.seen_urls.add(url)
            
            # Score and filter
            score, reason = self._score_opportunity(opp)
            
            if score >= self.criteria.min_relevance_score:
                matched.append({
                    "opportunity": opp,
                    "score": score,
                    "reason": reason,
                    "filtered_at": datetime.now().isoformat()
                })
        
        # Sort by score descending
        matched.sort(key=lambda x: x["score"], reverse=True)
        
        # Update history
        self.matched_history.extend(matched)
        
        return matched
    
    def _score_opportunity(self, opp: Dict) -> tuple[float, str]:
        """Score an opportunity 0.0 - 1.0 and explain why."""
        title = opp.get("title", "") or opp.get("summary", "")
        content = (title + " " + opp.get("content", "") + " " + 
                   opp.get("summary", "")).lower()
        
        score = 0.5  # Base score
        reasons = []
        
        # Check required action link
        if self.criteria.require_action_url:
            if not opp.get("link"):
                return 0.0, "No action link"
        
        # Check keywords (boost score)
        keyword_matches = sum(1 for kw in self.criteria.keywords 
                              if kw.lower() in content)
        if keyword_matches == 0:
            return 0.0, f"No keywords found"
        
        keyword_boost = min(keyword_matches * 0.15, 0.4)
        score += keyword_boost
        reasons.append(f"Matched {keyword_matches} keywords (+{keyword_boost:.2f})")
        
        # Check exclude keywords (kill score)
        excluded = any(kw.lower() in content 
                      for kw in self.criteria.exclude_keywords)
        if excluded:
            return 0.0, "Contains excluded keywords"
        
        # Check domain whitelist
        if self.criteria.domains:
            source = opp.get("source", "").lower()
            domain_match = any(domain.lower() in source 
                              for domain in self.criteria.domains)
            if not domain_match:
                score *= 0.7  # Penalize non-whitelisted domains
                reasons.append("Non-whitelisted domain (-0.3)")
        
        # Recency bonus
        published = opp.get("published") or opp.get("discovered_at", "")
        if published:
            try:
                from dateutil.parser import parse
                pub_date = parse(published)
                age_days = (datetime.now(pub_date.tzinfo) - pub_date).days
                
                if age_days > self.criteria.max_age_days:
                    return 0.0, f"Too old ({age_days} days)"
                
                if age_days < 1:
                    score += 0.15
                    reasons.append("Fresh (< 1 day) (+0.15)")
            except:
                pass
        
        return min(score, 1.0), " | ".join(reasons)
    
    def learn_from_feedback(self, matched_opp: Dict, user_feedback: str):
        """
        Learn from user feedback to improve filtering over time.
        
        Args:
            matched_opp: The opportunity that was matched
            user_feedback: "relevant", "irrelevant", "false_positive", etc.
        """
        if user_feedback == "relevant":
            # Extract patterns from this match
            title = matched_opp.get("title", "")
            words = title.lower().split()
            
            # Add new keywords if they seem discriminative
            for word in words:
                if len(word) > 4 and word not in self.criteria.keywords:
                    self.criteria.keywords.append(word)
        
        elif user_feedback == "false_positive":
            # Add to exclude list
            title = matched_opp.get("title", "")
            words = title.lower().split()
            for word in words:
                if len(word) > 4 and word not in self.criteria.exclude_keywords:
                    self.criteria.exclude_keywords.append(word)
    
    def update_criteria(self, new_criteria: Dict):
        """Update filtering criteria on the fly."""
        if "keywords" in new_criteria:
            self.criteria.keywords = new_criteria["keywords"]
        if "exclude_keywords" in new_criteria:
            self.criteria.exclude_keywords = new_criteria["exclude_keywords"]
        if "min_relevance_score" in new_criteria:
            self.criteria.min_relevance_score = new_criteria["min_relevance_score"]
        if "max_age_days" in new_criteria:
            self.criteria.max_age_days = new_criteria["max_age_days"]
    
    def get_statistics(self) -> Dict:
        """Return filtering statistics."""
        return {
            "total_matched": len(self.matched_history),
            "unique_opportunities_seen": len(self.seen_urls),
            "current_keywords": self.criteria.keywords,
            "current_exclude_keywords": self.criteria.exclude_keywords,
            "recent_matches": self.matched_history[-5:]
        }


# Hermes skill interface
def filter_opportunities(opportunities_json: str, criteria_json: Optional[str] = None) -> str:
    """
    Filter opportunities and return matches.
    
    Args:
        opportunities_json: JSON list of opportunity objects
        criteria_json: Optional JSON criteria overrides
    
    Returns:
        JSON string with matched opportunities and scores
    """
    opportunities = json.loads(opportunities_json)
    
    filter_obj = OpportunityFilter()
    
    if criteria_json:
        criteria = json.loads(criteria_json)
        filter_obj.update_criteria(criteria)
    
    matched = filter_obj.filter_opportunities(opportunities)
    
    return json.dumps({
        "matched": matched,
        "stats": filter_obj.get_statistics()
    }, indent=2, default=str)


if __name__ == "__main__":
    # Test locally
    test_opps = [
        {
            "title": "Startup Founder Looking for Growth Funding",
            "source": "ycombinator.com",
            "link": "https://example.com/1",
            "summary": "We're a startup seeking seed funding from investors",
            "published": "2024-01-10T10:00:00Z"
        },
        {
            "title": "Spam Email Campaign for MLM",
            "source": "spam.net",
            "link": "https://example.com/2",
            "summary": "Make money now with our mlm crypto blockchain scheme",
            "published": "2024-01-09T10:00:00Z"
        },
        {
            "title": "Open Source Partnership Opportunity",
            "source": "github.com",
            "link": "https://example.com/3",
            "summary": "Seeking collaboration on open source project",
            "published": "2024-01-10T15:00:00Z"
        }
    ]
    
    result = filter_opportunities(json.dumps(test_opps))
    print(result)
