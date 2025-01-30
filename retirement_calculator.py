import streamlit as st
import numpy as np

def calculate_monthly_savings(goal, current, annual_rate, years):
    months = years * 12
    monthly_rate = (1 + annual_rate) ** (1/12) - 1  # Convert annual return to monthly
    future_value_factor = (1 + monthly_rate) ** months
    needed_per_month = (goal - current * future_value_factor) * (monthly_rate / (future_value_factor - 1))
    return max(0, needed_per_month)

st.title("Retirement (aka "Peace of Mind") Calculator")
st.write("Adjust the inputs to see how your savings change.")

# User inputs
initial_age = st.number_input("Initial Age", min_value=18, max_value=80, value=38)
retirement_age = st.number_input("Retirement Age", min_value=30, max_value=80, value=45)
initial_investment = st.number_input("Initial Investment (€)", min_value=0, value=3000)
goal_investment = st.number_input("Goal Investment (€)", min_value=0, value=735798)
annual_return = st.slider("Annual Return (%)", min_value=5, max_value=100, value=12) / 100

years_to_grow = retirement_age - initial_age

# Calculation
monthly_savings = calculate_monthly_savings(goal_investment, initial_investment, annual_return, years_to_grow)

st.write(f"### Goal: €{goal_investment:,.2f} by the age of {retirement_age}!")

st.write(f"### Monthly Savings Required: €{monthly_savings:,.2f}")
