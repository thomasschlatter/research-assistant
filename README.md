python -m venv venv

.\venv\Scripts\Activate

Step 1: Locate the R Installation Folder
Find where R is installed on your system. It is usually in:
plaintext
Copy code
C:\Program Files\R\R-x.x.x\bin
Replace x.x.x with your installed version number. For example, it might be R-4.3.1.
Step 2: Add R to the System PATH
On Windows:
Press Win + R, type sysdm.cpl, and press Enter to open the System Properties.
Go to the Advanced tab and click Environment Variables.
Under System variables, find and select the variable named Path, then click Edit.
Add the path to the bin folder of your R installation. For example:
plaintext
Copy code
C:\Program Files\R\R-x.x.x\bin
Click OK to save and close all windows.
Step 3: Verify the Configuration
Open a new Command Prompt.
Type:
plaintext
Copy code
R --version
If configured correctly, it should display the version of R.
Step 4: Optional: Set R_HOME (If Required)
If your application still requires R_HOME, follow these steps:

In the Environment Variables window (as above), create a new System variable:

Variable name: R_HOME
Variable value: The root folder of your R installation, e.g.:
plaintext
Copy code
C:\Program Files\R\R-x.x.x
Click OK and restart your system to apply the changes.

Common Issues
Wrong Path: Double-check that the path to bin is correct.
Restart Needed: If it still doesn't work, restart your computer to apply the environment variable changes.
Let me know if you encounter further issues!
