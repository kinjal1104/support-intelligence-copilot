
import sys
from pathlib import Path

# Add project root to sys.path to ensure local code is prioritized
# This allows testing local changes without installing the package
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pytest
import datetime
from unittest.mock import patch
from ticket_risk_analyzer import analyze_ticket_risk

# Helper to mock datetime.datetime.now() for consistent date testing
@pytest.fixture
def mock_datetime_now():
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(2024, 9, 1, 10, 0, 0) # Fixed date for testing
    with patch('datetime.datetime', MockDatetime):
        yield

def test_empty_input_data():
    """
    Test with an empty dictionary to ensure graceful handling of missing fields.
    """
    data = {}
    result = analyze_ticket_risk(data)

    assert result["escalation_risk"] == "low"
    assert result["churn_intent"] == "low"
    assert result["urgency"] == "low"
    assert result["executive_dissatisfaction"] is False
    assert result["renewal_timing_signal"] is False
    assert result["vendor_switching_signal"] is False
    assert result["revenue_impact"] == "low"
    assert result["detected_signals"] == []
    assert "No immediate risk signals detected." in result["summary"]
    assert "Unknown Account" in result["summary"]

def test_medium_risk_ticket_with_urgency_and_pro_tier():
    """
    Test a ticket that should result in medium risk due to urgency and a pro tier account.
    """
    data = {
        "ticket_text": "This issue is urgent, our pro account is experiencing critical problems.",
        "account_name": "ProSolutions",
        "arr": 25000,
        "renewal_date": "2025-03-01",
        "customer_tier": "Pro"
    }
    result = analyze_ticket_risk(data)

    assert result["escalation_risk"] == "medium"
    assert result["churn_intent"] == "low"
    assert result["urgency"] == "high"
    assert result["executive_dissatisfaction"] is False
    assert result["renewal_timing_signal"] is False
    assert result["vendor_switching_signal"] is False
    assert result["revenue_impact"] == "medium"
    assert "High urgency language" in result["detected_signals"]
    assert "ProSolutions" in result["summary"]
    assert "Key issues: High urgency language." in result["summary"]

def test_renewal_timing_signal_within_90_days(mock_datetime_now):
    """
    Test a ticket with a renewal date within the 90-day window.
    """
    # Mocked current date is 2024-09-01
    data = {
        "ticket_text": "We need to discuss our upcoming contract renewal.",
        "account_name": "FutureTech",
        "arr": 30000,
        "renewal_date": "2024-11-20", # 80 days from 2024-09-01
        "customer_tier": "Standard"
    }
    result = analyze_ticket_risk(data)

    assert result["renewal_timing_signal"] is True
    assert "Explicit mention of renewal/contract" in result["detected_signals"]
    assert "Upcoming renewal window (80 days)" in result["detected_signals"]
    assert result["escalation_risk"] == "medium" # renewal signal adds to risk score

def test_renewal_timing_signal_exactly_90_days(mock_datetime_now):
    """
    Test a ticket with a renewal date exactly 90 days from now.
    """
    # Mocked current date is 2024-09-01
    data = {
        "ticket_text": "Just checking on our contract.",
        "account_name": "BoundaryCo",
        "arr": 15000,
        "renewal_date": "2024-11-30", # 90 days from 2024-09-01
        "customer_tier": "Standard"
    }
    result = analyze_ticket_risk(data)

    assert result["renewal_timing_signal"] is True
    assert "Upcoming renewal window (90 days)" in result["detected_signals"]
    assert "Explicit mention of renewal/contract" not in result["detected_signals"] # Only date-based
    assert result["escalation_risk"] == "medium"

def test_renewal_timing_signal_outside_90_days(mock_datetime_now):
    """
    Test a ticket with a renewal date outside the 90-day window.
    """
    # Mocked current date is 2024-09-01
    data = {
        "ticket_text": "Just checking on our contract.",
        "account_name": "LongTerm",
        "arr": 20000,
        "renewal_date": "2024-12-01", # 91 days from 2024-09-01
        "customer_tier": "Standard"
    }
    result = analyze_ticket_risk(data)

    assert result["renewal_timing_signal"] is False
    assert "Upcoming renewal window" not in result["detected_signals"]
    assert "Explicit mention of renewal/contract" not in result["detected_signals"]
    assert result["escalation_risk"] == "low"

def test_invalid_renewal_date_format():
    """
    Test with an invalid renewal date string to ensure graceful handling.
    """
    data = {
        "ticket_text": "Routine question.",
        "account_name": "BadDateCo",
        "arr": 5000,
        "renewal_date": "2024/11/20", # Invalid format
        "customer_tier": "Standard"
    }
    result = analyze_ticket_risk(data)

    assert result["renewal_timing_signal"] is False # Should not trigger from date
    assert "Upcoming renewal window" not in result["detected_signals"]
    assert result["escalation_risk"] == "low"

