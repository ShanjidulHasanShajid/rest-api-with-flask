CREATE DATABASE IF NOT EXISTS bookshelf
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bookshelf;

CREATE TABLE IF NOT EXISTS authors (
  id        INT             AUTO_INCREMENT PRIMARY KEY,
  name      VARCHAR(120)    NOT NULL,
  country   VARCHAR(80)     NULL
);

CREATE TABLE IF NOT EXISTS books (
  id                INT             AUTO_INCREMENT PRIMARY KEY,
  title             VARCHAR(200)    NOT NULL,
  published_year    INT             NULL,
  author_id         INT             NOT NULL,
  CONSTRAINT fk_books_author
    FOREIGN KEY (author_id) REFERENCES authors(id)
    ON DELETE CASCADE
);