# barkdown 🐻📚 

Simple Flask server to generate a markdown representation of a list of books.
1. Books are defined as Adlibris URL stubs (hosted at `BOOK_URL_SOURCE`)
2. Book data is extracted from individual Adlibris pages (`BOOK_DATA_SOURCE_PREFIX` + book stub)
3. Markdown representation is generated from the data

Result demo: https://foxtrot.bearblog.dev/bokonsker/
