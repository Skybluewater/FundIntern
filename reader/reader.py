class Reader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = self.read()

    def read_json(self):
        with open(self.file_path, "r") as f:
            import json
            return json.load(f)
        
    def read_pdf(self):
        with open(self.file_path, "rb") as f:
            from io import BytesIO
            return BytesIO(f.read())
    
    def read_xlsx(self):
        with open(self.file_path, "rb") as f:
            from io import BytesIO
            return BytesIO(f.read())

    def read(self):
        if self.file_path.endswith(".json"):
            return self.read_json()
        if self.file_path.endswith(".pdf"):
            return self.read_pdf()
        if self.file_path.endswith(".xlsx"):
            return self.read_xlsx()
        return None

if __name__ == "__main__":
    reader = Reader("上证50.json")
    print(reader.content)
    reader = Reader("15468.pdf")
    print(reader.content)