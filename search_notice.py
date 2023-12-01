import sqlite3
import argparse
from models.notice import Notice
from typing import List
from time import time

DB_NAME = "notices.db"

SELECT_QUERY = "SELECT * FROM notices"

def get_notices() -> List[Notice]:
    """
    Obtém todas as notificações armazenadas no banco de dados.

    :return: Uma lista de objetos de notificação.
    """
    notices = []
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(SELECT_QUERY)
        rows = cursor.fetchall()

        for row in rows:
            notice = Notice(*row)
            notices.append(notice)

    return notices


def has_term(text: str, term_list: List[str]) -> bool:
    """
    Verifica se uma string contém pelo menos um dos termos fornecidos.

    :param text: A string a ser verificada.
    :param term_list: Uma lista de termos.

    :return: True se pelo menos um termo for encontrado, False caso contrário.
    """
    text = text.lower()
    return any(term in text for term in [word.lower() for word in term_list])


def filter_notices(terms: List[str], modality: str, number: int, year: int, situation: str) -> List[Notice]:
    """
    Filtra notificações com base em critérios específicos.

    :param terms: Lista de termos a serem buscados nos títulos.
    :param modality: Modalidade do edital.
    :param number: Número do edital.
    :param year: Ano do edital.
    :param situation: Situação do edital.

    :return: Uma lista de notificações filtradas.
    """
    return [
            notice for notice in get_notices()
            if has_term(notice.title, terms)
            and (not modality or notice.modality.lower() == modality.lower())
            and (not number or notice.number == number)
            and (not year or notice.year == year)
            and (not situation or notice.situation.lower() == situation.lower())
        ]


def show_results(args: argparse.ArgumentParser, start_time: float, end_time: float, notices: List[Notice]):
    """
    Exibe os resultados da busca com base nos critérios fornecidos.

    :param args: Os argumentos da linha de comando fornecidos ao script.
    :param start_time: O tempo de início da busca.
    :param end_time: O tempo de término da busca.
    :param notices: Uma lista de objetos de notificação filtrados.

    :return: None
    """
    print("\n\nTermo(s) de busca: ", end='')
    [print(term, end = ' ') for term in args.term]

    print()
    
    if args.modalidade or args.numero or args.ano or args.situacao:
        print("\nFiltros: ")
        if args.modalidade:
            print(f"\tModalidade: {args.modalidade}")
        if args.numero:
            print(f"\tNúmero: {args.numero}")
        if args.ano:
            print(f"\tAno: {args.ano}")
        if args.situacao:
            print(f"\tSituação: {args.situacao}")

    print(f"\nTempo de resposta: {round((end_time - start_time) * 1000, 3)} ms\n\n{len(notices)} resultados\n\n----------------------------------------------------------------")
    if notices:
        for notice in notices:
            print(f"\n\n{notice.title}\n\nLink: {notice.pdf_url}\n")
    else:
        print("\nNenhum edital encontrado.\n\n")

    print()


def main():
    """
    Função principal para buscar editais com base nos critérios fornecidos via linha de comando.

    :return: None
    """
    parser = argparse.ArgumentParser(description="Busca editais com base nos critérios fornecidos.")
    parser.add_argument("term", nargs="*", help="Termo de busca nos títulos")
    parser.add_argument("-modalidade", type = str, help="Modalidade do edital")
    parser.add_argument("-numero", type = int, help="Número do edital")
    parser.add_argument("-ano", type = int, help="Ano do edital")
    parser.add_argument("-situacao", type = str, help="Situação do edital")

    args = parser.parse_args()

    if not args.term:
        print("\nO termo de busca é obrigatório!\n")
        return

    start_time = time()

    try:
        notices = filter_notices(args.term, args.modalidade, args.numero, args.ano, args.situacao)
    except sqlite3.OperationalError:
        print("\nBanco de dados inexistente ou com dados inválidos! Execute o crawler.py para criá-lo.\n")
        return 
    
    end_time = time()

    show_results(args, start_time, end_time, notices)


if __name__ == "__main__":
    main()
