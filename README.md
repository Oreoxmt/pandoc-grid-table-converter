# Pandoc Grid Table Converter

## Introduction

`pandoc-grid-table-converter` is a tool designed to convert the following tables in Markdown files to Pandoc grid tables:

- Pipe tables

  ```markdown
  | Header 1 | Header 2 |
  | -------- | -------- |
  | Cell 1   | Cell 2   |
  | Cell 3   | Cell 4   |
  ```

- HTML tables

  ```markdown
  <table>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
    <tr>
      <td>Cell 1</td>
      <td>Cell 2</td>
    </tr>
    <tr>
      <td>Cell 3</td>
      <td>Cell 4</td>
    </tr>
  ```

- Pipe tables that contain HTML tags

  ```markdown
  | Header 1 | Header 2 |
  | -------- | -------- |
  | Cell 1   | Line 1<br/>Line 2   |
  | Cell 3   | <ul><li>Item 1</li><li>Item 2</li></ul>   |
  ```

## Features

- Convert pipe tables and HTML tables in Markdown to Pandoc grid tables
- Preserve table alignment and structure

## Installation

### Requirements

- Python 3.7 or later
- Pandoc 3.1 or later

### Steps

1. Clone the repository and change to the directory:

  ```shell
  git clone https://github.com/Oreoxmt/pandoc-grid-table-converter.git
  cd pandoc-grid-table-converter
  ```

2. Configure the `convert_tables.sh` script:

  - `REPO_OWNER`: the GitHub username of the repository owner
  - `REPO_NAME`: the name of the repository
  - `TARGET_BRANCHES`: the branches to convert the tables in the Markdown files
  - `TABLE_FILTER`: controls which pipe tables to convert
    - `"all"`: convert all HTML tables and pipe tables
    - `"html"`: convert only HTML tables and pipe tables containing HTML tags

3. To convert the tables in the Markdown files, run the following command:

  ```bash
  bash convert_tables.sh 
  ```

  This script will create a new branch and commit the changes to that branch.
