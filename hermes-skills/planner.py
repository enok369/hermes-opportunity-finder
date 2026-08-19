#!/usr/bin/env python3
"""
Hermes Skill: Opportunity Planner
Architectures implementation strategies for matched opportunities.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class OpportunityPlanner:
    """Design implementation plans for discovered opportunities."""
    
    def __init__(self):
        self.plan_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load strategy templates for different opportunity types."""
        return {
            "funding": {
                "phases": [
                    {
                        "phase": "Research & Validation",
                        "duration_days": 7,
                        "tasks": [
                            "Research investor profile and thesis",
                            "Validate fit with your product/service",
                            "Identify key decision makers",
                            "Gather success stories of similar raises"
                        ]
                    },
                    {
                        "phase": "Pitch Preparation",
                        "duration_days": 14,
                        "tasks": [
                            "Refine elevator pitch",
                            "Prepare deck tailored to investor",
                            "Gather metrics and traction data",
                            "Prepare FAQ and objection handlers"
                        ]
                    },
                    {
                        "phase": "Outreach & Follow-up",
                        "duration_days": 30,
                        "tasks": [
                            "Identify warm introduction paths",
                            "Send personalized initial email",
                            "Schedule intro call",
                            "Follow up 3x if no response",
                            "Iterate based on feedback"
                        ]
                    }
                ],
                "success_metrics": [
                    "Initial meeting scheduled",
                    "Pitch delivered",
                    "Term sheet received"
                ]
            },
            "partnership": {
                "phases": [
                    {
                        "phase": "Opportunity Assessment",
                        "duration_days": 3,
                        "tasks": [
                            "Define mutual value exchange",
                            "Identify strategic fit",
                            "Estimate revenue impact",
                            "Check for conflicts with existing partners"
                        ]
                    },
                    {
                        "phase": "Initial Contact",
                        "duration_days": 7,
                        "tasks": [
                            "Craft compelling partnership proposal",
                            "Find right contact person",
                            "Send warm introduction if possible",
                            "Request partnership meeting"
                        ]
                    },
                    {
                        "phase": "Negotiation & Closure",
                        "duration_days": 21,
                        "tasks": [
                            "Agree on terms and scope",
                            "Draft partnership agreement",
                            "Legal review",
                            "Execution and activation"
                        ]
                    }
                ],
                "success_metrics": [
                    "Meeting held",
                    "Agreement signed",
                    "First collaboration completed"
                ]
            },
            "acquisition": {
                "phases": [
                    {
                        "phase": "Target Validation",
                        "duration_days": 5,
                        "tasks": [
                            "Research target company thoroughly",
                            "Evaluate technical fit",
                            "Assess team quality",
                            "Estimate valuation range"
                        ]
                    },
                    {
                        "phase": "Approach Strategy",
                        "duration_days": 7,
                        "tasks": [
                            "Identify decision maker",
                            "Find warm introduction",
                            "Prepare strategic overview",
                            "Schedule exploratory call"
                        ]
                    },
                    {
                        "phase": "Due Diligence & Negotiation",
                        "duration_days": 60,
                        "tasks": [
                            "Technical due diligence",
                            "Financial review",
                            "Legal review",
                            "Term sheet negotiation",
                            "Final documentation"
                        ]
                    }
                ],
                "success_metrics": [
                    "LOI signed",
                    "Due diligence completed",
                    "Deal closed"
                ]
            },
            "grant": {
                "phases": [
                    {
                        "phase": "Grant Research",
                        "duration_days": 7,
                        "tasks": [
                            "Review grant requirements and timeline",
                            "Confirm eligibility",
                            "Gather success stories of prior recipients",
                            "Estimate timeline to funding"
                        ]
                    },
                    {
                        "phase": "Application Preparation",
                        "duration_days": 21,
                        "tasks": [
                            "Write compelling narrative",
                            "Prepare financial projections",
                            "Gather supporting documentation",
                            "Have application reviewed by mentor",
                            "Polish and submit"
                        ]
                    },
                    {
                        "phase": "Post-Submission",
                        "duration_days": 30,
                        "tasks": [
                            "Monitor application status",
                            "Prepare for potential interviews/Q&A",
                            "Plan follow-up if rejected",
                            "Prepare to execute on approval"
                        ]
                    }
                ],
                "success_metrics": [
                    "Application submitted",
                    "Interview conducted",
                    "Grant awarded"
                ]
            }
        }
    
    def create_plan(self, opportunity: Dict) -> Dict:
        """
        Create an implementation plan for an opportunity.
        Automatically categorizes based on title/content.
        """
        opp_type = self._classify_opportunity(opportunity)
        template = self.plan_templates.get(opp_type, self.plan_templates["partnership"])
        
        # Calculate timeline
        total_days = sum(phase["duration_days"] for phase in template["phases"])
        start_date = datetime.now()
        end_date = start_date + timedelta(days=total_days)
        
        plan = {
            "opportunity": opportunity,
            "type": opp_type,
            "created_at": start_date.isoformat(),
            "estimated_completion": end_date.isoformat(),
            "total_duration_days": total_days,
            "phases": []
        }
        
        # Populate phases with timeline
        current_date = start_date
        for phase_template in template["phases"]:
            phase_end = current_date + timedelta(days=phase_template["duration_days"])
            
            plan["phases"].append({
                "name": phase_template["phase"],
                "start_date": current_date.isoformat(),
                "end_date": phase_end.isoformat(),
                "duration_days": phase_template["duration_days"],
                "tasks": phase_template["tasks"],
                "status": "pending",
                "completed_tasks": 0
            })
            
            current_date = phase_end
        
        plan["success_metrics"] = template["success_metrics"]
        
        return plan
    
    def _classify_opportunity(self, opportunity: Dict) -> str:
        """Classify opportunity type based on content."""
        content = (opportunity.get("title", "") + " " + 
                  opportunity.get("summary", "") + " " + 
                  opportunity.get("content", "")).lower()
        
        keywords = {
            "funding": ["funding", "seed", "series", "investment", "investor", "raise"],
            "partnership": ["partner", "partnership", "collaboration", "collaborate"],
            "acquisition": ["acquire", "acquisition", "acquired", "exit", "buyout"],
            "grant": ["grant", "grants", "subsidy", "funding from government"]
        }
        
        scores = {}
        for opp_type, kws in keywords.items():
            scores[opp_type] = sum(1 for kw in kws if kw in content)
        
        if not any(scores.values()):
            return "partnership"  # Default
        
        return max(scores, key=scores.get)
    
    def update_plan_progress(self, plan: Dict, 
                            phase_index: int, 
                            task_index: int,
                            completed: bool = True) -> Dict:
        """Mark tasks as completed."""
        if 0 <= phase_index < len(plan["phases"]):
            phase = plan["phases"][phase_index]
            
            if completed and phase["completed_tasks"] < len(phase["tasks"]):
                phase["completed_tasks"] += 1
            
            # Check if phase is done
            if phase["completed_tasks"] == len(phase["tasks"]):
                phase["status"] = "completed"
                phase["completed_date"] = datetime.now().isoformat()
        
        return plan
    
    def generate_next_steps(self, plan: Dict) -> List[str]:
        """Generate actionable next steps from current plan."""
        next_steps = []
        
        for i, phase in enumerate(plan["phases"]):
            if phase["status"] == "pending":
                # This is the current phase
                tasks_remaining = len(phase["tasks"]) - phase["completed_tasks"]
                if tasks_remaining > 0:
                    # Get first incomplete task
                    for task in phase["tasks"]:
                        next_steps.append(f"Phase {i+1} ({phase['name']}): {task}")
                        if len(next_steps) >= 3:  # Top 3 next steps
                            break
                break
        
        return next_steps


# Hermes skill interface
def plan_opportunity(opportunity_json: str) -> str:
    """
    Create an implementation plan for an opportunity.
    
    Args:
        opportunity_json: JSON opportunity object
    
    Returns:
        JSON string with detailed implementation plan
    """
    opportunity = json.loads(opportunity_json)
    planner = OpportunityPlanner()
    plan = planner.create_plan(opportunity)
    
    return json.dumps(plan, indent=2, default=str)


if __name__ == "__main__":
    # Test locally
    test_opp = {
        "title": "Series A Funding Round - $5M Raise",
        "source": "ycombinator.com",
        "link": "https://example.com/series-a",
        "summary": "Growth-stage startup seeking $5M Series A investment",
        "published": "2024-01-10T10:00:00Z"
    }
    
    result = plan_opportunity(json.dumps(test_opp))
    print(result)
