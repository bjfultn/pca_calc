# PCA Class Calculator

A web application for calculating PCA (Porsche Club of America) classing for autocross vehicles. The application helps users determine their car's class based on various modifications and specifications.

## Features

- Calculate base points based on vehicle specifications (weight, horsepower, wheel width)
- Track tire modifications and their point values
- Track performance upgrades and their point values
- Automatically determine class based on total points
- User management for multiple vehicles
- Competition view for comparing vehicles

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pca_calc.git
cd pca_calc
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Register an account
2. Add your vehicle(s) to your garage
3. Enter vehicle specifications
4. Add tire and upgrade information
5. View your calculated class and points

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
