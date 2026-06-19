import os
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread

load_dotenv()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("ошибка: API_KEY не найден")
    exit()
else:
    print('API key loaded')

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Загрузка данных курсов валют
        self.data = None
        self.dataeur = None
        self.load_exchange_rates()
        
        self.setup_ui()
    
    def load_exchange_rates(self):
        """Загрузка курсов валют в отдельном потоке"""
        def fetch_rates():
            try:
                url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
                urleur = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/EUR"
                
                response = requests.get(url)
                response2 = requests.get(urleur)
                
                if response.status_code == 200 and response2.status_code == 200:
                    self.data = response.json()
                    self.dataeur = response2.json()
                    print('Курсы валют успешно загружены')
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить курсы валют")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {e}")
        
        # Запуск в отдельном потоке чтобы не блокировать GUI
        thread = Thread(target=fetch_rates)
        thread.daemon = True
        thread.start()
    
    def setup_ui(self):
        # Стили
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TCombobox', font=('Arial', 10))
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Конвертер валют", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Выбор валют
        ttk.Label(main_frame, text="Из:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.from_currency = ttk.Combobox(main_frame, values=['USD', 'EUR', 'RUB'], state="readonly")
        self.from_currency.set('USD')
        self.from_currency.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="В:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.to_currency = ttk.Combobox(main_frame, values=['USD', 'EUR', 'RUB'], state="readonly")
        self.to_currency.set('RUB')
        self.to_currency.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Сумма
        ttk.Label(main_frame, text="Сумма:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, font=('Arial', 12))
        amount_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Кнопка конвертации
        convert_btn = ttk.Button(main_frame, text="Конвертировать", command=self.convert)
        convert_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Результат
        self.result_var = tk.StringVar()
        result_label = ttk.Label(main_frame, textvariable=self.result_var, font=('Arial', 12, 'bold'), 
                               foreground='blue')
        result_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Информация о курсах
        self.rates_info = tk.StringVar()
        rates_label = ttk.Label(main_frame, textvariable=self.rates_info, font=('Arial', 9), 
                              foreground='gray')
        rates_label.grid(row=6, column=0, columnspan=2, pady=10)
        
        # Кнопка выхода
        exit_btn = ttk.Button(main_frame, text="Выход", command=self.root.quit)
        exit_btn.grid(row=7, column=0, columnspan=2, pady=10)
        
        # Настройка расширения колонок
        main_frame.columnconfigure(1, weight=1)
        
        # Обновление информации о курсах
        self.root.after(1000, self.update_rates_info)
    
    def update_rates_info(self):
        """Обновление информации о текущих курсах"""
        if self.data and self.dataeur:
            usd_rub = self.data['conversion_rates'].get('RUB', 'N/A')
            usd_eur = self.data['conversion_rates'].get('EUR', 'N/A')
            eur_rub = self.dataeur['conversion_rates'].get('RUB', 'N/A')
            
            info_text = (f"Курсы: USD/RUB: {usd_rub:.2f} | "
                       f"USD/EUR: {usd_eur:.2f} | "
                       f"EUR/RUB: {eur_rub:.2f}")
            self.rates_info.set(info_text)
        
        # Повторное обновление через 5 секунд
        self.root.after(5000, self.update_rates_info)
    
    def convert(self):
        """Выполнение конвертации"""
        if not self.data or not self.dataeur:
            messagebox.showwarning("Предупреждение", "Курсы валют еще не загружены. Подождите немного.")
            return
        
        try:
            amount = float(self.amount_var.get())
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            
            if from_curr == to_curr:
                self.result_var.set(f"{amount} {from_curr} = {amount} {to_curr}")
                return
            
            result = self.calculate_conversion(amount, from_curr, to_curr)
            
            if result is not None:
                self.result_var.set(f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")
            else:
                messagebox.showerror("Ошибка", "Не удалось выполнить конвертацию для выбранных валют")
                
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при конвертации: {e}")
    
    def calculate_conversion(self, amount, from_curr, to_curr):
        """Расчет конвертации между валютами"""
        rates = self.data['conversion_rates']
        rates_eur = self.dataeur['conversion_rates']
        
        conversion_map = {
            ('USD', 'RUB'): lambda: rates['RUB'] * amount,
            ('USD', 'EUR'): lambda: rates['EUR'] * amount,
            ('RUB', 'USD'): lambda: amount / rates['RUB'],
            ('EUR', 'RUB'): lambda: rates_eur['RUB'] * amount,
            ('RUB', 'EUR'): lambda: amount / rates_eur['RUB'],
            ('EUR', 'USD'): lambda: rates_eur['USD'] * amount,
            # Добавляем обратные конвертации
            ('RUB', 'RUB'): lambda: amount,
            ('USD', 'USD'): lambda: amount,
            ('EUR', 'EUR'): lambda: amount,
        }
        
        conversion_func = conversion_map.get((from_curr, to_curr))
        if conversion_func:
            return conversion_func()
        
        # Если прямой конвертации нет, пробуем через USD
        if from_curr != 'USD' and to_curr != 'USD':
            # Конвертируем from_curr -> USD -> to_curr
            usd_amount = self.calculate_conversion(amount, from_curr, 'USD')
            if usd_amount is not None:
                return self.calculate_conversion(usd_amount, 'USD', to_curr)
        
        return None

def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    
    # Центрирование окна
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
