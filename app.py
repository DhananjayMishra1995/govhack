from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

# Set up your OpenAI API key here
openai.api_key = ''


# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for the products page
@app.route('/products')
def products():
    return render_template('products.html')

# Route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for the signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Helper function to calculate the spending plan dynamically
def calculate_spending_plan(income, fixed_expenses, savings_goal):
    remaining_income = income - fixed_expenses - savings_goal
    
    if remaining_income <= 0:
        return {"error": "Insufficient funds after savings and fixed expenses."}

    # Dynamically calculate the percentage allocation
    groceries_percentage = 0.35  # Example 35% for groceries
    entertainment_percentage = 0.15  # Example 15% for entertainment
    personal_care_percentage = 0.1  # Example 10% for personal care
    transportation_percentage = 0.4  # Example 40% for transportation

    groceries_amount = round(remaining_income * groceries_percentage)
    entertainment_amount = round(remaining_income * entertainment_percentage)
    personal_care_amount = round(remaining_income * personal_care_percentage)
    transportation_amount = round(remaining_income * transportation_percentage)

    breakdown = [
        {"category": "Groceries", "amount": groceries_amount, "percentage": f'{groceries_percentage * 100:.0f}%'},
        {"category": "Entertainment", "amount": entertainment_amount, "percentage": f'{entertainment_percentage * 100:.0f}%'},
        {"category": "Personal Care", "amount": personal_care_amount, "percentage": f'{personal_care_percentage * 100:.0f}%'},
        {"category": "Transportation", "amount": transportation_amount, "percentage": f'{transportation_percentage * 100:.0f}%'}
    ]
    
    return {
        "remaining_income": remaining_income,
        "breakdown": breakdown
    }

# Route to generate the spending plan based on user input
@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    data = request.get_json()

    try:
        # Retrieve user input
        income = int(data['income'])
        fixed_expenses = int(data['fixed_expenses'])
        savings_goal = int(data['savings_goal'])

        # Calculate spending plan
        spending_plan_data = calculate_spending_plan(income, fixed_expenses, savings_goal)
        
        if 'error' in spending_plan_data:
            return jsonify({"error": spending_plan_data['error']})

        # Format the prompt for the OpenAI API
        prompt = f"""
        To determine how to allocate the remaining amount after saving {savings_goal} AUD into different categories, we first need to calculate how much is left after deducting your fixed expenses and savings.

        Weekly income: {income} AUD
        Fixed expenses: {fixed_expenses} AUD
        Amount to save: {savings_goal} AUD

        Total deductions: {fixed_expenses} (fixed expenses) + {savings_goal} (savings) = {fixed_expenses + savings_goal} AUD per week

        Remaining amount: {income} (income) - {fixed_expenses + savings_goal} (deductions) = {spending_plan_data['remaining_income']} AUD

        Here's a suggested allocation into different categories:

        1. Groceries: {spending_plan_data['breakdown'][0]['amount']} AUD – This can cover your weekly grocery shopping.
        2. Entertainment: {spending_plan_data['breakdown'][1]['amount']} AUD – For leisure activities.
        3. Personal Care: {spending_plan_data['breakdown'][2]['amount']} AUD – For grooming and personal expenses.
        4. Transportation: {spending_plan_data['breakdown'][3]['amount']} AUD – For commuting or vehicle-related costs.

        Adjust these allocations based on your preferences and priorities.
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        # Extract the response message
        spending_plan = response['choices'][0]['message']['content']

        return jsonify({
            "spending_plan": spending_plan,
            "breakdown": spending_plan_data['breakdown']
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
