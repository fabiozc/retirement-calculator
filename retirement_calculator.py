import streamlit as st
import numpy as np

def calculate_monthly_savings(goal, current, annual_rate, years):
    months = years * 12
    monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Convert annual return to monthly
    future_value_factor = (1 + monthly_rate) ** months
    needed_per_month = (goal - current * future_value_factor) * (monthly_rate / (future_value_factor - 1))
    return max(0, needed_per_month)

st.title('Peace of Mind Calculator')
st.write("Adjust the inputs to see how your savings change.")

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
inflation_rate = st.slider("Inflation Rate (%)", min_value=0, max_value=10, value=3) / 100

# Calculate real rate of return (accounts for inflation)
real_return = (1 + annual_return) / (1 + inflation_rate) - 1

years_to_grow = retirement_age - initial_age

# Adjust goal for inflation
inflation_adjusted_goal = goal_investment * (1 + inflation_rate) ** years_to_grow

# Calculation using real return rate and inflation-adjusted goal
monthly_savings = calculate_monthly_savings(inflation_adjusted_goal, initial_investment, real_return, years_to_grow)

st.write(f"### Inflation-Adjusted Goal: €{inflation_adjusted_goal:,.2f} by the age of {retirement_age}!")
st.write(f"### Monthly Savings Required: €{monthly_savings:,.2f}")
