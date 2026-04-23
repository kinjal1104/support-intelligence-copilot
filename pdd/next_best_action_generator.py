import json
import unittest

def generate_next_best_action(ticket_text: str, analysis: dict) -> dict:
    """
    Generates an operational response plan based on ticket analysis.
    
    Logic follows a 'Heuristic Priority Matrix' considering revenue, 
    sentiment, and churn signals.
    """
    # Safe access to analysis fields with defaults
    risk_score = analysis.get("risk_score", 0)  # 0 to 10
    sentiment = analysis.get("sentiment", "neutral").lower()
    is_executive = analysis.get("is_executive_involved", False)
    revenue_impact = analysis.get("revenue_impact", "low").lower()
    renewal_window = analysis.get("renewal_window_days", 365)
    risk_factors = analysis.get("risk_factors", [])

    # 1. Determine Priority
    priority = "low"
    if risk_score >= 8 or "competitor_mention" in risk_factors or revenue_impact == "high":
        priority = "critical"
    elif risk_score >= 6 or renewal_window < 90 or is_executive:
        priority = "high"
    elif risk_score >= 4 or sentiment == "negative":
        priority = "medium"

    # 2. Identify Stakeholders
    stakeholders = ["Support Engineer"]
    if priority in ["high", "critical"]:
        stakeholders.append("Customer Success Manager")
    if revenue_impact == "high" or is_executive:
        stakeholders.append("Account Executive")
    if priority == "critical":
        stakeholders.append("VP of Engineering")
        stakeholders.append("Director of Support")

    # 3. Determine Actions
    actions = ["Review technical logs"]
    if "competitor_mention" in risk_factors:
        actions.append("Compare feature parity with mentioned competitor")
        actions.append("Prepare retention discount offer")
    if renewal_window < 90:
        actions.append("Schedule urgent renewal health check")
    if is_executive:
        actions.append("Draft executive summary of the root cause")
    
    if priority == "critical":
        actions.insert(0, "Initiate War Room / Incident Response")
    else:
        actions.append("Send standard troubleshooting guide")

    # 4. Escalation Recommendation
    if priority == "critical":
        esc = "Immediate escalation to Leadership Team. Bypass standard L2 queue."
    elif priority == "high":
        esc = "Escalate to Senior Engineer and notify the Account Team."
    else:
        esc = "Standard handling. No immediate escalation required."

    # 5. Executive Reply Draft
    if priority == "critical":
        draft = (f"Hello, I have personally taken ownership of this case. We recognize the urgency "
                 f"regarding your upcoming renewal and the technical hurdles you've encountered. "
                 f"Our engineering leadership is currently reviewing the logs, and I will provide "
                 f"an update every 2 hours until resolution.")
    elif priority == "high":
        draft = (f"Thank you for bringing this to our attention. We have flagged this as a high-priority "
                 f"item for our senior staff. We value our partnership and are committed to resolving "
                 f"this promptly to ensure your continued success.")
    else:
        draft = (f"Thank you for reaching out. We have received your request and our team is "
                 f"investigating the matter. We will get back to you shortly with next steps.")

    # 6. Internal Notes
    internal_notes = (
        f"Automated Alert: {priority.upper()} priority assigned. "
        f"Risk Score: {risk_score}/10. "
        f"Key Drivers: {', '.join(risk_factors) if risk_factors else 'None'}."
    )

    return {
        "priority": priority,
        "next_best_actions": actions,
        "stakeholders_to_involve": stakeholders,
        "escalation_recommendation": esc,
        "executive_reply_draft": draft,
        "internal_notes": internal_notes
    }

class TestNBAUtility(unittest.TestCase):
    def test_high_risk_churn_case(self):
        """Test a case with high revenue impact and competitor mentions."""
        ticket = "This is unacceptable. We are switching to CompetitorX if this isn't fixed."
        analysis = {
            "risk_score": 9,
            "sentiment": "negative",
            "is_executive_involved": True,
            "revenue_impact": "high",
            "renewal_window_days": 30,
            "risk_factors": ["competitor_mention", "executive_dissatisfaction"]
        }
        result = generate_next_best_action(ticket, analysis)
        self.assertEqual(result["priority"], "critical")
        self.assertIn("VP of Engineering", result["stakeholders_to_involve"])
        self.assertTrue(any("competitor" in a.lower() for a in result["next_best_actions"]))
        self.assertIn("War Room", result["next_best_actions"][0])

    def test_low_risk_standard_case(self):
        """Test a standard how-to question with no risk factors."""
        ticket = "How do I change my password?"
        analysis = {
            "risk_score": 1,
            "sentiment": "neutral",
            "is_executive_involved": False,
            "revenue_impact": "low",
            "renewal_window_days": 200
        }
        result = generate_next_best_action(ticket, analysis)
        self.assertEqual(result["priority"], "low")
        self.assertIn("Support Engineer", result["stakeholders_to_involve"])
        self.assertEqual(len(result["stakeholders_to_involve"]), 1)
        self.assertIn("standard troubleshooting guide", result["next_best_actions"])

if __name__ == "__main__":
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNBAUtility)
    unittest.TextTestRunner(verbosity=2).run(suite)

    # Example Usage
    mock_analysis = {
        "risk_score": 7,
        "sentiment": "frustrated",
        "is_executive_involved": False,
        "revenue_impact": "medium",
        "renewal_window_days": 45,
        "risk_factors": ["unresolved_incident", "renewal_at_risk"]
    }
    ticket_body = "We've had this open for three weeks. If we don't get the API integrated by our renewal date next month, we won't be able to justify the cost."
    nba_plan = generate_next_best_action(ticket_body, mock_analysis)
    print("\n--- NEXT BEST ACTION PLAN ---")
    print(f"PRIORITY: {nba_plan['priority'].upper()}")
    print(f"ESCALATION: {nba_plan['escalation_recommendation']}")