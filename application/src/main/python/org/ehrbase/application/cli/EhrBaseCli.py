import argparse
import sys
from some_module import CliRunner  # Assuming CliRunner is implemented somewhere

class EhrBaseCli:
    def __init__(self, cli_runner):
        self.cli_runner = cli_runner

    def run(self, args):
        self.cli_runner.run(args)

def build_application(args):
    # Setup the argument parser
    parser = argparse.ArgumentParser(description="EHRbase CLI Application")
    # Add arguments and options here as needed
    parser.add_argument('--some-option', help='An example option')

    # Parse the arguments
    parsed_args = parser.parse_args(args)
    
    # Initialize the CLI runner
    cli_runner = CliRunner()  # Initialize as needed
    return EhrBaseCli(cli_runner), parsed_args

if __name__ == "__main__":
    cli, args = build_application(sys.argv[1:])
    cli.run(args)
