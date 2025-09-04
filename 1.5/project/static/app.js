// static/app.js
document.addEventListener('DOMContentLoaded', () => {
  const booksList = document.getElementById('booksList');
  const bookForm = document.getElementById('bookForm');
  const titleInput = document.getElementById('title');
  const authorInput = document.getElementById('author');

  const API_URL = '/api/books';

  // Завантажити всі книги
  async function loadBooks() {
    try {
      booksList.innerHTML = '<li><span>Завантаження...</span></li>';
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error('Помилка завантаження');
      const books = await res.json();
      renderBooks(books);
    } catch (err) {
      booksList.innerHTML = `<li><span style="color:#c00">Не вдалося завантажити список книг</span></li>`;
      console.error(err);
    }
  }

  // Відобразити книги у списку
  function renderBooks(books) {
    if (!books.length) {
      booksList.innerHTML = '<li><span>Поки що книг немає</span></li>';
      return;
    }

    booksList.innerHTML = '';
    books.forEach(({ book_id, title, author }) => {
      const li = document.createElement('li');

      const span = document.createElement('span');
      span.textContent = `#${book_id} — "${title}" (${author})`;

      const btn = document.createElement('button');
      btn.className = 'delete-btn';
      btn.textContent = 'Видалити';
      btn.addEventListener('click', () => deleteBook(book_id));

      li.appendChild(span);
      li.appendChild(btn);
      booksList.appendChild(li);
    });
  }

  // Додати книгу
  async function addBook(title, author) {
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, author })
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Не вдалося додати книгу');
      }
      await loadBooks();
    } catch (err) {
      alert(err.message || 'Сталася помилка під час додавання книги');
      console.error(err);
    }
  }

  // Видалити книгу
  async function deleteBook(bookId) {
    if (!confirm(`Видалити книгу з ID ${bookId}?`)) return;
    try {
      const res = await fetch(`${API_URL}/${bookId}`, { method: 'DELETE' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Не вдалося видалити книгу');
      }
      await loadBooks();
    } catch (err) {
      alert(err.message || 'Сталася помилка під час видалення книги');
      console.error(err);
    }
  }

  // Обробник форми
  bookForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = titleInput.value.trim();
    const author = authorInput.value.trim();
    if (!title || !author) {
      alert('Будь ласка, заповніть поля Назва та Автор');
      return;
    }
    await addBook(title, author);
    bookForm.reset();
    titleInput.focus();
  });

  // Перший рендер
  loadBooks();
});
