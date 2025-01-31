import streamlit as st
import numpy as np

# Set wide layout mode
st.set_page_config(
    page_title='Dutch Financial Freedom Calculator',
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize variables at the start
has_partner = False
include_aow = False
monthly_aow = 0
withdrawal_rate = 0
real_return = 0
break_even_rate = 0

# Title section with gradient background
st.markdown("""
    <div style="
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        ">
        <h1 style="color: white; margin: 0;">Dutch Financial Freedom Calculator</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">
            Plan your path to financial independence in the Netherlands 🇳🇱<br>
            Calculate how much capital you need to generate your desired income by your target age.
        </p>
    </div>
""", unsafe_allow_html=True)

def calculate_monthly_savings(goal, current, annual_rate, years):
    if annual_rate <= -1:  # Handle extreme negative real returns
        return (goal - current) / (years * 12)
    months = years * 12
    monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Convert annual return to monthly
    future_value_factor = (1 + monthly_rate) ** months
    needed_per_month = (goal - current * future_value_factor) * (monthly_rate / (future_value_factor - 1))
    return max(0, needed_per_month)

# Define tax calculation function at the top
def calculate_box3_tax(wealth, has_partner):
    # Tax-free threshold
    tax_free_amount = 57000 * (2 if has_partner else 1)
    taxable_wealth = max(0, wealth - tax_free_amount)
    
    # 2024 Box 3 brackets and rates
    # Bracket 1: up to €100k (€200k for partners): 6.04% return taxed at 32% = 1.93%
    # Bracket 2: €100k to €1M: 5.53% return taxed at 32% = 1.77%
    # Bracket 3: above €1M: 5.80% return taxed at 32% = 1.86%
    
    bracket1_limit = 100000 * (2 if has_partner else 1)
    bracket2_limit = 1000000 * (2 if has_partner else 1)
    
    # Effective tax rates per bracket
    bracket1_rate = 0.0193  # 6.04% * 32%
    bracket2_rate = 0.0177  # 5.53% * 32%
    bracket3_rate = 0.0186  # 5.80% * 32%
    
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

# Define AOW constants (2024 rates)
aow_single = 1452.06  # Monthly AOW for singles
aow_partner = 994.81   # Monthly AOW per person for couples

# Create two main columns
left_col, right_col = st.columns([1, 1], gap="large")

# Left column - Inputs
with left_col:
    st.markdown("### 🎯 Your Goals")
    
    col1, col2 = st.columns(2)
    with col1:
        initial_age = st.number_input("Current Age", min_value=18, max_value=80, value=38,
            help="Your current age", kwargs={"inputmode": "numeric"})
    with col2:
        target_age = st.number_input("Target Freedom Age", min_value=30, max_value=80, value=45,
            help="Age when you want to achieve financial freedom", kwargs={"inputmode": "numeric"})
    
    if target_age <= initial_age:
        st.error("⚠️ Target age must be greater than your current age")
        st.stop()
    
    years_to_freedom = target_age - initial_age
    st.info(f"🕒 Time to financial freedom: **{years_to_freedom} years**")
    
    st.markdown("---")  # Separator
    st.markdown("### 💶 Income & Investments")
    
    monthly_income_goal = st.number_input("Monthly After-Tax Income Goal (€)",
        min_value=0, value=5000,
        help="How much monthly income you want your investments to generate",
        kwargs={"inputmode": "numeric"})
    
    st.info("""
        💡 This is the monthly income you want your investments to generate,
        giving you the freedom to work because you want to, not because you have to.
    """)
    
    initial_investment = st.number_input("Current Investment Portfolio (€)",
        min_value=0, value=90000,
        help="Your current investment portfolio value",
        kwargs={"inputmode": "numeric"})
    
    annual_return = st.slider("Annual Return (%)", min_value=5, max_value=100, value=12) / 100

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        inflation_rate = st.slider("Inflation Rate (%)", min_value=0, max_value=20, value=3) / 100
        
        # Calculate break-even withdrawal rate
        real_return = (1 + annual_return) / (1 + inflation_rate) - 1
        break_even_rate = real_return
        withdrawal_rate = break_even_rate
        
        has_partner = st.checkbox("Include Partner", value=False)
        include_aow = st.checkbox("Include AOW", value=False)

    # Calculate AOW benefit
    if include_aow:
        if has_partner:
            monthly_aow = aow_partner * 2
        else:
            monthly_aow = aow_single

    # Calculate required capital
    annual_spending = monthly_income_goal * 12
    annual_aow = monthly_aow * 12
    annual_income_needed_from_savings = annual_spending - annual_aow
    base_required_capital = annual_income_needed_from_savings / withdrawal_rate if withdrawal_rate > 0 else 0

    # Calculate tax and total required
    annual_tax = calculate_box3_tax(base_required_capital, has_partner)
    tax_buffer = annual_tax / withdrawal_rate if withdrawal_rate > 0 else 0
    required_capital = base_required_capital + tax_buffer

    # Calculate monthly savings needed
    years_to_grow = target_age - initial_age
    monthly_savings = calculate_monthly_savings(required_capital, initial_investment, real_return, years_to_grow)

# Right column - Analysis
with right_col:
    st.markdown("### 📊 Financial Freedom Analysis")
    
    # Monthly Income section
    st.markdown("#### Monthly Income")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Target Income", f"€{monthly_income_goal:,.2f}")
    with col2:
        if include_aow:
            st.metric("Required from Investments", f"€{(monthly_income_goal - monthly_aow):,.2f}")
    
    # Portfolio Needs section
    st.markdown("#### Investment Portfolio Needs")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Base Portfolio", f"€{base_required_capital:,.2f}")
    with col2:
        st.metric("Total Required", f"€{required_capital:,.2f}")
    
    st.markdown("---")  # Separator
    
    # Monthly Investment section
    st.markdown("#### Required Monthly Investment")
    st.metric("To reach your freedom goal", f"€{monthly_savings:,.2f}/month")

    st.markdown("---")  # Separator

    # Validation section
    st.write("#### Validation")
    annual_withdrawal = required_capital * withdrawal_rate
    monthly_withdrawal = annual_withdrawal / 12
    st.write(f"This capital would provide €{monthly_withdrawal:,.2f}/month before tax")
    st.write(f"After annual Box 3 tax of €{annual_tax:,.2f}, effective monthly income: €{(annual_withdrawal - annual_tax)/12:,.2f}")
    
    with st.expander("💡 Understanding Tax Buffer"):
        st.markdown("""
        The tax buffer accounts for Dutch Box 3 wealth tax (2024 rates):
        
        - First €57k is tax-free (€114k for partners)
        - Up to €100k: 6.04% assumed return, taxed at 32% = 1.93% effective rate
        - €100k to €1M: 5.53% assumed return, taxed at 32% = 1.77% effective rate
        - Above €1M: 5.80% assumed return, taxed at 32% = 1.86% effective rate
        
        The tax buffer is additional capital needed to generate income to pay this tax 
        while maintaining your target monthly income.
        """)
