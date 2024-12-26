# Scientific Writer Assistant

Automating the Research Process

## Prerequisites

Before running the project, ensure you have the following software installed:

- Python 3.8 or later
- R (Tested with R 4.x.x)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # On Windows
   .\venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

The following environment variables must be set to use the software:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `R_HOME`: The root folder of your R installation (e.g., `C:\Program Files\R\R-x.x.x`).
- `TAVILY_API_KEY`: Your Tavily API key.
- `OSF_API_TOKEN` Your Open Science Framework API Token

### Setting Environment Variables

#### On Windows:

1. Press `Win + R`, type `sysdm.cpl`, and press Enter.
2. Navigate to the `Advanced` tab and click `Environment Variables`.
3. Under `System variables`, click `New` and add the required variables:
   - Variable name: `OPENAI_API_KEY`
     Variable value: Your OpenAI API key.
   - Variable name: `R_HOME`
     Variable value: Path to your R installation (e.g., `C:\Program Files\R\R-x.x.x`).
   - Variable name: `TAVILY_API_KEY`
     Variable value: Your Tavily API key.
4. Click OK to save and close.

#### On macOS/Linux:

1. Open a terminal and edit your shell configuration file (e.g., `.bashrc`, `.zshrc`):
   ```bash
   nano ~/.bashrc  # or ~/.zshrc
   ```
2. Add the following lines:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   export R_HOME="/path/to/your/R"
   export TAVILY_API_KEY="your_tavily_api_key"
   ```
3. Save the file and apply the changes:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

## Usage

1. Create the virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   ```bash
   # On Windows
   .\venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. change the VENV_PATH in constants

4. Run the main script:
   ```bash
   python main.py
   ```

## When done creating the paper, use pandoc to convert the markdown file to a pdf file

```bash
pandoc -s -o tmp/write_up/final_paper.pdf tmp/write_up/final_paper.md

pandoc --citeproc -s -o paper.pdf paper.md --bibliography citations.bib
```

## Common Issues

### Missing Dependencies

Ensure you have installed all dependencies using the `requirements.txt` file.

### Environment Variables Not Set

Double-check that all required environment variables are properly set.

### R Configuration

Ensure the `R_HOME` variable points to the correct R installation folder.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
