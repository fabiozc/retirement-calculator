import streamlit as st
import numpy as np

# Set wide layout mode
st.set_page_config(
    page_title='Dutch Financial Freedom Calculator',
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initial values
INITIAL_AGE = 30
TARGET_AGE = 50
MONTHLY_INCOME_GOAL = 5000
INITIAL_PORTFOLIO = 50000
ANNUAL_RETURN = 12  # in percentage
INFLATION_RATE = 3  # in percentage

# Initialize calculation variables
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
        initial_age = st.number_input("Current Age", min_value=18, max_value=80, value=INITIAL_AGE,
            help="Your current age", kwargs={"inputmode": "numeric"})
    with col2:
        target_age = st.number_input("Target Freedom Age", min_value=30, max_value=80, value=TARGET_AGE,
            help="Age when you want to achieve financial freedom", kwargs={"inputmode": "numeric"})
    
    if target_age <= initial_age:
        st.error("⚠️ Target age must be greater than your current age")
        st.stop()
    
    years_to_freedom = target_age - initial_age
    st.info(f"🕒 Time to financial freedom: **{years_to_freedom} years**")
    
    st.markdown("---")  # Separator
    st.markdown("### 💶 Income & Investments")
    
    monthly_income_goal = st.number_input("Monthly After-Tax Income Goal (€)",
        min_value=0, value=MONTHLY_INCOME_GOAL,
        help="How much monthly income you want your investments to generate",
        kwargs={"inputmode": "numeric"})
    
    st.info("""
        💡 This is the monthly income you want your investments to generate,
        giving you the freedom to work because you want to, not because you have to.
    """)
    
    initial_investment = st.number_input("Current Investment Portfolio (€)",
        min_value=0, value=INITIAL_PORTFOLIO,
        help="Your current investment portfolio value",
        kwargs={"inputmode": "numeric"})
    
    # Annual return slider and info block
    annual_return = st.slider(
        "Annual Return (%)", 
        min_value=5, 
        max_value=100, 
        value=ANNUAL_RETURN
    ) / 100
    
    # Dynamic info block based on selected return
    if annual_return <= 0.07:
        st.info("""
            📊 Conservative Return (5-7%)
            Typical investments: Government bonds, high-grade corporate bonds
            • Very low risk
            • Stable but lower returns
            • May not keep up with inflation
        """)
    elif annual_return <= 0.09:
        st.info("""
            📈 Low-Moderate Return (7-9%)
            Typical investments: Mixed portfolio (bonds + some stocks)
            • Low to moderate risk
            • More stable than pure stocks
            • Historical returns above inflation
        """)
    elif annual_return <= 0.11:
        st.info("""
            📈 Moderate Return (9-11%)
            Typical investments: Stock market index funds
            • Moderate risk
            • Similar to S&P 500 historical returns
            • Expect significant fluctuations
        """)
    elif annual_return <= 0.15:
        st.warning("""
            ⚠️ High Return (11-15%)
            Typical investments: Growth stock portfolio
            • High risk
            • Large market fluctuations
            • Requires long time horizon
        """)
    elif annual_return <= 0.25:
        st.warning("""
            ⚠️ Very High Return (15-25%)
            Typical investments: Aggressive growth stocks, high-risk startups
            • Very high risk
            • Extreme market volatility
            • Significant chance of losses
            • Not sustainable long-term
        """)
    elif annual_return <= 0.50:
        st.error("""
            🚨 Speculative Return (25-50%)
            Typical investments: Early-stage crypto, penny stocks, venture capital
            • Extremely high risk
            • Massive volatility
            • High probability of significant losses
            • More similar to gambling than investing
            • Not suitable for retirement planning
        """)
    else:
        st.error("""
            🚨 Ultra-Speculative Return (>50%)
            Typical investments: New cryptocurrencies, high-leverage trading
            • Maximum risk level
            • Extreme volatility (can lose everything)
            • Similar to lottery odds
            • Not considered investing
            • Absolutely not suitable for retirement planning
        """)

    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("---")
        inflation_rate = st.slider("Inflation Rate (%)", min_value=0, max_value=20, value=INFLATION_RATE) / 100
        
        # Calculate break-even rate for reference
        real_return = (1 + annual_return) / (1 + inflation_rate) - 1
        break_even_rate = real_return
        
        st.markdown("##### Withdrawal Strategy")
        st.markdown("Select how much you plan to withdraw annually once you've reached your target investment portfolio:")
        
        # Add S&P 500 historical rate (approximately 10.2% annualized return for past 15 years)
        SP500_HISTORICAL = 0.102
        SP500_YEARS = 15  # Make it a constant for easy updates

        withdrawal_strategy = st.radio(
            "Choose your future withdrawal strategy",
            options=["Match Annual Return", f"S&P 500 Historical ({SP500_YEARS}y)", "Conservative", "Moderate", "Aggressive", "Custom"],
            index=0,
            help="""
            These rates determine how much you can safely withdraw each year after reaching your investment goal:
            Match Annual Return: Matches your real investment return (after inflation)
            S&P 500 Historical: Based on S&P 500 average return over past 15 years (~10.2%)
            Conservative (3%): Very safe withdrawal rate, high probability of growing capital
            Moderate (4%): Classic safe withdrawal rate, historically proven sustainable
            Aggressive (5%): Higher withdrawals, some risk to capital over time
            Custom: Set your own rate
            """
        )
        
        if withdrawal_strategy == "Match Annual Return":
            withdrawal_rate = real_return
            st.info(f"📊 {real_return*100:.1f}% - Matching your real investment return (after inflation) to preserve capital value")
        elif withdrawal_strategy == "S&P 500 Historical":
            withdrawal_rate = SP500_HISTORICAL
            st.info(f"""
                📈 {SP500_HISTORICAL*100:.1f}% - Based on S&P 500 historical performance ({SP500_YEARS} years: 2009-2023)
                
                Note: This rate:
                • Is before inflation adjustment
                • Doesn't account for market volatility
                • Past performance doesn't guarantee future returns
                • Might be too aggressive for stable retirement income
                • Period includes exceptional bull market years
            """)
        elif withdrawal_strategy == "Conservative":
            withdrawal_rate = 0.03
            st.info("""
                📊 3% - Very safe withdrawal rate
                
                • High probability of maintaining or growing capital
                • Accounts for market downturns
                • Provides buffer against inflation
                • Common choice for early retirement
            """)
        elif withdrawal_strategy == "Moderate":
            withdrawal_rate = 0.04
            st.info("""
                📈 4% - Classic 'safe withdrawal rate'
                
                • Based on extensive historical research (Trinity study)
                • 95% success rate over 30-year periods
                • Accounts for inflation adjustments
                • Balance between income and preservation
            """)
        elif withdrawal_strategy == "Aggressive":
            withdrawal_rate = 0.05
            st.warning("""
                ⚠️ 5% - Higher withdrawal rate
                
                • May deplete capital in poor market conditions
                • Less buffer against high inflation
                • Requires more active portfolio management
                • Consider reducing in market downturns
            """)
        else:  # Custom
            withdrawal_rate = st.slider(
                "Future Annual Withdrawal Rate (%)", 
                min_value=2.0, 
                max_value=20.0, 
                value=4.0, 
                step=0.1,
                help="Choose the percentage you'll withdraw annually after reaching your investment goal"
            ) / 100
            
            if withdrawal_rate > real_return:
                st.warning(f"""
                    ⚠️ Once you reach your goal, a rate above {real_return*100:.1f}% (real return) will gradually deplete capital
                    
                    Consider:
                    • Market volatility risk
                    • Inflation impact
                    • Longevity of your portfolio
                    • Having a flexible withdrawal strategy
                """)
            elif withdrawal_rate < real_return:
                st.info("""
                    ℹ️ This rate will allow your capital to grow in real terms after reaching your goal
                    
                    Benefits:
                    • Growing portfolio over time
                    • Better protection against inflation
                    • More buffer for market downturns
                    • Possibility to increase withdrawals later
                """)
        
        st.info(f"""
        💡 Based on your inputs:
        - Annual Return: {annual_return*100:.1f}%
        - Inflation: {inflation_rate*100:.1f}%
        - Real Return: {real_return*100:.1f}%
        - Selected Future Withdrawal Rate: {withdrawal_rate*100:.1f}%
        """)
        
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

    # Calculate monthly pre-tax income
    monthly_pre_tax = (required_capital * withdrawal_rate) / 12

# Right column - Analysis
with right_col:
    st.markdown("### 📊 Financial Freedom Analysis")
    
    # Main required amount
    st.markdown(f"#### Target: €{monthly_income_goal:,.2f}/month from Age {target_age}")
    st.metric(
        label="Required Investment Portfolio",
        value=f"€{required_capital:,.2f}",
        help="Includes Box 3 wealth tax buffer"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
    
    # Monthly investment needed
    st.metric(
        label="Required Monthly Investment",
        value=f"€{monthly_savings:,.2f}/month",
        help="Monthly investment needed to reach your freedom goal"
    )
    
    # Additional details in expander
    with st.expander("View Details"):
        st.markdown("##### Target Monthly Income")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Desired Income", f"€{monthly_income_goal:,.2f}")
        with col2:
            if include_aow:
                st.metric("From Investments", f"€{(monthly_income_goal - monthly_aow):,.2f}")
        
        st.markdown("##### Portfolio Breakdown")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Base Portfolio", f"€{base_required_capital:,.2f}")
        with col2:
            st.metric("Tax Buffer", f"€{tax_buffer:,.2f}")
        
        st.markdown("##### Key Assumptions")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Annual Return", f"{annual_return*100:.1f}%")
        with col2:
            st.metric("Inflation Rate", f"{inflation_rate*100:.1f}%")
        with col3:
            st.metric("Real Return", f"{real_return*100:.1f}%")
        
        st.markdown("##### Withdrawal Strategy")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Withdrawal Rate", f"{withdrawal_rate*100:.1f}%")
        with col2:
            st.metric("Break-even Rate", f"{break_even_rate*100:.1f}%")
        
        if include_aow:
            st.markdown("##### AOW Details")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Monthly AOW", f"€{monthly_aow:,.2f}")
            with col2:
                st.metric("Partner Included", "Yes" if has_partner else "No")

    # Validation section
    st.markdown("---")
    st.markdown("### Income Verification")
    st.markdown(f"This investment portfolio would generate €{monthly_pre_tax:.2f}/month before tax")
    st.markdown(f"After annual Box 3 tax of €{annual_tax:.2f}, effective monthly income: €{monthly_income_goal:.2f}")
    
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

# Footer disclaimer
st.markdown("<br><br><br>", unsafe_allow_html=True)  # Add some space
st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)  # Add some space
st.caption("""
    ⚠️ This calculator is for educational and illustrative purposes only. It provides a simplified simulation based on the inputs and assumptions you provide. 
    Not financial advice: The information presented here does not constitute financial advice, investment advice, trading advice, or any other sort of advice. 
    The calculations and projections are approximations and may not reflect real-world outcomes. Tax calculations are simplified and may not account for all regulations or future changes. 
    Do your own research: Before making any financial decisions, consult with qualified financial advisors, tax professionals, and legal experts. 
    Investment returns are not guaranteed, and past performance does not indicate future results. The actual results may vary significantly from these projections. 
    By using this calculator, you acknowledge that any decisions you make based on this information are at your own risk.
""")
