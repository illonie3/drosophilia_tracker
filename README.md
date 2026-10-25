# Semi-Automated Drosophila Tracker

A Python and OpenCV-based image analysis tool designed to automatically track the trajectory of a Drosophila (fruit fly) moving inside a transparent tube. The project includes a user-friendly GUI (built with Tkinter) to streamline the analysis process in a laboratory environment.

##  Features

* **Dynamic Background Generation:** Automatically reconstructs a "clean" background without the fly by calculating the median across the image sequence.

* **Interactive ROI Selection:** Allows you to draw a Region of Interest (ROI) around the tube, ensuring the algorithm ignores external reflections or background movement.

* **Robust Automated Tracking:** Utilizes background subtraction, contrast thresholding, and morphological filtering to isolate and track the fly.

* **Manual Fallback Mode:** If the algorithm loses the fly on a specific frame, a window automatically opens allowing you to manually pinpoint the fly's location with a simple mouse click.

* **Data Export:** Generates a `trajectoire_drosophile.csv` file containing the X/Y coordinates and creates a `verification` folder with the generated background and fully annotated images.

##  Prerequisites

You will need to install the following dependencies:

```
pip install opencv-python numpy

```

## Project Structure

* `interface.py`: The entry point of the application. It provides the GUI and launches the analysis in an isolated process to prevent UI freezing or conflicts with OpenCV.

* `pointage_vf.py`: The core scientific script that handles the computer vision processing, manual fallback logic, and CSV data export.

## Usage

1. Run the interface script from your terminal:

   ```
   python interface.py
   
   ```

2. A window will appear. Select the folder containing your image sequence. *(Note: The script expects images named `Image_Record*_Data1.png`, but you can adjust the regex pattern in `pointage_vf.py` if needed).*

3. Adjust the contrast threshold if necessary (default is `40`).

4. Click **LANCER L'ANALYSE** (Launch Analysis).

5. A window will pop up asking you to select the tube. Draw a rectangle around the inside of the tube using your mouse, then press `SPACE` or `ENTER` to confirm.

6. Let the program run. If it loses the fly, it will prompt you to click on it.

7. Once finished, a summary popup will appear, and your CSV/images will be ready in the target folder.

## 🖱️ Creating a Windows Desktop Shortcut (Anaconda)

For daily laboratory use, it is highly recommended to create a desktop shortcut that automatically activates your Anaconda environment and launches the UI.

1. In your project folder, create a new text file and name it `Launch_Tracker.bat`.

2. Open it in a text editor and paste the following code. **Make sure to replace the paths** with your actual installation and project paths:

```
@echo off
:: Activate the Anaconda virtual environment (replace paths and env name)
call C:\Users\YourUsername\Anaconda3\Scripts\activate.bat your_conda_env_name

:: Navigate to the project directory
cd /d "C:\Path\To\Your\Project\Folder"

:: Launch the graphical interface
python "interface.py"

```

3. Save the `.bat` file.

4. Right-click the `Launch_Tracker.bat` file and select **Send to > Desktop (create shortcut)**.

5. *(Optional)* Go to your desktop, right-click the new shortcut, select **Properties > Change Icon...**, and choose a custom `.ico` file to make it look like a real desktop application!
