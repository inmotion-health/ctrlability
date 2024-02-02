import os
import ast
import subprocess
import re

# Define the directories to search
directories = ["ctrlability/actions", "ctrlability/triggers", "ctrlability/streams", "ctrlability/processors"]

for directory in directories:
    # Open the output file
    output_file = f"docs/{os.path.basename(directory)}.md"
    with open(f"docs/{os.path.basename(directory)}.md", "w") as outfile:
        # Write the title to the output file
        outfile.write(f"# {os.path.basename(directory).upper()}\n\n")

        # Find all Python files in the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    # Open the file and parse it with the ast module
                    with open(os.path.join(root, file)) as f:
                        module = ast.parse(f.read())

                    # Find all classes in the module
                    classes = [node for node in module.body if isinstance(node, ast.ClassDef)]

                    # Write the class names and docstrings to the output file
                    for class_ in classes:
                        docstring = ast.get_docstring(class_)
                        if docstring:
                            outfile.write(f"## {class_.name}\n")

                            # Split the docstring into description and arguments
                            parts = re.split(r"\n\s*Args:", docstring)
                            description = parts[0].strip()
                            outfile.write(f"{description}\n\n")

                            if len(parts) > 1:
                                outfile.write("### Arguments:\n\n")
                                outfile.write("| Name | Description |\n")
                                outfile.write("| ---- | ----------- |\n")

                                # Split the arguments part into lines
                                args_lines = parts[1].strip().split("\n")
                                for line in args_lines:
                                    # Split the line into name and description
                                    arg_parts = line.split(":")
                                    if len(arg_parts) > 1:
                                        name = arg_parts[0].strip()
                                        description = ":".join(arg_parts[1:]).strip()
                                        outfile.write(f"| {name} | {description} |\n")

                            outfile.write("\n")

    # Run markdownlint on the output file
    subprocess.run(["markdownlint", output_file, "--fix"])
