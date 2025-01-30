import streamlit as st
import numpy as np

def calculate_monthly_savings(goal, current, annual_rate, years):
    if annual_rate <= -1:  # Handle extreme negative real returns
        return (goal - current) / (years * 12)
    months = years * 12
    monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Convert annual return to monthly
    future_value_factor = (1 + monthly_rate) ** months
    needed_per_month = (goal - current * future_value_factor) * (monthly_rate / (future_value_factor - 1))
    return max(0, needed_per_month)

st.title('Retirement (aka "Peace of Mind") Calculator')

# Basic inputs that everyone needs to see
initial_age = st.number_input("Initial Age", min_value=18, max_value=80, value=38, 
    key="initial_age", help="Your current age", kwargs={"inputmode": "numeric"})
retirement_age = st.number_input("Retirement Age", min_value=30, max_value=80, value=45,
    key="retirement_age", help="Age you plan to retire", kwargs={"inputmode": "numeric"})
monthly_income_goal = st.number_input("Monthly After-Tax Income Goal (€)", 
    min_value=0, value=5000, key="monthly_income", 
    help="How much monthly income you want after retirement", 
    kwargs={"inputmode": "numeric"})
initial_investment = st.number_input("Initial Investment (€)", min_value=0, value=90000,
    key="initial_investment", help="Current savings amount", kwargs={"inputmode": "numeric"})
annual_return = st.slider("Annual Return (%)", min_value=5, max_value=100, value=12) / 100

# Define AOW amounts first
aow_single = 1452.06  # Monthly AOW for singles
aow_partner = 994.81   # Monthly AOW per person for couples

# Advanced settings in expander
with st.expander("Advanced Settings"):
    col1, col2 = st.columns(2)
    with col1:
        inflation_rate = st.slider("Inflation Rate (%)", min_value=0, max_value=20, value=2) / 100
        
        st.write("##### Withdrawal Rate")
        use_custom_withdrawal = st.checkbox("Customize withdrawal rate", 
            help="Default is 4% (Trinity study safe withdrawal rate)")
        
        if use_custom_withdrawal:
            withdrawal_rate = st.slider("Annual Withdrawal Rate (%)", 
                min_value=2.5, max_value=8.0, value=4.0, step=0.1,
                help="Higher rates increase risk of depleting savings") / 100
            
            if withdrawal_rate > 0.04:
                st.warning("⚠️ Rates above 4% significantly increase the risk of depleting savings during retirement")
            elif withdrawal_rate < 0.035:
                st.info("ℹ️ Conservative rate selected - requires more savings but provides extra safety")
        else:
            withdrawal_rate = 0.04  # Default 4% safe withdrawal rate
            st.info("Using standard 4% safe withdrawal rate")
    
    with col2:
        has_partner = st.checkbox("Include Partner", value=False,
            help="Tax benefits for fiscal partners")
        include_aow = st.checkbox("Include AOW", value=True,
            help="Include Dutch state pension in calculations")
    
    st.markdown("""
    #### About AOW (Dutch State Pension)
    AOW is the Dutch state pension, a basic income provided by the government when you reach retirement age:
    - Single person: €1,452.06/month
    - With partner: €994.81/month per person
    
    **Important Notes:**
    - You must have lived/worked in the Netherlands to be eligible
    - Each year not in NL between ages 15-67 reduces AOW by 2%
    - These amounts are based on 2024 rates and may change
    - The retirement age is gradually increasing (currently 67 years)
    """)

# Calculate monthly AOW benefit
monthly_aow = 0
if include_aow:
    if has_partner:
        monthly_aow = aow_partner * 2
    else:
        monthly_aow = aow_single

# Calculate real return rate
real_return = (1 + annual_return) / (1 + inflation_rate) - 1

# Calculate required capital
annual_income_needed = (monthly_income_goal - monthly_aow) * 12
base_required_capital = annual_income_needed / withdrawal_rate

# Calculate Box 3 tax
def calculate_box3_tax(wealth, has_partner):
    tax_free_amount = 57000 * (2 if has_partner else 1)
    taxable_wealth = max(0, wealth - tax_free_amount)
    
    bracket1_rate = 0.0136
    bracket2_rate = 0.0451
    bracket3_rate = 0.0551
    
    bracket1_limit = 100000 * (2 if has_partner else 1)
    bracket2_limit = 1000000 * (2 if has_partner else 1)
    
    tax = 0
    if taxable_wealth > 0:
        if taxable_wealth <= bracket1_limit:
            tax = taxable_wealth * bracket1_rate
        elif taxable_wealth <= bracket2_limit:
            tax = (bracket1_limit * bracket1_rate +
                  (taxable_wealth - bracket1_limit) * bracket2_rate)
        else:
            tax = (bracket1_limit * bracket1_rate +
                  (bracket2_limit - bracket1_limit) * bracket2_rate +
                  (taxable_wealth - bracket2_limit) * bracket3_rate)
    return tax

# Iterate to find required capital including tax
required_capital = base_required_capital
for _ in range(5):
    annual_tax = calculate_box3_tax(required_capital, has_partner)
    required_capital = (annual_income_needed + annual_tax) / withdrawal_rate

# Set goal investment for monthly savings calculation
goal_investment = required_capital

# Display results
st.write("### Retirement Analysis")
col1, col2 = st.columns(2)

with col1:
    st.write("#### Monthly Income Breakdown")
    st.write(f"Target Income: €{monthly_income_goal:,.2f}")
    if include_aow:
        st.write(f"AOW Benefit: €{monthly_aow:,.2f}")
        st.write(f"Required from Savings: €{(monthly_income_goal - monthly_aow):,.2f}")

with col2:
    st.write("#### Capital Requirements")
    st.write(f"Base Capital: €{base_required_capital:,.2f}")
    st.write(f"Tax Buffer: €{(required_capital - base_required_capital):,.2f}")
    st.write(f"Total Required: €{required_capital:,.2f}")

# Calculate and display monthly savings requirement
years_to_grow = retirement_age - initial_age
monthly_savings = calculate_monthly_savings(goal_investment, initial_investment, real_return, years_to_grow)

st.write("### Summary")
st.write(f"Monthly Savings Required: €{monthly_savings:,.2f}")
st.write(f"Annual Box 3 Tax at Goal: €{annual_tax:,.2f}")
