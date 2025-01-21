import datetime
import ast
import tkinter as tk
from tkinter import messagebox
from tkinter import font
import json
from push_day import push_day_function
import os
from tkinter import filedialog


rfid_code = ''
reading_rfid = False

def name_check_in_file(file_name, search_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if search_name == line.strip():
                    return True
            return False
    except FileNotFoundError:
        return False

def name_add_to_txt(file_name, new_name):
    with open(file_name, 'a', encoding='utf-8') as file:
        file.write(new_name + '\n')

def name_and_rfid_to_file(name, rfid_code):
    name = name.title()
    new_entry = f"{{'name': '{name}', 'rfid': '{rfid_code}'}}\n"
    try:
        with open("names_rfid.txt", 'r', encoding='utf-8') as file:
            existing_data = file.readlines()

        if new_entry in existing_data:
            print("Bu giriş zaten mevcut. Yeni bir giriş eklenmedi.")
            return

        with open("names_rfid.txt", 'a', encoding='utf-8') as file:
            file.write(new_entry)
        print("İsim ve RFID eşleştirmesi names_rfid.txt dosyasına kaydedildi.")

    except FileNotFoundError:
        with open("names_rfid.txt", 'a', encoding='utf-8') as file:
            file.write(new_entry)
        print("Dosya bulunamadı, yeni bir dosya oluşturuldu ve giriş kaydedildi.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

def namerfid_to_namerfidpoll():
    try:
        with open("names_rfid.txt", 'r', encoding='utf-8') as file:
            names_rfid_data = [ast.literal_eval(line.strip()) for line in file]
    except FileNotFoundError:
        print("names_rfid.txt dosyası bulunamadı.")
        return

    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    file_name = f"names_rfidpoll_{current_date}.txt"

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            names_rfidpoll_data = [ast.literal_eval(line.strip()) for line in file]
    except FileNotFoundError:
        names_rfidpoll_data = []

    existing_names = set(entry['name'] for entry in names_rfidpoll_data)

    for entry in names_rfid_data:
        if entry['name'] not in existing_names:
            new_entry = {'name': entry['name'], 'rfid': entry['rfid'], 'poll': 0}
            names_rfidpoll_data.append(new_entry)

    with open(file_name, 'w', encoding='utf-8') as file:
        for entry in names_rfidpoll_data:
            file.write(f"{entry}\n")

def _0to1_turner(name):
    name = name.strip().title()
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    file_name = f"names_rfidpoll_{current_date}.txt"
    updated_data = []
    person_found = False

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                data = ast.literal_eval(line.strip())
                file_name_in_dict = data['name'].strip()

                if file_name_in_dict == name:
                    data['poll'] = 1
                    person_found = True
                updated_data.append(data)
    except FileNotFoundError:
        print(f"{file_name} dosyası bulunamadı.")
        return

    if person_found:
        with open(file_name, 'w', encoding='utf-8') as file:
            for data in updated_data:
                file.write(str(data) + '\n')
        print(f"{name} kişisinin poll değeri 1 olarak güncellendi.")
    else:
        print(f"{name} kişisi dosyada bulunamadı.")

def rfid_to_name(rfid):
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    file_name = f"names_rfidpoll_{current_date}.txt"

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                data = ast.literal_eval(line.strip())
                if data['rfid'] == rfid:
                    return data['name']
        return None
    except FileNotFoundError:
        print(f"{file_name} dosyası bulunamadı.")
        return None

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('new_registration_visible', True), config.get('attendance_visible', True)
    except FileNotFoundError:
        return True, True

def save_config(new_registration_visible, attendance_visible):
    config = {
        'new_registration_visible': new_registration_visible,
        'attendance_visible': attendance_visible
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f)

def main():
    global rfid_code, reading_rfid

    root = tk.Tk()
    root.title("RFID Kayıt Sistemi")
    root.configure(bg='#ECEEE5')
    root.attributes("-fullscreen", True)

    button_font = font.Font(family='Helvetica', size=14, weight='bold')
    label_font = font.Font(family='Helvetica', size=14)


    root.new_registration_visible, root.attendance_visible = load_config()

    button_frame = tk.Frame(root, bg='#ECEEE5')
    button_frame.pack(expand=True)

    def attendance_function():
        attendance_window = tk.Toplevel(root)
        attendance_window.title("Yoklama")
        attendance_window.configure(bg='#ECEEE5')
        attendance_window.attributes("-fullscreen", True)

        # Set focus to the new window
        attendance_window.focus_force()

        back_button = tk.Button(
            attendance_window,
            text="Geri",
            command=attendance_window.destroy,
            font=button_font,
            bg='#f0f0f0',
            fg='black',
            activebackground='#dcdcdc'
        )
        back_button.pack(anchor='nw', padx=10, pady=10)

        message_label = tk.Label(
            attendance_window,
            text="Yoklama İçin Lütfen Öğrenci Kartınızı Okutunuz.",
            bg='#ECEEE5',  # Arka plan rengini pencereyle aynı yapıyoruz
            fg='#666666',  # Yazı rengini koyu gri yapıyoruz
            font=("Helvetica", 30, "bold italic")  # Yazıyı kalın ve italik yapıyoruz
        )
        message_label.place(relx=0.5, rely=0.3, anchor='n')


        rfid_code = ''

        def reset_rfid():
            nonlocal rfid_code
            rfid_code = ''

        def process_rfid_code(rfid_code):
            name = rfid_to_name(rfid_code)
            if name:
                _0to1_turner(name)
                message_label.config(text=f"Hola {name}")
            else:
                message_label.config(text="Bu kart kayıtlı değil.")
            attendance_window.after(3000, lambda: message_label.config(text="Yoklama İçin Lütfen Öğrenci Kartınızı Okutunuz."))

        def on_key_press(event):
            nonlocal rfid_code
            if event.keysym == 'Return':
                process_rfid_code(rfid_code)
                reset_rfid()
            else:
                rfid_code += event.char

        attendance_window.bind('<Key>', on_key_press)

    def new_registration_function():
        registration_window = tk.Toplevel(root)
        registration_window.title("Yeni Kayıt")
        registration_window.configure(bg='#ECEEE5')
        registration_window.attributes("-fullscreen", True)

        for i in range(3):
            if i == 1:
                registration_window.columnconfigure(i, weight=0)
            else:
                registration_window.columnconfigure(i, weight=1)

        for i in range(30):
            if i == 1:
                registration_window.rowconfigure(i, weight=0)
            else:
                registration_window.rowconfigure(i, weight=1)
        # Back button to return to main window
        back_button = tk.Button(
            registration_window,
            text="Geri",
            command=registration_window.destroy,
            font=button_font,
            bg='#f0f0f0',
            fg='black',
            activebackground='#dcdcdc'
        )
        back_button.grid(row=0, column=0, padx=10, pady=2, sticky='nw')


        tk.Label(
            registration_window,
            text="Yeni Öğrenci Kaydı",
            font=("Helvetica", 40, "bold"),
            bg="#ECEEE5"
        ).grid(row=0, column=1, pady=(10, 10), sticky="n")

        # Instructions
        tk.Label(
            registration_window,
            text="Kayıt için aşağıdaki bilgileri doldurun ve kartınızı okutun.",
            bg='#ECEEE5',
            font=label_font
        ).grid(row=1, column=1, padx=10, pady=10)

        # Input label for name entry
        tk.Label(
            registration_window,
            text="İsim:",
            bg='#ECEEE5',
            font=label_font
        ).grid(row=2, column=1, padx=10, pady=5, sticky='w')

        # Name entry field
        name_entry = tk.Entry(
            registration_window,
            font=font.Font(family='Helvetica', size=14),
            width=30
        )
        name_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Suggestion list box for name suggestions
        suggestion_listbox = tk.Listbox(
            registration_window,
            height=5,
            font=font.Font(family='Helvetica', size=14),
            width=30
        )
        suggestion_listbox.grid(row=4, column=1, padx=10, pady=5, sticky='n')

        try:
            with open("names_inp.txt", 'r', encoding='utf-8') as file:
                name_list = [line.strip() for line in file]
        except FileNotFoundError:
            name_list = []

        # Function to update name suggestions
        def update_suggestions(event):
            suggestion_listbox.delete(0, tk.END)
            typed_text = name_entry.get()
            if typed_text:
                suggestions = [name for name in name_list if name.lower().startswith(typed_text.lower())]
                for name in suggestions:
                    suggestion_listbox.insert(tk.END, name)

        # Function to select a name from the suggestion box
        def fill_name(event=None):
            selected_name = suggestion_listbox.get(tk.ACTIVE)
            name_entry.delete(0, tk.END)
            name_entry.insert(0, selected_name)
            suggestion_listbox.delete(0, tk.END)

        # Bind key events for navigating suggestions
        def navigate_suggestions(event):
            current_index = suggestion_listbox.curselection()

            if event.keysym == "Tab" or event.keysym == "Down":  # Move to the next suggestion with Tab or Down Arrow
                next_index = (current_index[0] + 1) % suggestion_listbox.size() if current_index else 0
                suggestion_listbox.selection_clear(0, tk.END)
                suggestion_listbox.selection_set(next_index)
                suggestion_listbox.activate(next_index)
                return "break"  # Prevent default tab behavior

            elif event.keysym == "Up":  # Move to the previous suggestion with Up Arrow
                prev_index = (current_index[0] - 1) % suggestion_listbox.size() if current_index else suggestion_listbox.size() - 1
                suggestion_listbox.selection_clear(0, tk.END)
                suggestion_listbox.selection_set(prev_index)
                suggestion_listbox.activate(prev_index)
                return "break"  # Prevent default up arrow behavior

            elif event.keysym == "Return":  # Select the suggestion with Enter
                fill_name()
                return "break"  # Prevent default return behavior

        name_entry.bind('<KeyRelease>', update_suggestions)
        suggestion_listbox.bind('<Tab>', navigate_suggestions)
        suggestion_listbox.bind('<Down>', navigate_suggestions)
        suggestion_listbox.bind('<Up>', navigate_suggestions)
        suggestion_listbox.bind('<Return>', fill_name)
        suggestion_listbox.bind('<<ListboxSelect>>', fill_name)

        # Label for RFID card instructions
        instruction_label = tk.Label(
            registration_window,
            text="Lütfen isminizi girip kaydete basınız.",
            bg='#ECEEE5',
            font=label_font
        )
        instruction_label.grid(row=5, column=0, columnspan=3, pady=(20, 10))

        # Function to read RFID code
        def read_rfid(event=None):
            global rfid_code, reading_rfid
            reading_rfid = True
            instruction_label.config(text="Lütfen öğrenci kartınızı okutun...")
            name_entry.config(state='disabled')
            registration_window.bind('<Key>', on_key_press)

        # Captures each character of RFID input
        def on_key_press(event):
            global rfid_code, reading_rfid
            if reading_rfid:
                if event.keysym == 'Return':
                    instruction_label.config(text="")
                    reading_rfid = False
                    registration_window.unbind('<Key>')
                    name_entry.config(state='normal')
                    process_registration()
                    rfid_code = ''
                else:
                    rfid_code += event.char

        def show_success_message():
            success_label = tk.Label(root, text="Kayıt Başarılı", font=("Helvetica", 30), fg="green",bg="#ECEEE5")
            success_label.place(relx=0.5, rely=0.2, anchor='n')
            root.after(2000, success_label.destroy)  # 2 saniye sonra mesajı kaldır

        # Process registration data
        def process_registration():
            name = name_entry.get().strip().title()
            if not rfid_code:
                messagebox.showerror("Hata", "RFID kodu okunamadı.")
                return

            name_and_rfid_to_file(name, rfid_code)
            namerfid_to_namerfidpoll()
            _0to1_turner(name)
            show_success_message()  # Başarılı kayıt mesajını göster
            registration_window.destroy()

        # Trigger name registration process
        def register_name():
            name = name_entry.get().strip().title()
            if not name:
                messagebox.showwarning("Uyarı", "Lütfen bir isim giriniz.")
                return
            if not name_check_in_file("names_inp.txt", name):
                name_add_to_txt("names_inp.txt", name)
            read_rfid()

        # Button to finalize registration
        register_button = tk.Button(
            registration_window,
            text="Kaydet",
            command=register_name,
            font=button_font,
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            width=15
        )
        register_button.grid(row=6, column=0, columnspan=3, pady=20)

        # Add padding around each element for spacing and aesthetic layout
        for widget in registration_window.winfo_children():
            widget.grid_configure(padx=10, pady=10)

    def start_day_function():
        try:
            with open("names_rfid.txt", 'r', encoding='utf-8') as file:
                names_rfid_data = [ast.literal_eval(line.strip()) for line in file]
        except FileNotFoundError:
            messagebox.showerror("Hata", "names_rfid.txt dosyası bulunamadı.")
            return

        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        file_name = f"names_rfidpoll_{current_date}.txt"

        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                names_rfidpoll_data = [ast.literal_eval(line.strip()) for line in file]
        except FileNotFoundError:
            names_rfidpoll_data = []

        existing_names = set(entry['name'] for entry in names_rfidpoll_data)

        for entry in names_rfid_data:
            if entry['name'] not in existing_names:
                new_entry = {'name': entry['name'], 'rfid': entry['rfid'], 'poll': 0}
                names_rfidpoll_data.append(new_entry)

        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                for entry in names_rfidpoll_data:
                    file.write(f"{entry}\n")
            messagebox.showinfo("Bilgi", f"Gün başlatıldı. {file_name} dosyası güncellendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yazılırken bir hata oluştu: {e}")

    def show_admin_panel():
        password = password_entry.get().strip()
        if password == "admin123":  # Burada parolanızı belirleyin
            password_window.destroy()
            admin_window = tk.Toplevel(root)
            admin_window.title("Admin Panel")
            admin_window.configure(bg='#ECEEE5')

            # 'Güne Başla' butonu
            start_day_button = tk.Button(
                admin_window,
                text="Güne Başla",
                command=start_day_function,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            start_day_button.pack(pady=10)

            def push_day_function_main():
                # Dosya seçme penceresini aç
                filename = filedialog.askopenfilename(
                    title="Lütfen bir dosya seçin",
                    filetypes=[("Text files", "names_rfidpoll_*.txt")],
                    initialdir=os.getcwd(),
                    parent=admin_window
                )
                if filename:
                    # Dosya adından tarihi çıkar
                    base_name = os.path.basename(filename)
                    date_str = base_name.replace("names_rfidpoll_", "").replace(".txt", "")
                    try:
                        day_str, month_str, year_str = date_str.split('-')
                        day = int(day_str)
                        month = int(month_str)
                        year = int(year_str)
                        push_day_function(day, month, year)
                        messagebox.showinfo("Bilgi", "Gün başarıyla pushlandı.")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Tarih formatı hatalı veya dosya adı yanlış: {e}")
                else:
                    messagebox.showwarning("Uyarı", "Herhangi bir dosya seçilmedi.")

            # 'Günü Pushlamak' butonunu güncelle
            push_day_button = tk.Button(
                admin_window,
                text="Günü Pushlamak",
                command=push_day_function_main,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            push_day_button.pack(pady=10)

            # 'Manuel Yoklama Girişi' butonu
            def manual_attendance_entry():
                manual_window = tk.Toplevel(admin_window)
                manual_window.title("Manuel Yoklama Girişi")
                manual_window.configure(bg='#ECEEE5')

                # names_rfidpoll dosyasını oku
                current_date = datetime.datetime.now().strftime("%d-%m-%Y")
                file_name = f"names_rfidpoll_{current_date}.txt"

                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        names_rfidpoll_data = [ast.literal_eval(line.strip()) for line in file]
                except FileNotFoundError:
                    messagebox.showerror("Hata", f"{file_name} dosyası bulunamadı.")
                    return

                # poll değeri 0 olan öğrencileri al
                absent_students = [entry['name'] for entry in names_rfidpoll_data if entry['poll'] == 0]

                if not absent_students:
                    messagebox.showinfo("Bilgi", "Tüm öğrencilerin yoklaması zaten alınmış.")
                    manual_window.destroy()
                    return

                # Talimatlar
                instruction_label = tk.Label(
                    manual_window,
                    text="Yoklamasını güncellemek istediğiniz öğrencileri seçin:",
                    bg='#ECEEE5',
                    font=label_font
                )
                instruction_label.pack(pady=10)

                # Öğrencileri gösteren Listbox
                listbox = tk.Listbox(
                    manual_window,
                    selectmode=tk.MULTIPLE,
                    font=font.Font(family='Helvetica', size=14),
                    width=50,
                    height=20
                )
                for name in absent_students:
                    listbox.insert(tk.END, name)
                listbox.pack(pady=10)

                # Yoklamayı güncelleyen fonksiyon
                def update_attendance():
                    selected_indices = listbox.curselection()
                    if not selected_indices:
                        messagebox.showwarning("Uyarı", "Lütfen en az bir öğrenci seçiniz.")
                        return
                    selected_names = [listbox.get(i) for i in selected_indices]
                    for name in selected_names:
                        _0to1_turner(name)
                    messagebox.showinfo("Bilgi", "Seçilen öğrencilerin yoklaması güncellendi.")
                    manual_window.destroy()

                # Güncelle butonu
                update_button = tk.Button(
                    manual_window,
                    text="Yoklamayı Güncelle",
                    command=update_attendance,
                    font=button_font,
                    bg='#4CAF50',
                    fg='white',
                    activebackground='#45a049'
                )
                update_button.pack(pady=10)

                # Kapat butonu
                close_button = tk.Button(
                    manual_window,
                    text="Kapat",
                    command=manual_window.destroy,
                    font=button_font,
                    bg='#f0f0f0',
                    fg='black',
                    activebackground='#dcdcdc'
                )
                close_button.pack(pady=10)

            manual_attendance_button = tk.Button(
                admin_window,
                text="Manuel Yoklama Girişi",
                command=manual_attendance_entry,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            manual_attendance_button.pack(pady=10)

            # 'Yeni Kayıt' butonunu aç/kapat
            def toggle_registration():
                root.new_registration_visible = not root.new_registration_visible
                if root.new_registration_visible:
                    create_new_registration_button()
                    toggle_registration_button.config(text='Yeni Kayıt Butonunu Kapat')
                else:
                    remove_new_registration_button()
                    toggle_registration_button.config(text='Yeni Kayıt Butonunu Aç')
                save_config(root.new_registration_visible, root.attendance_visible)

            if root.new_registration_visible:
                toggle_button_text = 'Yeni Kayıt Butonunu Kapat'
            else:
                toggle_button_text = 'Yeni Kayıt Butonunu Aç'

            toggle_registration_button = tk.Button(
                admin_window,
                text=toggle_button_text,
                command=toggle_registration,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            toggle_registration_button.pack(pady=10)

            # 'Yoklama' butonunu aç/kapat
            def toggle_attendance():
                root.attendance_visible = not root.attendance_visible
                if root.attendance_visible:
                    create_attendance_button()
                    toggle_attendance_button.config(text='Yoklama Butonunu Kapat')
                else:
                    remove_attendance_button()
                    toggle_attendance_button.config(text='Yoklama Butonunu Aç')
                save_config(root.new_registration_visible, root.attendance_visible)

            if root.attendance_visible:
                toggle_attendance_text = 'Yoklama Butonunu Kapat'
            else:
                toggle_attendance_text = 'Yoklama Butonunu Aç'

            toggle_attendance_button = tk.Button(
                admin_window,
                text=toggle_attendance_text,
                command=toggle_attendance,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            toggle_attendance_button.pack(pady=10)

            # Admin panelini kapat butonu
            close_admin_button = tk.Button(
                admin_window,
                text="Kapat",
                command=admin_window.destroy,
                font=button_font,
                bg='#FFA500',
                fg='white',
                activebackground='#FF8C00'
            )
            close_admin_button.pack(pady=10)

        else:
            messagebox.showerror("Hata", "Yanlış parola.")










    # 'Yeni Kayıt' butonunu oluşturma ve kaldırma fonksiyonları
    def create_new_registration_button():
        if not hasattr(root, 'new_registration_button'):
            root.new_registration_button = tk.Button(
                button_frame,
                text="Yeni Kayıt",
                width=20,
                command=new_registration_function,
                font=button_font,
                bg='#4CAF50',
                fg='white',
                activebackground='#45a049'
            )
            root.new_registration_button.pack(padx=20, pady=20, side=tk.LEFT)

    def remove_new_registration_button():
        if hasattr(root, 'new_registration_button'):
            root.new_registration_button.pack_forget()
            del root.new_registration_button

    # 'Yoklama' butonunu oluşturma ve kaldırma fonksiyonları
    def create_attendance_button():
        if not hasattr(root, 'attendance_button'):
            root.attendance_button = tk.Button(
                button_frame,
                text="Yoklama",
                width=20,
                command=attendance_function,
                font=button_font,
                bg='#2196F3',
                fg='white',
                activebackground='#0b7dda'
            )
            root.attendance_button.pack(padx=20, pady=20, side=tk.LEFT)

    def remove_attendance_button():
        if hasattr(root, 'attendance_button'):
            root.attendance_button.pack_forget()
            del root.attendance_button

    # Kaydedilen duruma göre 'Yeni Kayıt' butonunu başlat
    if root.new_registration_visible:
        create_new_registration_button()

    # Kaydedilen duruma göre 'Yoklama' butonunu başlat
    if root.attendance_visible:
        create_attendance_button()

    bottom_frame = tk.Frame(root, bg='#ECEEE5')
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    password_window =    tk.Toplevel(root)
    password_window.title("Parola Girişi")
    tk.Label(password_window, text="Parola Giriniz:", font=label_font).pack(pady=10)
    password_entry = tk.Entry(password_window, show="*", font=font.Font(family='Helvetica', size=14))
    password_entry.pack(pady=10)
    tk.Button(password_window, text="Onayla", command=show_admin_panel, font=button_font, bg='#4CAF50', fg='white').pack(pady=10)

    def exit_fullscreen(event):
        root.attributes("-fullscreen", False)

    root.bind("<Escape>", exit_fullscreen)
    root.mainloop()

if __name__ == "__main__":
    main()

