import datetime
import re
import json

def analyze_ticket_risk(data: dict) -> dict:
    """
    Analyzes a support ticket to identify revenue-related risks and signals.
    """
    # Graceful handling of missing fields
    text = data.get("ticket_text", "").lower()
    arr = data.get("arr", 0)
    customer_tier = str(data.get("customer_tier", "Standard")).lower()
    renewal_date_str = data.get("renewal_date", "")
    
    signals = []
    
    # 1. Detect Executive Dissatisfaction
    exec_keywords = ["vp", "ceo", "cto", "leadership", "management", "executive", "unacceptable", "legal", "lawyer"]
    exec_dissat = any(word in text for word in exec_keywords)
    if exec_dissat:
        signals.append("Executive involvement/concern detected")

    # 2. Detect Churn Intent
    churn_keywords = ["cancel", "refund", "terminate", "closing our account", "unsubscribing", "stop using"]
    churn_match = any(word in text for word in churn_keywords)
    churn_intent = "high" if churn_match else "low"
    if churn_match:
        signals.append("Direct churn/cancellation language")

    # 3. Detect Vendor Switching
    switch_keywords = ["competitor", "alternative", "switching to", "evaluating other", "moving to"]
    vendor_switching = any(word in text for word in switch_keywords)
    if vendor_switching:
        signals.append("Vendor switching/competitor mention")

    # 4. Detect Urgency
    urgency_keywords = ["urgent", "asap", "emergency", "broken", "critical", "blocking", "immediately"]
    urgent_match = any(word in text for word in urgency_keywords)
    urgency = "high" if urgent_match else "low"
    if urgent_match:
        signals.append("High urgency language")

    # 5. Renewal Timing Signal
    renewal_timing_signal = False
    if "renew" in text or "contract" in text:
        renewal_timing_signal = True
        signals.append("Explicit mention of renewal/contract")
    
    # Date-based renewal check (if within 90 days)
    try:
        if renewal_date_str:
            renewal_date = datetime.datetime.strptime(renewal_date_str, "%Y-%m-%d")
            days_to_renewal = (renewal_date - datetime.datetime.now()).days
            if 0 <= days_to_renewal <= 90:
                renewal_timing_signal = True
                signals.append(f"Upcoming renewal window ({days_to_renewal} days)")
    except (ValueError, TypeError):
        pass

    # 6. Revenue Impact Assessment
    # High impact if ARR is > 50k or Enterprise tier
    if arr >= 50000 or customer_tier == "enterprise":
        revenue_impact = "high"
    elif arr >= 10000 or customer_tier == "pro":
        revenue_impact = "medium"
    else:
        revenue_impact = "low"

    # 7. Escalation Risk Logic
    # Escalation is high if there is churn intent OR (executive dissat AND high revenue)
    risk_score = 0
    if churn_intent == "high": risk_score += 3
    if exec_dissat: risk_score += 2
    if vendor_switching: risk_score += 2
    if urgency == "high": risk_score += 1
    if revenue_impact == "high": risk_score += 1

    if risk_score >= 4:
        escalation_risk = "high"
    elif risk_score >= 2:
        escalation_risk = "medium"
    else:
        escalation_risk = "low"

    # 8. Generate Summary
    summary_parts = [f"Ticket from {data.get('account_name', 'Unknown Account')}."]
    if escalation_risk == "high":
        summary_parts.append("This is a high-risk situation requiring immediate attention.")
    if churn_intent == "high" or vendor_switching:
        summary_parts.append("The customer is explicitly mentioning leaving or alternatives.")
    if not signals:
        summary_parts.append("No immediate risk signals detected.")
    else:
        summary_parts.append(f"Key issues: {', '.join(signals[:2])}.")

    return {
        "escalation_risk": escalation_risk,
        "churn_intent": churn_intent,
        "urgency": urgency,
        "executive_dissatisfaction": exec_dissat,
        "renewal_timing_signal": renewal_timing_signal,
        "vendor_switching_signal": vendor_switching,
        "revenue_impact": revenue_impact,
        "detected_signals": signals,
        "summary": " ".join(summary_parts)
    }

def test_high_risk_ticket():
    print("Testing: High Risk Ticket...")
    data = {
        "ticket_text": "I am the CTO and this downtime is unacceptable. We are evaluating competitors and considering switching to another vendor before our renewal next month.",
        "account_name": "MegaCorp",
        "arr": 100000,
        "renewal_date": "2024-12-01",
        "customer_tier": "Enterprise"
    }
    result = analyze_ticket_risk(data)
    
    assert result["escalation_risk"] == "high"
    assert result["executive_dissatisfaction"] is True
    assert result["vendor_switching_signal"] is True
    assert result["renewal_timing_signal"] is True
    assert "CTO" in result["summary"] or "high-risk" in result["summary"]
    print("Result:", result["summary"])
    print("PASSED\n")

def test_low_risk_ticket():
    print("Testing: Low Risk Ticket...")
    data = {
        "ticket_text": "Hi, how do I change my password in the settings panel? Thanks!",
        "account_name": "SmallBiz",
        "arr": 1200,
        "renewal_date": "2025-08-15",
        "customer_tier": "Free"
    }
    result = analyze_ticket_risk(data)
    
    assert result["escalation_risk"] == "low"
    assert result["churn_intent"] == "low"
    assert result["executive_dissatisfaction"] is False
    print("Result:", result["summary"])
    print("PASSED\n")

if __name__ == "__main__":
    # Run tests
    test_high_risk_ticket()
    test_low_risk_ticket()

    # Sample incoming webhook data example
    incoming_ticket = {
        "ticket_text": "Our CEO is very upset that the integration is still broken. This is urgent. If this isn't fixed, we will have to cancel our contract.",
        "account_name": "Acme Inc",
        "arr": 45000,
        "renewal_date": "2024-11-30",
        "customer_tier": "Pro"
    }

    # Run Analysis
    analysis = analyze_ticket_risk(incoming_ticket)

    # Output results
    print("--- Ticket Risk Analysis ---")
    print(f"Account: {incoming_ticket['account_name']}")
    print(f"Escalation Level: {analysis['escalation_risk'].upper()}")
    print(f"Summary: {analysis['summary']}")
    print(f"Signals Detected: {analysis['detected_signals']}")
    print("\nFull Structured Data:")
    print(json.dumps(analysis, indent=2))