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

st.title('Retirement (aka "Peace of Mind") Calculator')

# Create two main columns for the entire app
left_col, right_col = st.columns([1, 1], gap="large")

# Left column - Inputs
with left_col:
    st.write("### Basic Inputs")
    initial_age = st.number_input("Initial Age", min_value=18, max_value=80, value=38, 
        key="initial_age", help="Your current age", kwargs={"inputmode": "numeric"})
    retirement_age = st.number_input("Retirement Age", min_value=30, max_value=80, value=45,
        key="retirement_age", help="Age you plan to retire", kwargs={"inputmode": "numeric"})
    
    st.write("##### Target Retirement Income")
    monthly_income_goal = st.number_input("Monthly After-Tax Income at Retirement (€)", 
        min_value=0, value=5000, key="monthly_income", 
        help="How much monthly income you want AFTER you retire (not needed now)", 
        kwargs={"inputmode": "numeric"})
    
    st.info("💡 This is the income you want to have each month AFTER you retire, "
            f"starting at age {retirement_age}. It's not the amount you need to save monthly now.")
    
    initial_investment = st.number_input("Current Savings (€)", min_value=0, value=90000,
        key="initial_investment", help="How much you have saved already", kwargs={"inputmode": "numeric"})
    annual_return = st.slider("Annual Return (%)", min_value=5, max_value=100, value=12) / 100

    # Advanced settings in expander
    with st.expander("Advanced Settings"):
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
        
        has_partner = st.checkbox("Include Partner", value=False,
            help="Tax benefits for fiscal partners")
        include_aow = st.checkbox("Include AOW", value=False,
            help="Include Dutch state pension in calculations")
        
        if include_aow:
            st.caption("ℹ️ About AOW (Dutch State Pension)")
            st.caption("""
            AOW is the Dutch state pension, providing basic income at retirement age:
            • Single person: €1,452.06/month
            • With partner: €994.81/month per person

            Note: Requires NL residency/work history. Each year not in NL (ages 15-67) reduces AOW by 2%. 
            Amounts shown are 2024 rates. Retirement age is currently 67 years.
            """)

# Right column - Analysis
with right_col:
    st.write("### Retirement Analysis")
    
    # Calculate real return rate (after inflation)
    real_return = (1 + annual_return) / (1 + inflation_rate) - 1

    # Calculate monthly AOW benefit
    monthly_aow = 0
    if include_aow:
        if has_partner:
            monthly_aow = aow_partner * 2
        else:
            monthly_aow = aow_single

    # Calculate required capital
    annual_spending = monthly_income_goal * 12
    annual_aow = monthly_aow * 12
    annual_income_needed_from_savings = annual_spending - annual_aow

    # Base capital calculation using withdrawal rate
    base_required_capital = annual_income_needed_from_savings / withdrawal_rate

    # Calculate final required capital including tax buffer
    required_capital = base_required_capital
    annual_tax = calculate_box3_tax(required_capital, has_partner)
    tax_buffer = annual_tax / withdrawal_rate
    required_capital = base_required_capital + tax_buffer

    # Set goal investment for monthly savings calculation
    goal_investment = required_capital

    # Display results in a single column
    st.write("#### Monthly Income")
    st.write(f"Target Income: €{monthly_income_goal:,.2f}")
    if include_aow:
        st.write(f"AOW Benefit: €{monthly_aow:,.2f}")
        st.write(f"Required from Savings: €{(monthly_income_goal - monthly_aow):,.2f}")

    st.write("#### Capital Needs")
    st.write(f"Base Capital: €{base_required_capital:,.2f}")
    with st.expander("💡 Why this amount?"):
        st.markdown(f"""
        Base Capital calculation:
        - Monthly income goal: €{monthly_income_goal:,.2f}
        - Annual income needed: €{annual_income_needed_from_savings:,.2f}
        - Withdrawal rate: {withdrawal_rate*100:.1f}%
        - Formula: Annual income ÷ Withdrawal rate
        - €{annual_income_needed_from_savings:,.2f} ÷ {withdrawal_rate:.3f} = €{base_required_capital:,.2f}
        
        This is the amount needed to generate your target income using 
        the {withdrawal_rate*100:.1f}% withdrawal rate, before considering taxes.
        """)
    st.write(f"Annual Box 3 Tax: €{annual_tax:,.2f}")
    st.write(f"Tax Buffer: €{tax_buffer:,.2f}")
    st.write(f"Total Required: €{required_capital:,.2f}")

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

    # Validation section
    st.write("#### Validation")
    annual_withdrawal = required_capital * withdrawal_rate
    monthly_withdrawal = annual_withdrawal / 12
    st.write(f"This capital would provide €{monthly_withdrawal:,.2f}/month before tax")
    st.write(f"After annual Box 3 tax of €{annual_tax:,.2f}, effective monthly income: €{(annual_withdrawal - annual_tax)/12:,.2f}")

    # Calculate and display monthly savings requirement
    years_to_grow = retirement_age - initial_age
    monthly_savings = calculate_monthly_savings(goal_investment, initial_investment, real_return, years_to_grow)
    st.write("#### Required Monthly Savings")
    st.write(f"To reach your goal: €{monthly_savings:,.2f}/month")

# Define AOW amounts first
aow_single = 1452.06  # Monthly AOW for singles
aow_partner = 994.81   # Monthly AOW per person for couples
