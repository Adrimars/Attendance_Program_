import ast
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def push_day_function(day=None, month=None, year=None):
    # Tarih bilgisi verilmemişse, bugünün tarihini kullan
    if day is None or month is None or year is None:
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    else:
        current_date = f"{int(day):02d}-{int(month):02d}-{year}"

    file_name = f"names_rfidpoll_{current_date}.txt"

    # Google Sheets API'ye bağlanmak için gerekli kimlik bilgileri
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    client = gspread.authorize(creds)

    spreadsheet_id = '1XGr_OkIhrWnvLsnoMuwDCJCFpEdzgmRG1wpHH-J3kU8'  # Kendi Spreadsheet ID'nizi buraya girin

    try:
        sh = client.open_by_key(spreadsheet_id)
        sheet = sh.sheet1  # İlk sayfayı seçiyoruz
    except gspread.SpreadsheetNotFound:
        print(f"Spreadsheet ID '{spreadsheet_id}' ile bir spreadsheet bulunamadı.")
        return
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API Hatası: {e}")
        return

    # Attendance verilerini dosyadan oku
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            attendance_data = [ast.literal_eval(line.strip()) for line in file]
    except FileNotFoundError:
        print(f"{file_name} dosyası bulunamadı.")
        return

    # Mevcut sayfa verilerini al
    try:
        existing_data = sheet.get_all_values()
    except Exception as e:
        print(f"Google Sheet verileri alınırken bir hata oluştu: {e}")
        return

    # Eğer sayfa boşsa veya başlıklar eksikse, başlık satırını oluştur
    if not existing_data or len(existing_data[0]) < 2:
        headers = ['İsim', 'RFID', current_date]
        data = [headers]
        # Verileri ekle
        for entry in attendance_data:
            name = entry.get('name', '')
            rfid = entry.get('rfid', '')
            poll = entry.get('poll', 0)
            data.append([name, rfid, poll])
        # Verileri yaz
        try:
            sheet.update('A1', data)
            print("Veriler başarıyla Google Sheets'e pushlandı.")
        except Exception as e:
            print(f"Veriler pushlanırken bir hata oluştu: {e}")
        return  # İşlem tamamlandı, fonksiyondan çıkıyoruz

    else:
        # Mevcut başlıkları ve verileri ayrıştır
        headers = existing_data[0]  # İlk satır başlıklar
        records = existing_data[1:]  # Geri kalan veriler

        # Başlıkların ilk iki sütununun 'İsim' ve 'RFID' olduğundan emin olun
        if headers[0] != 'İsim' or headers[1] != 'RFID':
            print("Başlıklar beklenen formatta değil. Lütfen Google Sheet'in ilk iki sütununun 'İsim' ve 'RFID' olduğundan emin olun.")
            return

        # Tarih indeksini bulun veya ekleyin
        if current_date in headers:
            date_index = headers.index(current_date)
        else:
            headers.append(current_date)
            date_index = len(headers) - 1

        # İsim ve RFID'ye göre satırları eşleştirmek için bir sözlük oluştur
        name_rfid_to_row = {}
        for row in records:
            # Satırın uzunluğunu başlıklarla eşitle
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            # Satırın ilk iki elemanının var olduğundan emin olun
            if len(row) < 2:
                continue  # Satır yeterli bilgiye sahip değil, atlıyoruz
            name = row[0]
            rfid = row[1]
            name_rfid = (name, rfid)
            name_rfid_to_row[name_rfid] = row

        # Attendance data'daki öğrencileri güncelle veya ekle
        for entry in attendance_data:
            name = entry.get('name', '')
            rfid = entry.get('rfid', '')
            poll = entry.get('poll', 0)
            name_rfid = (name, rfid)

            if name_rfid in name_rfid_to_row:
                # Mevcut öğrenci
                row = name_rfid_to_row[name_rfid]
                # Satırı başlıklarla hizala
                if len(row) < len(headers):
                    row.extend([''] * (len(headers) - len(row)))
                row[date_index] = poll
            else:
                # Yeni öğrenci, boş bir satır oluştur
                row = [''] * len(headers)
                row[0] = name
                row[1] = rfid
                row[date_index] = poll
                name_rfid_to_row[name_rfid] = row

        # Tüm satırları bir araya getir
        new_records = list(name_rfid_to_row.values())

        # Verileri yaz
        data = [headers] + new_records

        try:
            sheet.clear()
            sheet.update('A1', data)
            print("Veriler başarıyla Google Sheets'e pushlandı.")
        except Exception as e:
            print(f"Veriler pushlanırken bir hata oluştu: {e}")

