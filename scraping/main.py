from logger_config import setup_logging
from scraper import scrape_pages

def main():
    setup_logging("scraper.log")
    scrape_pages()

if __name__ == "__main__":
    main()
