import os
import re
import subprocess


def get_indent(line: str) -> int:
    indent = 0
    for ch in line:
        if ch == " ":
            indent += 1
        else:
            break
    return indent


def is_table_contains_html_tags(table: list[str]) -> bool:
    # Read the table char by char and check if it contains any HTML tags
    # If it encounters `, it's a code block, skip it until the next `
    for line in table:
        in_code = False
        in_link = False
        in_tag = False
        for char in line:
            # Skip new line characters
            if char == "\n":
                continue
            # Skip code blocks
            if char == "`":
                in_code = not in_code
            if in_code:
                continue
            # Check for HTML tags
            if char == "<":
                in_tag = True
            if in_tag and char == ">":
                return True
    return False


def convert_html_table(table: list[str]) -> list[str]:
    p = subprocess.Popen(
        [
            "pandoc",
            "--from=html",
            "--to=markdown-smart+hard_line_breaks+grid_tables-pipe_tables-simple_tables-multiline_tables",
            "--wrap=none",
            "--lua-filter=remove-attr.lua",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    for line in table:
        p.stdin.write(line)
    p.stdin.close()
    temp_result = [line for line in p.stdout]
    p.wait()
    result = []
    for line in temp_result:
        line_process_bullet = re.sub(r"\|( +)-( ){3}(\S(.*?))\|", "|\\1- \\3  |", line)
        result.append(line_process_bullet)
    return result


def convert_md_table(table: list[str]) -> list[str]:
    if len(table) == 0:
        return []
    indent = get_indent(table[0])
    p = subprocess.Popen(
        [
            "pandoc",
            "--from=gfm+pipe_tables",
            "--to=html",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    for line in table:
        if get_indent(line) != indent:
            raise RuntimeError("Indentation mismatch")
        p.stdin.write(line[indent:])
    p.stdin.close()
    result = [
        f"{' ' * indent}{line}"
        for line in convert_html_table([line for line in p.stdout])
    ]
    p.wait()
    return result


def process_markdown_file(file_path: str, table_filter: str | None = None):
    out_lines: list[str] = []
    with open(file_path, "r") as file:
        in_html_table = False
        in_md_table = False
        in_code_block = False
        last_stripped_line = ""
        html_table = []
        md_table = []
        for line in file:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
            if in_code_block:
                out_lines.append(line)
            elif in_html_table:
                if stripped.startswith("</table>"):
                    html_table.append(line)
                    out_lines.extend(convert_html_table(html_table))
                    in_html_table = False
                    html_table = []
                else:
                    html_table.append(line)
            elif in_md_table:
                if not stripped.startswith("|"):
                    if table_filter != "html" or (table_filter == "html" and is_table_contains_html_tags(md_table)):
                        out_lines.extend(convert_md_table(md_table))
                    else:
                        out_lines.extend(md_table)
                    out_lines.append(line)
                    in_md_table = False
                    md_table = []
                else:
                    md_table.append(line)
            elif stripped.startswith("<table>"):
                in_html_table = True
                html_table.append(line)
            elif stripped.startswith("|") and last_stripped_line == "":
                in_md_table = True
                md_table.append(line)
            else:
                out_lines.append(line)
            last_stripped_line = stripped
        if in_html_table:
            raise AssertionError("in_html_table should always be false")
        if in_md_table:
            if table_filter != "html" or (table_filter == "html" and is_table_contains_html_tags(md_table)):
                out_lines.extend(convert_md_table(md_table))
            else:
                out_lines.extend(md_table)
    with open(file_path, "w") as file:
        for line in out_lines:
            file.write(line)


def merge_grid_table_cells(file_path: str):
    out_lines: list[str] = []
    with open(file_path, "r") as file:
        in_grid_table = False
        in_code_block = False
        last_line = ""
        last_stripped_line = ""
        for line in file:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
            if in_code_block:
                out_lines.append(last_line)
            elif in_grid_table:
                empty_first_cell = re.match(r"^\|( )+\|", stripped)
                if empty_first_cell is not None:
                    pattern = r"^(\s*)\+(-+)\+"
                    match_last_line = re.match(pattern, last_line)
                    if match_last_line is not None:
                        row_width = len(match_last_line.group(2))
                        last_line = re.sub(
                            pattern, rf"\1+{' ' * row_width}+", last_line
                        )
                out_lines.append(last_line)
                if not stripped.startswith("+") and not stripped.startswith("|"):
                    in_grid_table = False
            elif stripped.startswith("+-") and last_stripped_line == "":
                in_grid_table = True
                out_lines.append(last_line)
            else:
                out_lines.append(last_line)
            last_line = line
            last_stripped_line = stripped
        out_lines.append(last_line)
    with open(file_path, "w") as file:
        for line in out_lines:
            file.write(line)


def main():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = f"{curr_dir}/docs-cn"
    ignore_dirs = [".git", ".github", "resources", "media"]
    ignore_files = ["README.md", "CONTRIBUTING.md", "TOC.md"]
    for root, dirs, files in os.walk(work_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith(".md") and file not in ignore_files:
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}")
                process_markdown_file(file_path, "html")
                merge_grid_table_cells(file_path)


if __name__ == "__main__":
    main()
