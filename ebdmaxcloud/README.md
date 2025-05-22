# ebdmaxcloud Project

## Overview
The ebdmaxcloud project is a Flask-based web application designed to manage and visualize order data. It follows the Model-View-Controller (MVC) architectural pattern, allowing for easy expansion and maintenance.

## Project Structure
```
ebdmaxcloud
├── app
│   ├── __init__.py          # Initializes the Flask application and sets up the context
│   ├── models
│   │   └── pedido.py        # Defines the Pedido model for order data
│   ├── views
│   │   └── dashboard.py      # Contains view functions for the dashboard
│   ├── controllers
│   │   └── pedido_controller.py # Handles requests related to orders
│   ├── templates
│   │   └── dashboard.html    # HTML template for the dashboard view
│   └── static                # Directory for static files (CSS, JS, images)
├── config.py                 # Configuration settings for the application
├── requirements.txt          # Lists project dependencies
├── run.py                    # Entry point for running the application
└── README.md                 # Documentation for the project
```

## Setup Instructions
1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd ebdmaxcloud
   ```

2. **Create a Virtual Environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```
   python run.py
   ```

5. **Access the Dashboard**
   Open your web browser and navigate to `http://127.0.0.1:5000/` to access the dashboard.

## Usage
- The dashboard allows users to filter and visualize order data based on specified date ranges.
- The application is designed to be extensible, allowing for the addition of new features and screens as needed.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.