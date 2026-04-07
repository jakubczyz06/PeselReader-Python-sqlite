#Importy
from datetime import date
import sqlite3


#Słownik potrzebny do klasy
MSC_DICT = {1: 'stycznia', 2: 'lutego', 3: 'marca',
            4: 'kwietnia', 5: 'maja', 6: 'czerwca',
            7: 'lipca', 8: 'sierpnia', 9: 'września',
            10: 'października', 11: 'listopada', 12: 'grudnia'}


#Cała klasa PeselReader z zapisem do bazy danych oraz blokiem testowym
class PeselReader:
    def __init__(self, pesel_str):
        if not (pesel_str.isdigit() and len(pesel_str) == 11):
            raise ValueError("Podany numer PESEL jest nieprawidłowy.")

        self.pesel_str = pesel_str
        self.checksum()


    def checksum(self):
        wagi = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        suma = 0

        for i in range(10):
            suma += int(self.pesel_str[i]) * wagi[i]
        kontrolna = (10 - (suma % 10)) % 10
        if kontrolna != int(self.pesel_str[10]):
            raise ValueError("Błąd checksum.")


    def decode_date_parts(self):
        rr = int(self.pesel_str[:2])
        mm_raw = int(self.pesel_str[2:4])
        dd = int(self.pesel_str[4:6])

        if 41 <= mm_raw <= 52:
            rok = 2100 + rr
            msc = mm_raw - 40
        elif 21 <= mm_raw <= 32:
            rok = 2000 + rr
            msc = mm_raw - 20
        elif 1 <= mm_raw <= 12:
            rok = 1900 + rr
            msc = mm_raw
        elif 81 <= mm_raw <= 92:
            rok = 1800 + rr
            msc = mm_raw - 80
        else:
            raise ValueError("Błędny kod miesiąca w numerze PESEL.")

        return rok, msc, dd


    def get_birth_date(self):
        rok, msc, dd = self.decode_date_parts()
        try:
            return date(rok, msc, dd)
        except ValueError:
            raise ValueError("Niepoprawna data w numerze PESEL.")


    def get_gender(self):
        cyfra_plec = int(self.pesel_str[9])

        return "Kobieta" if cyfra_plec % 2 == 0 else "Mężczyzna"


    def __str__(self):
        plec = self.get_gender()
        data = self.get_birth_date()
        rodzaj = "urodzona" if plec == "Kobieta" else "urodzony"

        return f"{plec}, {rodzaj} {data.day} {MSC_DICT[data.month]} {data.year} roku"


    def save_to_db(self, db_name = "PeselInfo.db"):
        con = sqlite3.connect(db_name)
        cur = con.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS PeselInfo("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "pesel TEXT UNIQUE NOT NULL,"
                    "plec TEXT NOT NULL,"
                    "data_ur TEXT NOT NULL)")

        plec = self.get_gender()
        data_ur = str(self.get_birth_date())

        try:
            cur.execute("""
                        INSERT INTO PeselInfo(pesel, plec, data_ur)
                        VALUES (?, ?, ?)
                        """, (self.pesel_str, plec, data_ur))
            con.commit()
            print(f"Zapisano PESEL: {self.pesel_str}")
        except sqlite3.IntegrityError:
            print(f"Info: PESEL o numerze {self.pesel_str} jest już w bazie.")
        finally:
            con.close()


    @classmethod
    def load_everything(cls, db_name = "PeselInfo.db"):
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        obiekty_pesel = []
        try:
            cur.execute("SELECT pesel FROM PeselInfo")
            records = cur.fetchall()

            for row in records:
                try:
                    obiekty_pesel.append(cls(row[0]))
                except ValueError as e:
                    print(f"Pominięty błędny rekord z bazy ({row[0]}): {e}")
            return obiekty_pesel
        except sqlite3.Error as e1:
            print(f"Błąd odczytu: {e1}")
            return []
        finally:
            con.close()


#Test
if __name__ == "__main__":
    testowe_pesele = []

    for p in testowe_pesele:
        try:
            nowy = PeselReader(p)
            nowy.save_to_db()
        except ValueError as e2:
            print(e2)

    print("---POBIERAM DANE---")
    lista_obywateli = PeselReader.load_everything(db_name="PeselInfo.db")

    if not lista_obywateli:
        print("Baza jest pusta, bądź wystąpił błąd.")
    else:
        for obywatel in lista_obywateli:
                print(f"- {obywatel}")
