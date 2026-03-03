import json, os
from datetime import date

DATA_FILE = "library_data.json"


class Book:
    def __init__(self, book_id, title, author, genre, year):
        self.book_id    = book_id
        self.title      = title
        self.author     = author
        self.genre      = genre
        self.year       = year
        self.is_issued  = False
        self.issued_to  = None
        self.issue_date = None

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d):
        b = cls(d["book_id"], d["title"], d["author"], d["genre"], d["year"])
        b.is_issued  = d["is_issued"]
        b.issued_to  = d["issued_to"]
        b.issue_date = d["issue_date"]
        return b

    def __str__(self):
        status = f"Issued to {self.issued_to}" if self.is_issued else "Available"
        return f"[{self.book_id}] {self.title} | {self.author} | {self.genre} | {self.year} | {status}"


class Library:
    def __init__(self):
        self.books = {}   # HashMap: { book_id → Book }
        self.counter = 1

    def _next_id(self):
        i = f"B{self.counter:03d}"
        self.counter += 1
        return i

    def add(self, title, author, genre, year):
        b = Book(self._next_id(), title, author, genre, year)
        self.books[b.book_id] = b
        print(f"✅ Added: [{b.book_id}] {b.title}")

    def search(self, query, by="title"):
        q = query.lower()
        results = [b for b in self.books.values() if q in getattr(b, by).lower()]
        if results:
            for b in results: print(b)
        else:
            print("❌ No books found.")

    def issue(self, book_id, person):
        b = self.books.get(book_id)
        if not b:               return print("❌ Book not found.")
        if b.is_issued:         return print(f"⚠️  Already issued to {b.issued_to}.")
        b.is_issued, b.issued_to, b.issue_date = True, person, str(date.today())
        print(f"✅ '{b.title}' issued to {person}.")

    def return_book(self, book_id):
        b = self.books.get(book_id)
        if not b:           return print("❌ Book not found.")
        if not b.is_issued: return print("⚠️  Book is not issued.")
        b.is_issued, b.issued_to, b.issue_date = False, None, None
        print(f"✅ '{b.title}' returned successfully.")

    def display(self):
        if not self.books: return print("📭 No books in library.")
        for b in self.books.values(): print(b)

    def report(self):
        all_b  = list(self.books.values())
        issued = [b for b in all_b if b.is_issued]
        print(f"\n📊 Total: {len(all_b)} | Available: {len(all_b)-len(issued)} | Issued: {len(issued)}")
        genres = {}
        for b in all_b: genres[b.genre] = genres.get(b.genre, 0) + 1
        print("📁 Genres:", ", ".join(f"{g}({c})" for g, c in genres.items()))
        if issued:
            print("📤 Issued Books:")
            for b in issued: print(f"   {b.title} → {b.issued_to} ({b.issue_date})")

    def save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({"counter": self.counter,
                       "books": [b.to_dict() for b in self.books.values()]}, f, indent=2)
        print(f"💾 Saved to {DATA_FILE}")

    def load(self):
        if not os.path.exists(DATA_FILE): return
        with open(DATA_FILE) as f: data = json.load(f)
        self.counter = data["counter"]
        self.books   = {d["book_id"]: Book.from_dict(d) for d in data["books"]}
        print(f"✅ Loaded {len(self.books)} book(s) from {DATA_FILE}")


def main():
    lib = Library()
    lib.load()

    if not lib.books:
        for args in [("The Alchemist","Paulo Coelho","Fiction",1988),
                     ("Atomic Habits","James Clear","Self-Help",2018),
                     ("Clean Code","R.C. Martin","Tech",2008)]:
            lib.add(*args)

    menu = """
┌─────────────────────────────┐
│   📚 LIBRARY MANAGER        │
├─────────────────────────────┤
│ 1. View All Books           │
│ 2. Add Book                 │
│ 3. Search by Title          │
│ 4. Search by Author         │
│ 5. Issue Book               │
│ 6. Return Book              │
│ 7. Report                   │
│ 8. Save & Exit              │
└─────────────────────────────┘"""

    actions = {
        "1": lambda: lib.display(),
        "2": lambda: lib.add(input("Title : "), input("Author: "),
                              input("Genre : "), input("Year  : ")),
        "3": lambda: lib.search(input("Search title : "), "title"),
        "4": lambda: lib.search(input("Search author: "), "author"),
        "5": lambda: lib.issue(input("Book ID: ").upper(), input("Issue to: ")),
        "6": lambda: lib.return_book(input("Book ID: ").upper()),
        "7": lambda: lib.report(),
    }

    while True:
        print(menu)
        choice = input("Choice: ").strip()
        if choice == "8":
            lib.save()
            print("👋 Goodbye!")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("❌ Invalid choice.")


if __name__ == "__main__":
    main()