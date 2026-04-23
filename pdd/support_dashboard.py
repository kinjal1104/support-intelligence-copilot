import streamlit as st

# --- MOCK LOGIC FUNCTIONS (from separate files) ---

def analyze_ticket_risk(text, customer_data):
    """
    Analyzes the risk of a support ticket based on text content and customer data.
    """
    # Mock logic for analysis
    return {
        "risk_score": "High" if customer_data['arr'] > 100000 else "Medium",
        "summary": "Customer is frustrated with recurring downtime and is threatening to cancel ahead of their renewal date.",
        "signals": ["Negative Sentiment", "Churn Threat", "Technical Blockers"],
        "impact_analysis": f"Potential loss of {customer_data['arr']} ARR. Account is {customer_data['tier']} tier.",
        "escalation_recommendation": "Executive Sponsor Involvement Required",
        "internal_brief": f"Account {customer_data['account_name']} is reporting critical issues. Sentiment is highly negative."
    }

def generate_next_best_action(text, risk_results, customer_data):
    """
    Generates strategic response actions based on risk analysis and customer data.
    """
    # Mock logic for recommendations
    return {
        "actions": [
            "Schedule immediate 1:1 call with the CTO",
            "Provision temporary credits for downtime",
            "Assign a dedicated Senior Solutions Architect"
        ],
        "stakeholders": ["Customer Success Manager", "VP of Engineering", "Account Executive"],
        "internal_notes": "The customer has been with us for 2 years. This is the first time they have escalated to this level.",
        "executive_reply": f"Hi {customer_data['account_name']} Team,\n\nI've received your feedback regarding the recent issues. We value our partnership and I am personally overseeing the resolution... "
    }

# --- MAIN STREAMLIT APPLICATION ---

# Page Configuration
st.set_page_config(page_title="Support Intelligence Copilot", layout="wide")

# Custom CSS for polished look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title(" Support Intelligence Copilot")
    st.markdown("Analyze high-stakes support tickets, assess churn risk, and generate strategic recovery plans.")
    
    st.divider()

    # Sidebar / Input Section
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ticket_text = st.text_area("Support Ticket Text", height=250, placeholder="Paste the customer's message here...")
        
        with col2:
            st.subheader("Customer Metadata")
            account_name = st.text_input("Account Name")
            arr = st.number_input("Annual Recurring Revenue (ARR)", min_value=0, value=50000, step=1000)
            renewal_date = st.text_input("Renewal Date", placeholder="YYYY-MM-DD")
            tier = st.selectbox("Customer Tier", ["SMB", "Mid-Market", "Enterprise"])
            
            analyze_btn = st.button("Analyze Ticket", type="primary", use_container_width=True)

    if analyze_btn:
        if not ticket_text:
            st.error("Please enter ticket text to begin analysis.")
            return

        # Prepare context
        customer_data = {
            "account_name": account_name,
            "arr": arr,
            "renewal_date": renewal_date,
            "tier": tier
        }

        # Run Backend Logic
        with st.spinner("Analyzing sentiment and generating strategy..."):
            risk_results = analyze_ticket_risk(ticket_text, customer_data)
            nba_results = generate_next_best_action(ticket_text, risk_results, customer_data)

        st.divider()
        
        # UI Display of Results
        st.header(f"Analysis Results: {account_name}")
        
        # Row 1: High Level Risk & Impact
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Risk Level", risk_results.get("risk_score", "N/A"))
        with m2:
            st.metric("Revenue at Risk", f"${arr:,}")
        with m3:
            st.metric("Escalation Status", risk_results.get("escalation_recommendation", "None"))

        # Main Content Area
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            st.subheader("🔍 Risk Assessment")
            with st.expander("Risk Summary", expanded=True):
                st.write(risk_results.get("summary", "No summary available."))
            
            with st.expander("Key Detected Signals"):
                for signal in risk_results.get("signals", []):
                    st.markdown(f"- {signal}")
            
            with st.expander("Revenue & Impact Details"):
                st.write(risk_results.get("impact_analysis", "N/A"))

        with res_col2:
            st.subheader("🚀 Strategic Response")
            with st.expander("Next Best Actions", expanded=True):
                for action in nba_results.get("actions", []):
                    st.markdown(f"✅ **{action}**")
            
            with st.expander("Stakeholders to Involve"):
                st.write(", ".join(nba_results.get("stakeholders", [])))
            
            with st.expander("Internal Notes"):
                st.info(nba_results.get("internal_notes", ""))

        st.divider()
        
        # Communication Drafts
        st.subheader("📝 Communication Drafts")
        tab1, tab2 = st.tabs(["Executive Reply Draft", "Internal Escalation Brief"])
        
        with tab1:
            st.text_area("Suggested Customer Reply", value=nba_results.get("executive_reply", ""), height=200)
            st.button("Copy to Clipboard", key="copy_exec")
            
        with tab2:
            st.text_area("Internal Context Brief", value=risk_results.get("internal_brief", ""), height=200)

if __name__ == "__main__":
    main()