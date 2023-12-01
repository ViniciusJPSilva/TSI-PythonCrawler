import sqlite3
from time import time
from concurrent.futures import ThreadPoolExecutor
from web_utils import web_scraping as ws

IFET_URL = "https://www.ifsudestemg.edu.br/editais/editais-de-barbacena?b_start:int={}"
IFET_PAGINATOR_INCREMENT = 30
IFET_PAGINATOR_END = 180
LINK_CLASS = "state-published"
DB_NAME = "notices.db"

CREATE_TABLE_QUERY = '''
            CREATE TABLE IF NOT EXISTS notices (
                title TEXT,
                modality TEXT,
                number INTEGER,
                year INTEGER,
                situation TEXT,
                pdf_url TEXT
            )
        '''

INSERT_QUERY = '''
            INSERT INTO notices (title, modality, number, year, situation, pdf_url)
            VALUES (?, ?, ?, ?, ?, ?)
        '''


def create_table() -> None:
    """
    Cria a tabela 'notices' no banco de dados se não existir.

    :return: None
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Verificando se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notices'")
        table_exists = cursor.fetchone()

        # Apagando caso exista
        if table_exists:
            cursor.execute("DROP TABLE notices")

        cursor.execute(CREATE_TABLE_QUERY)
        conn.commit()


def process_link(link) -> None:
    """
    Processa um link para obter dados de um edital, e insere esses dados no banco de dados.

    :param link: Um link do edital.

    :return: None
    """
    result = ws.get_notice_data(link[1])
    if result:
        insert_into_db(result)


def insert_into_db(notice) -> None:
    """
    Insere os dados de um edital no banco de dados.

    :param notice: Um objeto de edital contendo título, modalidade, número, ano, situação e URL do PDF.

    :return: None
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(INSERT_QUERY, (notice.title, notice.modality, notice.number, notice.year, notice.situation, notice.pdf_url))
        conn.commit()


def main() -> None:
    """
    Função principal para criar a tabela, processar links e inserir dados no banco de dados.

    :return: None
    """
    create_table()
    page = 0
    with ThreadPoolExecutor(max_workers = 5) as executor:
        while page <= IFET_PAGINATOR_END:
            links = ws.get_links(IFET_URL.format(page), LINK_CLASS)
            executor.map(process_link, links)
            page += IFET_PAGINATOR_INCREMENT


if __name__ == "__main__":
    start = time()
    main()
    print(time() - start)

