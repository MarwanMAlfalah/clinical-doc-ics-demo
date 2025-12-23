import os
import sys

def main():
    # Ensure project root is in PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Run Streamlit app
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", "app/ui/main.py"]
    stcli.main()

if __name__ == "__main__":
    main()
