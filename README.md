python -m venv venv

.\venv\Scripts\Activate

# Kaggle API Setup

Place your kaggle.json credentials file in:

- Windows: C:\Users\<YOUR-USER>\.kaggle\kaggle.json
- Linux/Mac: ~/.kaggle/kaggle.json

You can download kaggle.json from your Kaggle account settings at https://www.kaggle.com/settings

# Setting Up the OSF API Key

This project uses the OSF API, which requires an API key for authentication. Follow the steps below to set up the `OSF_API_TOKEN` on your system and retrieve it using Python.

---

## Prerequisites

1. Ensure you have Python installed (3.6 or later).
2. Ensure your operating system has the ability to set environment variables.

---

## Step 1: Obtain Your OSF API Key

1. Log in to your [OSF account](https://osf.io/).
2. Navigate to the **API Keys** section under your account settings.
3. Generate a new API key and copy it.

---

## Step 2: Set the API Key as an Environment Variable

### Windows (PowerShell)

1. Open PowerShell.
2. Run the following command, replacing `<YOUR_API_TOKEN>` with your actual OSF API key:

   ````powershell
   [Environment]::SetEnvironmentVariable("YOUR_API_TOKEN", "<YOUR_API_TOKEN>", "User")```
   ````
