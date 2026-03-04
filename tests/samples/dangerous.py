"""Dangerous Python code for testing."""
import os
import subprocess


def delete_everything():
    """DANGEROUS: This would delete files."""
    os.system("rm -rf /")


def run_command(cmd):
    """DANGEROUS: This executes arbitrary commands."""
    subprocess.run(cmd, shell=True)


def execute_code(code):
    """DANGEROUS: This executes arbitrary Python code."""
    eval(code)


if __name__ == "__main__":
    delete_everything()
    run_command("ls -la")
    execute_code("print('hello')")
