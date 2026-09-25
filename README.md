# Flask Blog 

A full-stack blog application built with **Flask**, featuring user authentication, blog post creation, editing, deletion, and author-specific content management.

## Features

*  User registration and login
*  User-specific blog posts
*  Create, edit, and delete blog posts
*  View individual blog posts
*  Homepage displaying available posts
*  Form validation using Flask-WTF
*  SQLite database for persistent data storage
*  Custom CSS styling
*  Authentication-protected post management
*  Author pages displaying posts by a specific user

## Tech Stack

### Backend

* **Python**
* **Flask**
* **Flask-SQLAlchemy**
* **Flask-WTF**
* **Flask-Login**

### Frontend

* **HTML5**
* **CSS3**
* **Jinja2 Templates**

### Database

* **SQLite**

## Project Structure

```text
flask-blog-with-users/
│
├── main.py                 # Flask application and routes
├── forms.py                # WTForms definitions and validation
├── seed.py                 # Script for adding demo users and posts
│
├── instance/
│   └── posts.db            # SQLite database
│
├── templates/
│   ├── header.html         # Shared navigation/layout
│   ├── index.html          # Homepage
│   ├── post.html           # Individual post page
│   └── author.html         # Author page
│
├── static/
│   └── css/
│       └── custom.css      # Custom styling
│
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Atreyeee/flask-blog.git
cd flask-blog
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**macOS/Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install flask flask-sqlalchemy flask-wtf flask-login
```

### 4. Seed the database

The project includes a seed script that creates demo users and blog posts.

```bash
python seed.py
```

Example output:

```text
Seeded 3 users and 9 posts.
```

### 5. Run the application

```bash
python main.py
```

Open the application in your browser at:

```text
http://127.0.0.1:5000
```

## Demo Login

A demo account is available for testing:

```text
Email: atreyee@example.com
Password: demo1234
```

## Application Flow

```text
User
 │
 ├── Register / Login
 │
 ├── Browse Blog Posts
 │
 ├── View Individual Post
 │
 ├── View Author
 │
 └── Manage Own Posts
      ├── Create
      ├── Edit
      └── Delete
```

## Authentication

The application uses **Flask-Login** to manage user sessions and restrict authenticated actions.

Users can:

* Register an account
* Log in and log out
* Create posts while authenticated
* Edit their own posts
* Delete their own posts

## Database

The application uses **SQLite** with SQLAlchemy as the ORM.

The database stores information such as:

* User accounts
* Blog posts
* Post authorship
* Post content and metadata

## Future Improvements

Potential extensions include:

* Comments and replies
* Like/bookmark functionality
* Search and filtering
* Pagination
* Rich-text/Markdown editor
* User profile pages
* Image uploads for posts
* Password reset functionality
* REST API endpoints
* Deployment using a production WSGI server

## License

This project is intended for educational and portfolio purposes.
