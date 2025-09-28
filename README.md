<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

# OBSIDIAN-HTTP-MCP

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=default&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=default&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=default&logo=Pytest&logoColor=white" alt="Pytest">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=default&logo=Docker&logoColor=white" alt="Docker">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Poetry-60A5FA.svg?style=default&logo=Poetry&logoColor=white" alt="Poetry">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This is an obsidian MCP server using http transport protocoll. 
The purpose of this server is to provide MCP functionalities for obsidian from a remote server.

**Benefits:**
  - Centrally hosted MCP server for usage with multiple clients 
  - Direct access to Obsidian notes on remote server.
  - Setup fully headless (no Obsidian Rest API)
  - Easily customizable

---

## Features

- [x] Basic obsidian MCP functionalities exist.
- [x] Run http server in a docker container and access it from AI client (Cursor).
- [x] Implementation of user authentication is done.
- [ ] Advanced obsidian MCP functionalities exist.

---

## Project Structure

```sh
└── obsidian-http-mcp/
    ├── Dockerfile
    ├── README.md
    ├── pyproject.toml
    ├── scripts
    │   └── docker_run.sh
    ├── src
    │   └── obsidian_http_mcp
    └── tests
        ├── python_client.py
        └── test_mcp.py
```

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Poetry
- **Container Runtime:** Docker
- **Secrets:** 
  - VAULT_PATH
  - MCP_API_KEY
  - MCP_USER
  

### Installation

Build obsidian-http-mcp from the source and install dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone ../obsidian-http-mcp
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd obsidian-http-mcp
    ```

3. **Install the dependencies:**
	```sh
	❯ poetry install
	```

### Usage

### Server 
Run the sever with:

**Using [docker](https://www.docker.com/):**
```sh
	❯ ./scripts/docker_run.sh
```

### Client 
**Config.json - e.g. Cursor**
 ```json
{
  "mcpServers": {
    "obsidian-http-mcp": {
      "transport": "http",
      "url": "http://localhost:9001/mcp",
      "headers": {
        "Authorization": "Bearer <MCP_API_KEY>"
      }
    }
  }
}
```
 
**Python Client**
See example of testing python client [python-client](#manual-test-client)

### Testing

### Unit tests

Obsidian-http-mcp uses the **pytest** test framework. Run the test suite with:

```sh
  source .venv/bin/activate
  pytest ./tests/test_mcp.py -v
```

### Manual test client

It is possible to test Obsidian-http-mcp using a Python test client.
For authentication it is necessary to save a configuration file **client_config.json** (see #client)

```sh
  source .venv/bin/activate
  tests/python-client.py
```

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL//obsidian-http-mcp/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL//obsidian-http-mcp/issues)**: Submit bugs found or log feature requests for the `obsidian-http-mcp` project.
- **💡 [Submit Pull Requests](https://LOCAL//obsidian-http-mcp/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone ./obsidian-http-mcp
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://LOCAL{//obsidian-http-mcp/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=/obsidian-http-mcp">
   </a>
</p>
</details>

---

## License

Obsidian-http-mcp is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
