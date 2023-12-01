
class Notice:
    def __init__(self, title: str, modality: str, number: int, year: int, situation: str, pdf_url: str) -> None:
        self.title = title
        self.modality = modality
        self. number = number
        self.year = year
        self.situation = situation
        self.pdf_url = pdf_url

    def __str__(self) -> str:
        return f"{self.title}:\n\tModalidade: {self.modality}\n\tNúmero: {self.number}\n\tAno: {self.year}\n\tSituação: {self.situation}\n\tPDF: {self.pdf_url}"