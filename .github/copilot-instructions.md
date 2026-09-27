# Project Notes

- This is a Python 3.11+ Streamlit application.
- Keep resume analysis in `app/services`; do not persist submitted resume text.
- Use the SQLite job catalog for role matching and keep it independent of Streamlit.
- OpenAI is optional; preserve the deterministic offline analyzer and mocked tests.
- Run tests with `pytest` from the project root.