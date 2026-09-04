/* ==========================================================================
   Bookshelf — browser code
   This file is the *client* of your API. It never touches MySQL; it only
   sends HTTP requests to the endpoints you are going to write in Flask.
   You don't need to edit anything here.
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. A tiny wrapper around fetch()
   Every request goes through here, so all the error handling lives in one
   place. `method` is the HTTP verb: GET, POST, PUT or DELETE.
   -------------------------------------------------------------------------- */
async function api(path, method = "GET", body = null) {
  const options = { method, headers: {} };

  if (body !== null) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);

  // Read the body as text first: if the endpoint doesn't exist yet, Flask
  // sends back an HTML error page, not JSON, and JSON.parse would explode.
  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      throw new Error(
        `${method} ${path} → ${response.status}. The server did not return JSON. ` +
        `Have you written this endpoint yet?`
      );
    }
  }

  if (!response.ok) {
    const detail = (data && (data.error || data.message)) || response.statusText;
    throw new Error(`${method} ${path} → ${response.status}: ${detail}`);
  }

  return data;
}

/* --------------------------------------------------------------------------
   2. Small helpers
   -------------------------------------------------------------------------- */
const $ = (id) => document.getElementById(id);

function flash(message, kind = "error") {
  const box = $("flash");
  if (!box) return;
  box.textContent = message;
  box.className = "flash " + (kind === "ok" ? "is-ok" : "is-error");
  box.hidden = false;
  if (kind === "ok") setTimeout(() => { box.hidden = true; }, 2500);
}

function clearFlash() {
  const box = $("flash");
  if (box) box.hidden = true;
}

// Escapes text before putting it in the page, so a book titled
// "<script>" can never run as code.
function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function markActiveNav(page) {
  const map = { home: "home", authors: "authors", books: "books" };
  const link = document.querySelector(`.nav-link[data-nav="${map[page]}"]`);
  if (link) link.classList.add("is-active");
}

/* --------------------------------------------------------------------------
   3. Overview page
   Needs: GET /api/authors, GET /api/books
   -------------------------------------------------------------------------- */
async function initHome() {
  try {
    const [authors, books] = await Promise.all([
      api("/api/authors"),
      api("/api/books"),
    ]);

    $("stat-authors").textContent = authors.length;
    $("stat-books").textContent = books.length;

    const recent = books.slice(-5).reverse();
    const tbody = $("recent-books");

    if (recent.length === 0) {
      tbody.innerHTML = `<tr class="empty-row"><td colspan="3">No books yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = recent.map((book) => `
      <tr>
        <td class="title-cell">${esc(book.title)}</td>
        <td>${esc(book.author_name || "—")}</td>
        <td class="num">${esc(book.published_year || "—")}</td>
      </tr>
    `).join("");
  } catch (err) {
    flash(err.message);
  }
}

/* --------------------------------------------------------------------------
   4. Authors page
   Needs: GET/POST /api/authors, PUT/DELETE /api/authors/<id>
   -------------------------------------------------------------------------- */
async function initAuthors() {
  const form = $("author-form");

  async function refresh() {
    const tbody = $("author-rows");
    try {
      const authors = await api("/api/authors");
      $("author-count").textContent = `${authors.length} total`;

      if (authors.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="4">No authors yet. Add one on the left.</td></tr>`;
        return;
      }

      tbody.innerHTML = authors.map((a) => `
        <tr>
          <td class="num">${esc(a.id)}</td>
          <td class="title-cell">${esc(a.name)}</td>
          <td>${esc(a.country || "—")}</td>
          <td>
            <div class="row-actions">
              <button class="btn btn-row" data-edit="${esc(a.id)}">Edit</button>
              <button class="btn btn-row danger" data-delete="${esc(a.id)}">Delete</button>
            </div>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      flash(err.message);
      tbody.innerHTML = `<tr class="empty-row"><td colspan="4">Could not load authors.</td></tr>`;
    }
  }

  function resetForm() {
    form.reset();
    $("author-id").value = "";
    $("author-form-title").textContent = "Add an author";
    $("author-submit").textContent = "Save author";
    $("author-cancel").hidden = true;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFlash();

    const id = $("author-id").value;
    const payload = {
      name: $("author-name").value.trim(),
      country: $("author-country").value.trim(),
    };

    try {
      if (id) {
        await api(`/api/authors/${id}`, "PUT", payload);
        flash("Author updated.", "ok");
      } else {
        await api("/api/authors", "POST", payload);
        flash("Author added.", "ok");
      }
      resetForm();
      refresh();
    } catch (err) {
      flash(err.message);
    }
  });

  $("author-cancel").addEventListener("click", resetForm);

  $("author-rows").addEventListener("click", async (event) => {
    const editId = event.target.dataset.edit;
    const deleteId = event.target.dataset.delete;

    if (editId) {
      clearFlash();
      try {
        const author = await api(`/api/authors/${editId}`);
        $("author-id").value = author.id;
        $("author-name").value = author.name || "";
        $("author-country").value = author.country || "";
        $("author-form-title").textContent = `Edit author #${author.id}`;
        $("author-submit").textContent = "Update author";
        $("author-cancel").hidden = false;
        window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (err) {
        flash(err.message);
      }
    }

    if (deleteId) {
      if (!confirm(`Delete author #${deleteId}? Their books may be removed too.`)) return;
      clearFlash();
      try {
        await api(`/api/authors/${deleteId}`, "DELETE");
        flash("Author deleted.", "ok");
        resetForm();
        refresh();
      } catch (err) {
        flash(err.message);
      }
    }
  });

  refresh();
}

