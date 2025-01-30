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

st.title('Peace of Mind Calculator')
st.write("Adjust the inputs to see how your savings change. This calculator is based on the NL tax structure from 2025 and assuming a after tax return of €5k/month after the retirement age.")

# User inputs
initial_age = st.number_input("Initial Age", min_value=18, max_value=80, value=38, 
    key="initial_age", help="Your current age", kwargs={"inputmode": "numeric"})
retirement_age = st.number_input("Retirement Age", min_value=30, max_value=80, value=45,
    key="retirement_age", help="Age you plan to retire", kwargs={"inputmode": "numeric"})
initial_investment = st.number_input("Initial Investment (€)", min_value=0, value=90000,
    key="initial_investment", help="Current savings amount", kwargs={"inputmode": "numeric"})
goal_investment = st.number_input("Goal Investment (€)", min_value=0, value=735798,
    key="goal_investment", help="Target savings amount", kwargs={"inputmode": "numeric"})
annual_return = st.slider("Annual Return (%)", min_value=5, max_value=100, value=12) / 100
inflation_rate = st.slider("Inflation Rate (%)", min_value=0, max_value=20, value=3) / 100

# Calculate real rate of return (accounts for inflation)
real_return = (1 + annual_return) / (1 + inflation_rate) - 1

years_to_grow = retirement_age - initial_age

# Adjust goal for inflation
inflation_adjusted_goal = goal_investment * (1 + inflation_rate) ** years_to_grow

# Calculation using real return rate and inflation-adjusted goal
monthly_savings = calculate_monthly_savings(inflation_adjusted_goal, initial_investment, real_return, years_to_grow)

st.write(f"### Inflation-Adjusted Goal: €{inflation_adjusted_goal:,.2f} by the age of {retirement_age}!")
st.write(f"### Monthly Savings Required: €{monthly_savings:,.2f}")

st.write("### Retirement Income Planning")

monthly_income_goal = st.number_input("Monthly After-Tax Income (€)", 
    min_value=0, value=5000, key="monthly_income", 
    help="How much monthly income you want after retirement", 
    kwargs={"inputmode": "numeric"})

with st.expander("Advanced Settings"):
    col1, col2 = st.columns(2)
    with col1:
        withdrawal_rate = st.slider("Safe Withdrawal Rate (%)", 
            min_value=2.5, max_value=5.0, value=4.0, step=0.1,
            help="Lower is more conservative, higher is more aggressive") / 100
        
        has_partner = st.checkbox("Include Partner", value=False,
            help="Tax benefits for fiscal partners")
    
    with col2:
        include_aow = st.checkbox("Include AOW", value=True,
            help="Include Dutch state pension in calculations")
        
        if withdrawal_rate > 0.04:
            st.warning("⚠️ Withdrawal rate above 4% increases the risk of depleting savings during retirement")
        elif withdrawal_rate < 0.035:
            st.info("ℹ️ Conservative withdrawal rate selected - this provides extra safety but requires more savings")

# Dutch AOW amounts (2024)
aow_single = 1452.06  # Monthly AOW for singles
aow_partner = 994.81   # Monthly AOW per person for couples

# Box 3 tax brackets (2024)
def calculate_box3_tax(wealth, has_partner):
    tax_free_amount = 57000 * (2 if has_partner else 1)
    taxable_wealth = max(0, wealth - tax_free_amount)
    
    # 2024 Box 3 brackets and rates
    bracket1_rate = 0.0136  # Up to €100k
    bracket2_rate = 0.0451  # €100k to €1M
    bracket3_rate = 0.0551  # Above €1M
    
    bracket1_limit = 100000
    bracket2_limit = 1000000
    
    if has_partner:
        bracket1_limit *= 2
        bracket2_limit *= 2
    
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

# Calculate monthly AOW benefit
monthly_aow = 0
if include_aow:
    if has_partner:
        monthly_aow = aow_partner * 2
    else:
        monthly_aow = aow_single

# Calculate required capital
annual_income_needed = (monthly_income_goal - monthly_aow) * 12
base_required_capital = annual_income_needed / withdrawal_rate

# Iterate to find the correct capital needed including tax
required_capital = base_required_capital
for _ in range(5):  # Few iterations for convergence
    annual_tax = calculate_box3_tax(required_capital, has_partner)
    required_capital = (annual_income_needed + annual_tax) / withdrawal_rate

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

# Update goal investment for the rest of calculations
goal_investment = required_capital

# Annual tax impact
annual_tax = calculate_box3_tax(required_capital, has_partner)
st.write(f"#### Annual Box 3 Tax: €{annual_tax:,.2f}")

# Warning for high withdrawal rates
if withdrawal_rate > 0.04:
    st.warning("⚠️ Withdrawal rate above 4% increases the risk of depleting savings during retirement")
elif withdrawal_rate < 0.035:
    st.info("ℹ️ Conservative withdrawal rate selected - this provides extra safety but requires more savings")