def test_revenue_impact_boundaries():
    """
    Test revenue impact calculation at various ARR and customer tier boundaries.
    """
    # ARR = 0, Standard -> Low
    data_low_arr = {"ticket_text": "", "arr": 0, "customer_tier": "Standard"}
    assert analyze_ticket_risk(data_low_arr)["revenue_impact"] == "low"

    # ARR = 9999, Standard -> Low
    data_low_arr_boundary = {"ticket_text": "", "arr": 9999, "customer_tier": "Standard"}
    assert analyze_ticket_risk(data_low_arr_boundary)["revenue_impact"] == "low"

    # ARR = 10000, Standard -> Medium
    data_medium_arr_boundary = {"ticket_text": "", "arr": 10000, "customer_tier": "Standard"}
    assert analyze_ticket_risk(data_medium_arr_boundary)["revenue_impact"] == "medium"

    # ARR = 49999, Pro -> Medium
    data_medium_tier_boundary = {"ticket_text": "", "arr": 49999, "customer_tier": "Pro"}
    assert analyze_ticket_risk(data_medium_tier_boundary)["revenue_impact"] == "medium"

    # ARR = 50000, Pro -> High
    data_high_arr_boundary = {"ticket_text": "", "arr": 50000, "customer_tier": "Pro"}
    assert analyze_ticket_risk(data_high_arr_boundary)["revenue_impact"] == "high"

    # Enterprise tier -> High (regardless of ARR)
    data_enterprise_tier = {"ticket_text": "", "arr": 1000, "customer_tier": "Enterprise"}
    assert analyze_ticket_risk(data_enterprise_tier)["revenue_impact"] == "high"

    # Pro tier -> Medium (regardless of ARR if ARR < 50k)
    data_pro_tier = {"ticket_text": "", "arr": 500, "customer_tier": "Pro"}
    assert analyze_ticket_risk(data_pro_tier)["revenue_impact"] == "medium"

def test_case_insensitivity():
    """
    Test that keyword detection and customer tier are case-insensitive.
    """
    data = {
        "ticket_text": "This is URGENT. Our CEO is very upset. We are evaluating ALTERNATIVES.",
        "account_name": "CaseSensitiveCo",
        "arr": 60000,
        "renewal_date": "2025-01-01",
        "customer_tier": "ENTERPRISE"
    }
    result = analyze_ticket_risk(data)

    assert result["urgency"] == "high"
    assert result["executive_dissatisfaction"] is True
    assert result["vendor_switching_signal"] is True
    assert result["revenue_impact"] == "high"
    assert result["escalation_risk"] == "high"
    assert "High urgency language" in result["detected_signals"]
    assert "Executive involvement/concern detected" in result["detected_signals"]
    assert "Vendor switching/competitor mention" in result["detected_signals"]

def test_no_signals_detected():
    """
    Test a ticket with no keywords or other risk factors.
    """
    data = {
        "ticket_text": "I have a question about a feature. Can you help me find the documentation?",
        "account_name": "HappyCustomer",
        "arr": 5000,
        "renewal_date": "2025-06-30",
        "customer_tier": "Standard"
    }
    result = analyze_ticket_risk(data)

    assert result["escalation_risk"] == "low"
    assert result["churn_intent"] == "low"
    assert result["urgency"] == "low"
    assert result["executive_dissatisfaction"] is False
    assert result["renewal_timing_signal"] is False
    assert result["vendor_switching_signal"] is False
    assert result["revenue_impact"] == "low"
    assert result["detected_signals"] == []
    assert "No immediate risk signals detected." in result["summary"]

def test_churn_intent_low_arr():
    """
    Test a ticket with explicit churn intent but from a low ARR account.
    Should still be high churn intent, but potentially lower escalation risk.
    """
    data = {
        "ticket_text": "I want to cancel my account. Please process a refund.",
        "account_name": "SmallFry",
        "arr": 500,
        "renewal_date": "2025-07-01",
        "customer_tier": "Free"
    }
    result = analyze_ticket_risk(data)

    assert result["churn_intent"] == "high"
    assert result["revenue_impact"] == "low"
    assert result["escalation_risk"] == "high" # Churn intent alone makes it high risk
    assert "Direct churn/cancellation language" in result["detected_signals"]
    assert "The customer is explicitly mentioning leaving or alternatives." in result["summary"]

def test_executive_dissatisfaction_only():
    """
    Test a ticket with only executive dissatisfaction, no other major signals.
    """
    data = {
        "ticket_text": "Our VP is very unhappy with the recent performance.",
        "account_name": "ConcernedCorp",
        "arr": 15000,
        "renewal_date": "2025-09-01",
        "customer_tier": "Pro"
    }
    result = analyze_ticket_risk(data)

    assert result["executive_dissatisfaction"] is True
    assert result["churn_intent"] == "low"
    assert result["urgency"] == "low"
    assert result["vendor_switching_signal"] is False
    assert result["revenue_impact"] == "medium"
    assert result["escalation_risk"] == "medium" # Exec dissat (2) + Medium revenue (0) = 2 (medium)
    assert "Executive involvement/concern detected" in result["detected_signals"]
    assert "Key issues: Executive involvement/concern detected." in result["summary"]

def test_summary_generation_multiple_signals():
    """
    Test that the summary correctly reflects multiple detected signals.
    """
    data = {
        "ticket_text": "Our CEO is demanding an immediate fix. We are considering alternatives if this isn't resolved ASAP.",
        "account_name": "DemandingClient",
        "arr": 75000,
        "renewal_date": "2025-01-01",
        "customer_tier": "Enterprise"
    }
    result = analyze_ticket_risk(data)

    assert result["escalation_risk"] == "high"
    assert "DemandingClient" in result["summary"]
    assert "high-risk situation requiring immediate attention." in result["summary"]
    assert "The customer is explicitly mentioning leaving or alternatives." in result["summary"]
    assert "Key issues: Executive involvement/concern detected, High urgency language." in result["summary"] # Checks that only first two are listed