/* --------------------------------------------------------------------------
   5. Books page
   Needs: GET/POST /api/books, PUT/DELETE /api/books/<id>, GET /api/authors
   -------------------------------------------------------------------------- */
async function initBooks() {
  const form = $("book-form");

  async function loadAuthorOptions() {
    const select = $("book-author");
    try {
      const authors = await api("/api/authors");
      select.innerHTML = `<option value="">Choose an author</option>` +
        authors.map((a) => `<option value="${esc(a.id)}">${esc(a.name)}</option>`).join("");
      $("book-author-hint").hidden = authors.length > 0;
    } catch (err) {
      flash(err.message);
    }
  }

  async function refresh() {
    const tbody = $("book-rows");
    try {
      const books = await api("/api/books");
      $("book-count").textContent = `${books.length} total`;

      if (books.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="5">No books yet. Add one on the left.</td></tr>`;
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
    } catch (err) {
      flash(err.message);
      tbody.innerHTML = `<tr class="empty-row"><td colspan="5">Could not load books.</td></tr>`;
    }
  }

  function resetForm() {
    form.reset();
    $("book-id").value = "";
    $("book-form-title").textContent = "Add a book";
    $("book-submit").textContent = "Save book";
    $("book-cancel").hidden = true;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFlash();

    const id = $("book-id").value;
    const year = $("book-year").value;
    const payload = {
      title: $("book-title").value.trim(),
      author_id: Number($("book-author").value),
      published_year: year ? Number(year) : null,
    };

    try {
      if (id) {
        await api(`/api/books/${id}`, "PUT", payload);
        flash("Book updated.", "ok");
      } else {
        await api("/api/books", "POST", payload);
        flash("Book added.", "ok");
      }
      resetForm();
      refresh();
    } catch (err) {
      flash(err.message);
    }
  });

  $("book-cancel").addEventListener("click", resetForm);

  $("book-rows").addEventListener("click", async (event) => {
    const editId = event.target.dataset.edit;
    const deleteId = event.target.dataset.delete;

    if (editId) {
      clearFlash();
      try {
        const book = await api(`/api/books/${editId}`);
        $("book-id").value = book.id;
        $("book-title").value = book.title || "";
        $("book-author").value = book.author_id || "";
        $("book-year").value = book.published_year || "";
        $("book-form-title").textContent = `Edit book #${book.id}`;
        $("book-submit").textContent = "Update book";
        $("book-cancel").hidden = false;
        window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (err) {
        flash(err.message);
      }
    }

    if (deleteId) {
      if (!confirm(`Delete book #${deleteId}?`)) return;
      clearFlash();
      try {
        await api(`/api/books/${deleteId}`, "DELETE");
        flash("Book deleted.", "ok");
        resetForm();
        refresh();
      } catch (err) {
        flash(err.message);
      }
    }
  });

  loadAuthorOptions();
  refresh();
}

/* --------------------------------------------------------------------------
   6. Start the right page
   -------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  markActiveNav(page);

  if (page === "home") initHome();
  if (page === "authors") initAuthors();
  if (page === "books") initBooks();
});
