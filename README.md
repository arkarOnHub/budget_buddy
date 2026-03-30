# Budget Buddy

Budget Buddy is a personal finance management application designed to help you track your expenses, manage your budget, and gain insights into your spending habits. The project is organized with a modular backend (database, models, tools, and agent logic) and a user-friendly UI built with Streamlit.

# Members

Htet Arkar 66011535
Myat Oo Swe 66011644

## Features
- Track and categorize expenses
- Manage budgets
- Analyze spending patterns
- Modular agent and tool architecture
- Streamlit-based user interface

## Project Structure
```
app/
	agent/         # Agent logic and prompts
	tools/         # Budget and expense tools
	ui/            # Streamlit UI
	database.py    # Database setup
	models.py      # Data models
	schemas.py     # Pydantic schemas
init_db.py       # Script to initialize the database
check_models.py  # Script to check models
```

## How to Run

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. Install required packages:

```bash
pip install -r requirements.txt
```

### 2. Initialize the Database
Run the following command to set up the database:

```bash
python init_db.py
```

### 3. Start the Streamlit App
Launch the user interface:

```bash
streamlit run app/ui/streamlit_app.py
```

### 4. (Optional) Run Tests
To run the test scripts:

```bash
python test_agent.py
python test_tools.py
```

## Contributing
Feel free to open issues or submit pull requests to improve Budget Buddy!

## License
This project is licensed under the MIT License.