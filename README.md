# Bookshelf-API

A book-and-author CRUD app I built to learn how a backend actually works: Flask,
MySQL, and a plain HTML/CSS/JS frontend that talks to the API.

This README is my note on **what i learnt** — the flow from the
HTML on the page, to the JavaScript that calls the API, to the Flask route, to
MySQL, and back onto the screen.



---

## Run it

```bash
# MySQL running in XAMPP, copy and run schema.sql to create the database in phpMyAdmin, import bookshelf.sql to the database
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```

---

## How the app is wired

This project uses **both** rendering approaches, and the split between them is
the thing I most wanted to understand.

**SSR — server-side rendering.** The page itself. Flask runs the route, Jinja
builds the HTML, the browser receives finished markup.

```python
# routes/pages.py
@pages.route("/books")
def books_page():
    return render_template("books.html")     # SSR: the page is built on the server
```

The HTML it sends has an **empty** table — headers, no rows.

**CSR — client-side rendering.** The data. Once the page is on screen,
`static/js/app.js` runs, calls the JSON API, and builds the rows in the browser.

```
1. GET /books                → HTML with an empty table      (SSR — Flask + Jinja)
2. GET /static/css/style.css → stylesheet                    (Flask, no route needed)
3. GET /static/js/app.js     → the script                    (Flask, no route needed)
   ── JavaScript starts running ──
4. GET /api/authors          → JSON                          (CSR — fills the dropdown)
5. GET /api/books            → JSON                          (CSR — fills the table)
   ── rows appear ──
```

So: **pages are SSR, data is CSR.** The `/api/...` routes never return HTML, and
the page routes never return data.

### Why the API calls go through one wrapper

Every call needs the same four things: set the method, set the JSON header,
stringify the body, check the status. Writing that out in ten places is how bugs
get in — and the status check is the one everybody forgets, because **`fetch`
does not throw on 400, 404 or 500.** It only throws when the request can't be
made at all, so a 404 sails straight through and gets rendered as if it were
data.

So it's written once:

```javascript
// static/js/app.js
async function api(path, method = "GET", body = null) {
  const options = { method, headers: {} };

  if (body !== null) {
    options.headers["Content-Type"] = "application/json";   // or Flask won't parse the body
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);
  const data = await response.json();

  if (!response.ok) throw new Error(data.error);   // turns a 400/404 into a real exception
  return data;
}
```

Now every caller is one line and can just use `try` / `catch`:

```javascript
const books = await api("/api/books");
await api("/api/books", "POST", payload);
await api(`/api/books/${id}`, "DELETE");
```

If I later add a login token or change the error shape, I change this function
and all ten call sites get it.

---

## GET — read a list and put it on the page

**Flow:** page loads → JS asks the API for JSON → JS builds the table rows.

**1. The empty table Jinja sent** — `templates/books.html`

```html
<tbody id="book-rows">
  <tr class="empty-row"><td colspan="5">No books yet. Add one on the left.</td></tr>
</tbody>
```

That `id` is the handle. The server puts an empty container on the page and the
JavaScript fills it.

**2. The JavaScript that runs after the page loads** — `static/js/app.js`

```javascript
async function refresh() {
  const books = await api("/api/books");
  const tbody = $("book-rows");

  if (books.length === 0) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="5">No books yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = books.map((b) => `
    <tr>
      <td class="num">${esc(b.id)}</td>
      <td class="title-cell">${esc(b.title)}</td>
      <td>${esc(b.author_name || "—")}</td>
      <td class="num">${esc(b.published_year || "—")}</td>
      <td>
        <div class="row-actions">
          <button class="btn btn-row" data-edit="${esc(b.id)}">Edit</button>
          <button class="btn btn-row danger" data-delete="${esc(b.id)}">Delete</button>
        </div>
      </td>
    </tr>
  `).join("");
}
```

What the JS is doing:

- Sends `GET /api/books` through the wrapper and waits for the array.
- Grabs the empty `<tbody id="book-rows">` that Jinja already placed.
- Turns each object into an HTML string, glues them into one string, and assigns
  it to `innerHTML`. Assigning **replaces** the contents, so re-running this can
  never duplicate rows.
- `esc()` escapes user text before it becomes HTML.
- Writes each record's id into `data-edit` / `data-delete` on the buttons. That's
  how a button knows which row it belongs to when it gets clicked later.

**3. The route it hits** — `routes/books.py`

```python
@books_bp.route("", methods=["GET"])          # → GET /api/books
def list_books():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(BOOK_QUERY + " ORDER BY books.id")   # JOIN, so each row carries author_name
        books = cursor.fetchall()
        return jsonify(books), 200            # 200 = fine
    finally:
        cursor.close()
        connection.close()
```

**What the connection and cursor are:**

- `get_connection()` opens a live network connection to MySQL — the phone line.
- `connection.cursor()` is the conversation on that line: the object that sends a
  query and holds the result.
- `cursor.execute(sql, values)` sends it; `fetchall()` returns every row as a
  list, `fetchone()` returns one row or `None`.
