# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands
- Run app: `streamlit run app.py`
- Install dependencies: `pip install -r requirements.txt`
- Create conda environment: `conda env create -f environment.yaml`
- Activate conda environment: `conda activate settlement-app`

## Code Style Guidelines
- **Imports**: Group imports by standard library, third-party, then local modules
- **Naming**: Use snake_case for variables/functions, UPPER_SNAKE_CASE for constants
- **Error handling**: Use try/except blocks for database operations with informative messages
- **Type hints**: Add type hints to function parameters and return values
- **Documentation**: Add docstrings to functions explaining purpose, parameters, and return values
- **Streamlit**: Follow Streamlit best practices for UI components and layout
- **Database**: Use parameterized queries to prevent SQL injection

## Project Structure
- `app.py`: Main Streamlit application entry point
- `config.py`: Configuration settings and constants
- `utils/`: Helper functions and utility modules
- `.streamlit/`: Streamlit configuration and secrets