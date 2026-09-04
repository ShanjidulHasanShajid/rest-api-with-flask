# Bookshelf — Flask + REST API practice project

The purpose of this project was to learn REST Api through Flask and learn about data validation techniques before running any queries. 

## Folder map

```
bookshelf-api/
├── app.py              ← Flask app + startup
├── config.py           ← DB credentials.
├── db.py               ← MySQL connection.
├── schema.sql          ← CREATE TABLE statements.
├── requirements.txt    
├── routes/
│   ├── __init__.py     
│   ├── pages.py        ← Routes that show the HTML pages.
│   ├── authors.py      ← /api/authors endpoints.
│   └── books.py        ← /api/books endpoints.
├── static/
│   ├── css/style.css   
│   └── js/app.js       
└── templates/
    ├── base.html       
    ├── index.html      
    ├── authors.html   
    └── books.html      
```

## Setup

1. Start **Apache** and **MySQL** in the XAMPP control panel.
2. import the bookshelf.sql Database to XAMPP
3. Open a terminal in this folder and create a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   source venv/bin/activate       # macOS / Linux
   pip install -r requirements.txt
   pyhton app.py                  #will start the webapp
   ```



### Authors

| Method | URL                  | Sends                    | Returns              |
|--------|----------------------|--------------------------|----------------------|
| GET    | `/api/authors`       | —                        | list of authors      |
| GET    | `/api/authors/<id>`  | —                        | one author           |
| POST   | `/api/authors`       | `{name, country}`        | the created author   |
| PUT    | `/api/authors/<id>`  | `{name, country}`        | the updated author   |
| DELETE | `/api/authors/<id>`  | —                        | `{message: "..."}`   |

An author looks like:

```json
{ "id": 1, "name": "Chinua Achebe", "country": "Nigeria" }
```

### Books

| Method | URL                | Sends                                   | Returns            |
|--------|--------------------|-----------------------------------------|--------------------|
| GET    | `/api/books`       | —                                       | list of books      |
| GET    | `/api/books/<id>`  | —                                       | one book           |
| POST   | `/api/books`       | `{title, author_id, published_year}`    | the created book   |
| PUT    | `/api/books/<id>`  | `{title, author_id, published_year}`    | the updated book   |
| DELETE | `/api/books/<id>`  | —                                       | `{message: "..."}` |

A book looks like:

```json
{
  "id": 1,
  "title": "Things Fall Apart",
  "published_year": 1958,
  "author_id": 1,
  "author_name": "Chinua Achebe"
}
```

`author_name` is not a column — it comes from a JOIN with the authors table.
The list pages use it so they don't have to make a second request per row.

### Pages (plain HTML, not API)

| Method | URL        | Renders          |
|--------|------------|------------------|
| GET    | `/`        | `index.html`     |
| GET    | `/authors` | `authors.html`   |
| GET    | `/books`   | `books.html`     |
