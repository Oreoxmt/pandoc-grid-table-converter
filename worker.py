import os
from typing import List


def is_html_table_start(line: str) -> bool:
    return line.strip().startswith("<table>")


def is_html_table_end(line: str) -> bool:
    return line.strip().startswith("</table>")


def is_table_line_start(line: str) -> bool:
    return line.strip().startswith("|")


def is_code_block_start(line: str) -> bool:
    return line.strip().startswith("```")


def is_table_contains_html_tags(table: str) -> bool:
    # Read the table char by char and check if it contains any HTML tags
    # If it encounters `, it's a code block, skip it until the next `
    # If it encounters [, it's a link, skip it until the next )
    in_code = False
    in_link = False
    in_tag = False
    for char in table:
        if char == "\n":
            in_tag = False
            in_link = False
            in_code = False
        if char == "`":
            in_code = not in_code
        if char == "[":
            in_link = True
        if in_link and char == ")":
            in_link = False
        if in_code or in_link:
            continue
        if char == "<":
            in_tag = True
        if char == ">" and in_tag:
            return True
    return False


def process_markdown_file(file_path: str) -> (List[str], List[str]):
    with open(file_path, "r") as file:
        in_html_table = False
        in_md_table = False
        in_code_block = False
        html_tables = []
        md_tables = []
        html_table = ""
        md_table = ""
        for line in file:
            # Skip code blocks
            if is_code_block_start(line):
                in_code_block = not in_code_block
            if in_code_block:
                continue

            if in_html_table:
                html_table += line
                if is_html_table_end(line):
                    in_html_table = False
                    html_tables.append(html_table)
                    html_table = ""
                    # TODO: Convert HTML table to markdown using pandoc
            else:
                if is_html_table_start(line):
                    in_html_table = True
                    html_table += "\n" + line

            if in_md_table:
                md_table += line
                if not is_table_line_start(line):
                    in_md_table = False
                    md_tables.append(md_table)
                    md_table = ""
                    # TODO: Convert table to grid table using pandoc
            else:
                if is_table_line_start(line):
                    in_md_table = True
                    md_table += line

    return html_tables, md_tables


def write_table_to_file(tables: list, file_path: str):
    with open(file_path, "w") as file:
        for table in tables:
            file.write(table)
            file.write("\n")


def main():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    work_dir = f"{curr_dir}/docs-cn"
    IGNORE_DIRS = [".git", ".github", "resources", "media"]
    all_html_tables = []
    all_md_tables = []
    for root, dirs, files in os.walk(work_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith(".md") and file not in ["README.md", "CONTRIBUTING.md", "TOC.md"]:
                file_path = os.path.join(root, file)
                html_tables, md_tables = process_markdown_file(file_path)
                all_html_tables.extend(html_tables)
                all_md_tables.extend(md_tables)
    target_table = []
    for table in all_md_tables:
        if is_table_contains_html_tags(table):
            target_table.append(table)
    write_table_to_file(target_table, f"{curr_dir}/temp/target_table.md")
    write_table_to_file(all_html_tables, f"{curr_dir}/temp/html_tables.html")
    write_table_to_file(all_md_tables, f"{curr_dir}/temp/md_tables.md")


if __name__ == "__main__":
    main()