- `try` / `finally` so both close even if something throws. Leaked connections
  eventually make MySQL refuse new ones.

**`dictionary=True`** — rows come back as dictionaries instead of tuples:

```python
{"id": 1, "title": "Things Fall Apart", "author_name": "Chinua Achebe"}   # dictionary=True
(1, "Things Fall Apart", "Chinua Achebe")                                 # the default
```

The dictionary version is already the shape `jsonify` needs, so there's no
manual conversion step and no remembering that position 1 is the title.

**`buffered=True`** — the driver pulls the whole result into memory immediately
instead of leaving it on the server to stream. Without it, running a second
`execute()` before the first result is fully read throws
`InternalError: Unread result found` — which is exactly what the update and
delete routes do when they check a record exists and then change it.

**4. What comes back**

```json
[{ "id": 1, "title": "Things Fall Apart", "published_year": 1958,
   "author_id": 1, "author_name": "Chinua Achebe" }]
```

`author_name` isn't a column — it comes from the `JOIN` in `BOOK_QUERY`. The API
returns what the page needs, not a copy of the table.

---

## POST — create from a form

**Flow:** submit → JS cancels the page reload → sends JSON → re-reads the list.

**1. The form** — `templates/books.html`

```html
<form id="book-form" class="form" autocomplete="off">
  <input type="hidden" id="book-id" name="id" value="">

  <input type="text" id="book-title" name="title" required>

  <select id="book-author" name="author_id" required>
    <option value="">Choose an author</option>
  </select>

  <input type="number" id="book-year" name="published_year" min="0" max="2100">

  <button type="submit" class="btn btn-primary" id="book-submit">Save book</button>
</form>
```

Two things to notice. There's **no `action` and no `method`** — the form isn't
meant to be submitted to the server the normal way; JavaScript intercepts it. And
the `<select>` is **empty**: its options are filled in by a separate
`GET /api/authors` call when the page loads, so the dropdown always matches the
authors table.

**2. The JavaScript** — `static/js/app.js`

```javascript
form.addEventListener("submit", async (event) => {
  event.preventDefault();                    // stops the browser's default full-page reload

  const id = $("book-id").value;
  const year = $("book-year").value;
  const payload = {
    title: $("book-title").value.trim(),
    author_id: Number($("book-author").value),
    published_year: year ? Number(year) : null,
  };

  try {
    await api("/api/books", "POST", payload);
    flash("Book added.", "ok");
    resetForm();
    refresh();                               // ask the server for the list again
  } catch (err) {
    flash(err.message);                      // shows the message Flask put in {"error": ...}
  }
});
```

What the JS is doing:

- Cancels the form's built-in submit, which would otherwise reload the whole page
  and throw away the response.
- Reads each input's `.value` — always a string, even on `type="number"` — and
  builds one object.
- Hands it to `api()`, which stringifies it into the request body and sets the
  JSON content type.
- On success: clears the form and calls `refresh()`. It re-reads from the server
  rather than guessing what the table should now contain.
- On failure: the message written in Python ends up in the red banner.

**3. The route** — `routes/books.py`

```python
@books_bp.route("", methods=["POST"])         # → POST /api/books
def create_book():
    data = request.get_json(silent=True) or {}          # the JSON body the browser sent

    values, error = read_book_payload(data)
    if error:
        return jsonify({"error": error}), 400           # 400 = the client's data was wrong

    title, year, author_id = values

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "That author does not exist."}), 400

        cursor.execute(
            "INSERT INTO books (title, published_year, author_id) VALUES (%s, %s, %s)",
            (title, year, author_id),                   # %s placeholders — never f-strings, or it's SQL injection
        )
        connection.commit()                             # without this the row never actually saves

        cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (cursor.lastrowid,))
        return jsonify(cursor.fetchone()), 201          # 201 = a new record exists now
    finally:
        cursor.close()
        connection.close()
```

`request.get_json()` is where a JSON body lands. (`request.form` is for HTML form
posts, `request.args` for `?query=strings`.) The browser's `required` attribute is
a convenience — anyone can curl this URL, so the real check is the one in Python.

---

## PUT — update an existing record

**Flow:** Edit button → fetch that one record → fill the form → submit sends PUT.

**1. The button** — generated by the GET render, in `static/js/app.js`

```html
<button class="btn btn-row" data-edit="3">Edit</button>
```

Plus the hidden input that already sits in the form:

```html
<input type="hidden" id="book-id" name="id" value="">
```

**2. Clicking Edit** — `static/js/app.js`

```javascript
const book = await api(`/api/books/${editId}`);

$("book-id").value = book.id;                          // hidden field, invisible to the user
$("book-title").value = book.title || "";
$("book-author").value = book.author_id || "";
$("book-year").value = book.published_year || "";

$("book-form-title").textContent = `Edit book #${book.id}`;
$("book-submit").textContent = "Update book";
$("book-cancel").hidden = false;
```

What the JS is doing: requests the one record by id and writes its values back
into the same inputs, so "edit" is the create form in a different mode rather
than a separate screen. The id goes into the hidden field, and the button label
changes so the user can see which mode they're in.

**3. The single-record route** — `routes/books.py`

```python
@books_bp.route("/<int:book_id>", methods=["GET"])     # → GET /api/books/3
def get_book(book_id):
    ...
    cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
    book = cursor.fetchone()
    if book is None:
        return jsonify({"error": "Book not found."}), 404    # 404 = no such record
    return jsonify(book), 200
