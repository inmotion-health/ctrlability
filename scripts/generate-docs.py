import os
import ast
import subprocess
import re

# Define the directories to search
directories = ["ctrlability/actions", "ctrlability/triggers", "ctrlability/streams", "ctrlability/processors"]


def write_section_as_list(outfile, title, content):
    """
    Writes a section (Inputs or Returns) as a list to the outfile.
    """
    lines = content.strip().split("\n")
    if lines:
        outfile.write(f"#### {title}\n")
        for line in lines:
            # Split the line into name and description
            parts = line.split(":", 1)
            if len(parts) > 1:
                name = parts[0].strip()
                description = parts[1].strip()
                outfile.write(f"- **{name}**: {description}\n")
        outfile.write("\n")


for directory in directories:
    output_file = f"docs/{os.path.basename(directory)}.md"
    with open(output_file, "w") as outfile:
        outfile.write(f"# {os.path.basename(directory).capitalize()}\n\n")

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file)) as f:
                        module = ast.parse(f.read())

                    classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
                    classes.sort(key=lambda x: x.name)

                    for class_ in classes:
                        docstring = ast.get_docstring(class_)
                        if docstring:
                            parts = re.split(r"\n\s*(Args|Inputs|Returns):", docstring, flags=re.IGNORECASE)
                            description = parts[0].strip()
                            outfile.write(f"## {class_.name}\n{description}\n\n")

                            sections = {parts[i].lower(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}

                            if "inputs" in sections:
                                write_section_as_list(outfile, "Inputs", sections["inputs"])

                            if "returns" in sections:
                                write_section_as_list(outfile, "Returns", sections["returns"])

                            if "args" in sections:
                                outfile.write("#### Arguments:\n\n")
                                outfile.write("| Name | Description |\n")
                                outfile.write("| ---- | ----------- |\n")
                                args_lines = sections["args"].strip().split("\n")
                                for line in args_lines:
                                    arg_parts = line.split(":", 1)
                                    if len(arg_parts) > 1:
                                        name = arg_parts[0].strip()
                                        description = arg_parts[1].strip()
                                        outfile.write(f"| {name} | {description} |\n")
                                outfile.write("\n")

    subprocess.run(["markdownlint", output_file, "--fix"])
