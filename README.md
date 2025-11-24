# KCCC QC Report Portal

## Overview
The KCCC QC Report Portal is a Streamlit application designed for the Nuclear Medicine Department's Physics Unit. It facilitates the quality control (QC) reporting process by allowing users to input measured values for various tests, check them against predefined limits, and generate a comprehensive QC report.

## Features
- User-friendly interface for entering QC measurements.
- Automatic evaluation of measurements against defined tolerance limits.
- Generation of detailed QC reports summarizing the results.
- Downloadable report in text format.

## Installation

To run this application, you need to have Python installed on your machine. Follow these steps to set up the project:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/kccc-qc-report-portal.git
   cd kccc-qc-report-portal
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command in your terminal:
```
streamlit run app.py
```

Open your web browser and navigate to `http://localhost:8501` to access the application.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find bugs, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.