```

`<int:book_id>` makes that part of the URL a variable, only matches digits, and
arrives as a real `int` in the parameter of the same name.

**4. Submitting** — the same handler as POST, branching on the hidden field

```javascript
if (id) {
  await api(`/api/books/${id}`, "PUT", payload);     // has an id → update
} else {
  await api("/api/books", "POST", payload);          // no id → create
}
```

One form, two endpoints, decided by whether that hidden input holds a value.

**5. The route** — `routes/books.py`

```python
@books_bp.route("/<int:book_id>", methods=["PUT"])     # → PUT /api/books/3
def update_book(book_id):
    data = request.get_json(silent=True) or {}
    values, error = read_book_payload(data)
    if error:
        return jsonify({"error": error}), 400

    title, year, author_id = values
    ...
    cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
    if cursor.fetchone() is None:
        return jsonify({"error": "Book not found."}), 404     # UPDATE on a missing row isn't an SQL error

    cursor.execute(
        "UPDATE books SET title = %s, published_year = %s, author_id = %s WHERE id = %s",
        (title, year, author_id, book_id),                    # the WHERE, or every book changes
    )
    connection.commit()

    cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
    return jsonify(cursor.fetchone()), 200
```

Four `%s`, four values, in the order they appear in the SQL — `book_id` last
because the `WHERE` is last.

---

## DELETE — remove a record

**Flow:** Delete button → confirm → send DELETE → re-read the list.

**1. The button** — generated by the GET render

```html
<button class="btn btn-row danger" data-delete="3">Delete</button>
```

**2. The JavaScript** — `static/js/app.js`

```javascript
$("book-rows").addEventListener("click", async (event) => {
  const deleteId = event.target.dataset.delete;        // reads data-delete="3"
  if (!deleteId) return;

  if (!confirm(`Delete book #${deleteId}?`)) return;

  try {
    await api(`/api/books/${deleteId}`, "DELETE");     // no body — the id is in the URL
    flash("Book deleted.", "ok");
    refresh();
  } catch (err) {
    flash(err.message);
  }
});
```

What the JS is doing:

- The listener sits on the `<tbody>`, not on the buttons. The buttons are created
  by `innerHTML` and replaced on every refresh, so a listener attached directly
  to a button would die the next time the table redraws. Clicks bubble up to the
  container, which never gets replaced.
- `event.target.dataset.delete` reads the id back off whichever button was
  clicked — the same id written into the row during the GET render.
- Clicking a cell instead of a button leaves `deleteId` undefined, so nothing
  happens.

**3. The route** — `routes/books.py`

```python
@books_bp.route("/<int:book_id>", methods=["DELETE"])  # → DELETE /api/books/3
def delete_book(book_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        connection.commit()
        if cursor.rowcount == 0:                       # nothing matched that id
            return jsonify({"error": "Book not found."}), 404
        return jsonify({"message": "Book deleted."}), 200
    finally:
        cursor.close()
        connection.close()
```

`cursor.rowcount` is how many rows the statement actually affected, so it tells
me whether that book existed without a separate `SELECT`.

Deleting an **author** works the same way at `/api/authors/<id>`, and MySQL
removes their books too — the foreign key is declared `ON DELETE CASCADE`, so one
statement changes two tables.

---

## What I took away

- The frontend and backend are two separate programs. The only things crossing
  between them are a URL, a method, a status code, and JSON field names.
- `GET`/`POST`/`PUT`/`DELETE` on two URLs (`/api/books` and `/api/books/<id>`)
  cover every operation. The verb carries the action, not the URL.
- Pages can be server-rendered while the data inside them is client-rendered, in
  the same app.
- After any change: re-read from the server and redraw. Never patch the table by
  hand to match what I think happened.
- `commit()` or the write silently doesn't happen. `%s` placeholders or it's SQL
  injection. `WHERE` or the whole table changes.
- `dictionary=True` so rows are already JSON-shaped; `buffered=True` so a second
  query on the same cursor doesn't blow up.
- `fetch` doesn't throw on 400/404/500 — the status has to be checked by hand,
  which is why a consistent error shape `{"error": "..."}` is worth deciding up
  front.
- Validation in the browser is a convenience. The check in Python is the real one.

---

## Layout

```
app.py               creates the app, registers the blueprints
db.py                get_connection()
config.py            MySQL credentials
schema.sql           the two tables
routes/pages.py      SSR pages:  /  /authors  /books
routes/books.py      JSON API:   /api/books
routes/authors.py    JSON API:   /api/authors
templates/           Jinja: base, index, authors, books
static/js/app.js     fetch + render — the API client
static/css/          styling (served by Flask automatically, no route)
```