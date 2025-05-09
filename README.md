# TeOdioDocker-back
## How to run
 ´´´´docker compose build´´´
 ´´´´docker compose up´´´

## File Structure
├── app  # Contains the main application files.
│   ├── __init__.py   # this file makes "app" a "Python package"
│   ├── main.py       # Initializes the FastAPI application.
│   ├── dependencies.py # Defines dependencies used by the routers
│   ├── routers
│   │   ├── __init__.py
│   │   └── users.py  # Defines routes and endpoints related to cards.
│   ├── crud
│   │   ├── __init__.py
│   │   └── card  # Defines CRUD operations for cards.
│   ├── schemas
│   │   ├── __init__.py
│   │   └── card  # Defines schemas for cards.
│   ├── models
│   │   ├── __init__.py
│   │   └── card  # Defines database models for cards.
│   ├── external_services
│   │   ├── __init__.py
│   │   ├── email.py          # Defines functions for sending emails.
│   │   └── notification.py   # Defines functions for sending notifications
│   └── utils
│       ├── __init__.py
│       ├── authentication.py  # Defines functions for authentication.
│       └── validation.py      # Defines functions for validation.
├── tests
│   ├── __init__.py
│   ├── test_main.py
│   └── test_cards.py  # Tests for the cards module.
├── requirements.txt
├── .gitignore
└── README.md