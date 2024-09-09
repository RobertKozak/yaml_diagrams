import sys
import yaml
import traceback
from yaml_to_diagrams import YamlToDiagramsConverter

def main():
    if len(sys.argv) != 3:
        print("Usage: python test.py <input_yaml_file> <output_filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, 'r') as file:
            yaml_content = file.read()

        # Create an instance of YamlToDiagramsConverter
        converter = YamlToDiagramsConverter(yaml_content)

        # Update the output filename in the YAML data
        converter.yaml_data['output_file'] = output_file

        # Generate the diagram
        converter.generate_diagram()

        print(f"Diagram generated and saved as {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in input file. {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
