import json
import sys
import os

# Add the directory containing the module to the search path
# This ensures the script can find ticket_risk_analyzer.py regardless of the execution context
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ticket_risk_analyzer import analyze_ticket_risk

def main():
    """
    This example demonstrates how to use the analyze_ticket_risk function to 
    process a customer support ticket and extract revenue-critical insights.
    """
    
    # 1. Define the input data
    # Expected keys in the dictionary:
    # - ticket_text (str): The raw content of the support ticket.
    # - account_name (str): The name of the company/account.
    # - arr (int/float): Annual Recurring Revenue for the account.
    # - renewal_date (str): Format 'YYYY-MM-DD'.
    # - customer_tier (str): e.g., 'Enterprise', 'Pro', 'Standard'.
    ticket_data = {
        "ticket_text": "I've been trying to reach my account manager for days. This issue is blocking our production release. If this isn't resolved by EOD, our CTO will look into moving to a competitor after our contract expires in December.",
        "account_name": "Global Logistics Corp",
        "arr": 65000,
        "renewal_date": "2024-12-15",
        "customer_tier": "Enterprise"
    }

    # 2. Analyze the ticket risk
    # The function returns a dictionary containing risk scores, flags, and a summary.
    analysis_results = analyze_ticket_risk(ticket_data)

    # 3. Process the output
    # Output structure includes:
    # - escalation_risk (str): 'low' | 'medium' | 'high'
    # - churn_intent (str): 'low' | 'high'
    # - urgency (str): 'low' | 'high'
    # - executive_dissatisfaction (bool): True if keywords like CTO/CEO found
    # - renewal_timing_signal (bool): True if within renewal window or mentioned
    # - vendor_switching_signal (bool): True if competitor mentioned
    # - revenue_impact (str): 'low' | 'medium' | 'high' based on ARR/Tier
    # - detected_signals (list): Human-readable strings explaining the risk factors
    # - summary (str): A concise natural language summary of the risk profile

    print("--- Ticket Risk Analysis Report ---")
    print(f"Account:      {ticket_data['account_name']}")
    print(f"Risk Level:   {analysis_results['escalation_risk'].upper()}")
    print(f"Rev Impact:   {analysis_results['revenue_impact'].upper()}")
    print("-" * 35)
    
    print(f"Summary: {analysis_results['summary']}")
    
    print("\nSignals Detected:")
    for signal in analysis_results['detected_signals']:
        print(f" - {signal}")

    # Detailed JSON output for integration with CRM or Alerting systems
    print("\nFull Metadata Export:")
    print(json.dumps(analysis_results, indent=2))

if __name__ == "__main__":
    main()