"""Entry point for sus-py when run as a module."""
import sys

if __name__ == "__main__":
    # Import here to avoid circular imports
    from sus_py.cli import app

    # Ensure typer receives the correct arguments
    # When running as 'python -m sus_py', sys.argv[0] is the module path
    # We need to ensure typer gets the arguments correctly
    app()
