from PIL import Image, ImageTk
import tkinter as tk

from Dashboard_page import DashboardPage
from customer_order_page import CustomerOrderPage
from customers_page import CustomerPage
from item_page import ItemsPage
from orders_page import OrdersPage
from reports_page import FrequentPatternsPage


class MainButtonsPage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Supermarket Management System")
        self.root.attributes('-fullscreen', True)  # Fullscreen
        self.root.config(bg='white')



        self.build_main_menu()

    def build_main_menu(self):
        # Top Header
        header = tk.Frame(self.root, bg='#4ade80', height=80)
        header.pack(fill='x')

        title = tk.Label(header, text="Supermarket Management System", font=("Arial", 24, "bold"), bg='#4ade80', fg='white')
        title.pack(pady=20)
        try:
            image = Image.open('images/images.jpeg')
            image = image.resize((420, 170), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            img_label = tk.Label(self.root, image=self.photo)  # Use self.root here
            img_label.pack(pady=20)
        except Exception as e:
            print("Error loading image:", e)
        # Buttons Grid
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=50)

        buttons = [
            ("Dashboard", self.open_dashboard),
            ("Place Order", self.open_place_order),
            ("Items", self.open_items),
            ("Customers", self.open_customers),
            ("Orders", self.open_orders),
            ("Reports", self.open_reports)
        ]

        for index, (label, command) in enumerate(buttons):
            row = index // 2
            col = index % 2
            btn = tk.Button(
                button_frame, text=label, font=("Arial", 16, "bold"),
                width=25, height=2, command=command,
                bg='#ef4444',  # 🔴 Red color
                fg='white',
                relief='raised', bd=2
            )

            btn.grid(row=row, column=col, padx=30, pady=20)
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)

        # Footer
        footer = tk.Label(self.root, text="© 2025 Supermarket Inc.", font=("Arial", 10), bg='white', fg='gray')
        footer.pack(side='bottom', pady=10)

    # Window-opening functions (fullscreen)
    def open_dashboard(self):
        self.switch_window(DashboardPage)

    def open_place_order(self):
        self.switch_window(CustomerOrderPage)

    def open_items(self):
        self.switch_window(ItemsPage)

    def open_customers(self):
        self.switch_window(CustomerPage)

    def open_orders(self):
        self.switch_window(OrdersPage)

    def open_reports(self):
        self.switch_window(FrequentPatternsPage)

    def switch_window(self, PageClass):
        self.root.destroy()
        new_root = tk.Tk()
        new_root.attributes('-fullscreen', True)
        PageClass(new_root)
        new_root.mainloop()

    def on_enter(self, e):
        e.widget['background'] = '#dc2626'  # Darker red on hover

    def on_leave(self, e):
        e.widget['background'] = '#ef4444'  # Original red

    def run(self):
        self.root.mainloop()

