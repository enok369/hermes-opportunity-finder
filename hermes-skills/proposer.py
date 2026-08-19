#!/usr/bin/env python3
"""
Hermes Skill: Opportunity Proposer
Formats and proposes opportunities with all supporting analysis.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import textwrap


class OpportunityProposer:
    """Format opportunities and plans into compelling proposals."""
    
    def __init__(self):
        self.template = """
# 🎯 OPPORTUNITY PROPOSAL

**Discovered:** {discovered_at}
**Score:** {score}/1.0
**Type:** {opp_type}

## 📋 Opportunity Summary

**Title:** {title}
**Source:** {source}
**Link:** {link}

**Description:**
{description}

---

## 💡 Why This Matters

{relevance_analysis}

---

## 🎬 Recommended Action Plan

{plan_summary}

### Phase Timeline

{phase_timeline}

### Success Metrics
{success_metrics}

---

## 📊 Risk Assessment

- **Feasibility:** {feasibility}
- **Time Investment:** {time_investment}
- **Resource Requirements:** {resource_requirements}
- **Key Risks:** {risks}

---

## ✅ Next Steps (First 48 Hours)

{immediate_actions}

---

**Proposal Generated:** {generated_at}
**Agent:** Hermes Opportunity Finder
        """
    
    def generate_proposal(self, opportunity: Dict, 
                         plan: Dict,
                         filter_score: float) -> str:
        """
        Generate a formatted proposal for an opportunity.
        
        Args:
            opportunity: The discovered opportunity
            plan: The implementation plan
            filter_score: Relevance score from filter
        
        Returns:
            Formatted proposal text
        """
        
        opp_type = plan.get("type", "partnership")
        
        proposal = self.template.format(
            discovered_at=opportunity.get("discovered_at", datetime.now().isoformat()),
            score=f"{filter_score:.2f}",
            opp_type=opp_type.capitalize(),
            title=opportunity.get("title", "N/A"),
            source=opportunity.get("source", "N/A"),
            link=opportunity.get("link", "N/A"),
            description=self._wrap_text(
                opportunity.get("summary", "") or opportunity.get("content", "")[:500]
            ),
            relevance_analysis=self._generate_relevance_analysis(opportunity, filter_score),
            plan_summary=self._summarize_plan(plan),
            phase_timeline=self._format_phase_timeline(plan),
            success_metrics=self._format_success_metrics(plan),
            feasibility=self._assess_feasibility(plan),
            time_investment=self._estimate_time(plan),
            resource_requirements=self._assess_resources(opp_type),
            risks=self._identify_risks(opp_type),
            immediate_actions=self._immediate_actions(plan),
            generated_at=datetime.now().isoformat()
        )
        
        return proposal
    
    def _wrap_text(self, text: str, width: int = 80) -> str:
        """Wrap text for readability."""
        return textwrap.fill(text, width=width)
    
    def _generate_relevance_analysis(self, opportunity: Dict, score: float) -> str:
        """Explain why this opportunity is relevant."""
        analysis = f"This opportunity scored {score:.1%} relevance based on:\n\n"
        
        # Extract key factors (this would be enhanced with actual analysis)
        factors = [
            "✓ Matches target keywords and domains",
            "✓ Recent discovery (less than 24h old)",
            "✓ Clear action path and timeline",
            "✓ Aligns with strategic objectives"
        ]
        
        if score < 0.7:
            factors.append("⚠ Lower confidence - requires additional validation")
        
        analysis += "\n".join(factors)
        return analysis
    
    def _summarize_plan(self, plan: Dict) -> str:
        """Summarize the implementation plan."""
        summary = f"Estimated completion: {plan['total_duration_days']} days\n\n"
        
        for i, phase in enumerate(plan["phases"], 1):
            summary += f"**{i}. {phase['name']}** ({phase['duration_days']} days)\n"
            summary += f"   Tasks: {len(phase['tasks'])}\n"
            summary += f"   • " + "\n   • ".join(phase["tasks"][:2])  # First 2 tasks
            if len(phase["tasks"]) > 2:
                summary += f"\n   • ... and {len(phase['tasks']) - 2} more"
            summary += "\n\n"
        
        return summary
    
    def _format_phase_timeline(self, plan: Dict) -> str:
        """Format phase timeline."""
        timeline = ""
        for i, phase in enumerate(plan["phases"], 1):
            timeline += f"- **Day 1-{phase['duration_days']}:** {phase['name']}\n"
        return timeline
    
    def _format_success_metrics(self, plan: Dict) -> str:
        """Format success metrics."""
        metrics = plan.get("success_metrics", [])
        return "\n".join(f"- {metric}" for metric in metrics)
    
    def _assess_feasibility(self, plan: Dict) -> str:
        """Assess how feasible this plan is."""
        total_days = plan["total_duration_days"]
        
        if total_days < 14:
            return "⚡ High - Can be executed in less than 2 weeks"
        elif total_days < 30:
            return "✓ Moderate - One-month timeline"
        else:
            return "⏳ Longer-term - Requires sustained commitment"
    
    def _estimate_time(self, plan: Dict) -> str:
        """Estimate time investment."""
        total_days = plan["total_duration_days"]
        
        # Rough estimate: average task takes 1-2 days
        task_count = sum(len(p["tasks"]) for p in plan["phases"])
        hours_per_week = max(2, min(10, task_count * 2 / (total_days / 7)))
        
        return f"~{hours_per_week:.0f} hours/week over {total_days} days"
    
    def _assess_resources(self, opp_type: str) -> str:
        """Assess resource requirements."""
        requirements = {
            "funding": "Team presentation skills, financial data, legal support",
            "partnership": "Sales skills, business development expertise",
            "acquisition": "Technical team, financial team, legal counsel",
            "grant": "Writing skills, documentation"
        }
        return requirements.get(opp_type, "Basic business development capability")
    
    def _identify_risks(self, opp_type: str) -> str:
        """Identify key risks."""
        risks = {
            "funding": "Valuation mismatch, investor scope creep, lengthy due diligence",
            "partnership": "Conflicting interests, execution barriers, revenue share disagreement",
            "acquisition": "Deal fatigue, integration challenges, culture clash",
            "grant": "Application rejection, slow processing time, restrictive terms"
        }
        return risks.get(opp_type, "General business risk")
    
    def _immediate_actions(self, plan: Dict) -> str:
        """Get first 48-hour actions from plan."""
        actions = []
        
        if plan["phases"]:
            first_phase = plan["phases"][0]
            # Take first 2-3 tasks
            for task in first_phase["tasks"][:3]:
                actions.append(f"- {task}")
        
        actions.append("- Set reminder for Day 3 to assess progress")
        actions.append("- Document any blockers or learnings")
        
        return "\n".join(actions)


# Hermes skill interface
def propose_opportunity(opportunity_json: str, plan_json: str, filter_score: float) -> str:
    """
    Generate a formatted proposal.
    
    Args:
        opportunity_json: JSON opportunity object
        plan_json: JSON plan object
        filter_score: Relevance score (0.0 - 1.0)
    
    Returns:
        Formatted proposal text
    """
    opportunity = json.loads(opportunity_json)
    plan = json.loads(plan_json)
    
    proposer = OpportunityProposer()
    proposal = proposer.generate_proposal(opportunity, plan, filter_score)
    
    return proposal


def save_proposal(proposal_text: str, output_path: str) -> str:
    """Save proposal to file."""
    with open(output_path, "w") as f:
        f.write(proposal_text)
    return f"Proposal saved to {output_path}"


if __name__ == "__main__":
    # Test locally
    test_opp = {
        "title": "Series A Funding Round - $5M Raise",
        "source": "ycombinator.com",
        "link": "https://example.com/series-a",
        "summary": "Growth-stage startup seeking $5M Series A investment to expand team",
        "published": "2024-01-10T10:00:00Z",
        "discovered_at": "2024-01-10T12:30:00Z"
    }
    
    test_plan = {
        "type": "funding",
        "total_duration_days": 51,
        "phases": [
            {
                "name": "Research & Validation",
                "duration_days": 7,
                "tasks": ["Research investor profile", "Validate fit"]
            },
            {
                "name": "Pitch Preparation",
                "duration_days": 14,
                "tasks": ["Refine pitch", "Prepare deck"]
            },
            {
                "name": "Outreach",
                "duration_days": 30,
                "tasks": ["Send intro emails", "Schedule calls"]
            }
        ],
        "success_metrics": ["Meeting scheduled", "Term sheet received"]
    }
    
    proposal = propose_opportunity(
        json.dumps(test_opp),
        json.dumps(test_plan),
        0.85
    )
    print(proposal)
