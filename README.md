# Setting Up Virtual Environment for Multi-Agent Research Assistant

This guide will walk you through setting up a virtual environment named `multiagentresearchassistantenv` using Python 3.12 on Windows.

## Prerequisites

Make sure you have the following installed before proceeding:

- Python 3.12 (or the specific version you want to use)
- pip (Python's package installer)

## Steps

### 1. Open Command Prompt (cmd)

Open Command Prompt with administrative privileges. This ensures that you can install packages globally.

### 2. Install Virtual Environment (if not already installed)

If you haven't installed `virtualenv` yet, you can install it using pip:

```bash
python -m venv multiagentresearchassistantenv
```

```bash
.\multiagentresearchassistantenv\Scripts\activate
```

### Start the backend

    ```bash
    cd backend
    ```

    ```bash
    flask run
    ```
