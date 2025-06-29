import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime


class CustomerOrderPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Place Customer Order")
        self.root.attributes('-fullscreen', True)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="supermarket_db"
        )
        self.cursor = self.db.cursor()

        self.selected_items = []

        # Back button at top

        # Top frame for back button + headline
        top_frame = tk.Frame(root, bg="white")  # Increased height
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)  # Prevent shrinking to fit content

        back_btn = tk.Button(top_frame, text="Back", command=self.go_back, bg="red", fg="white", font=("Arial", 12))
        back_btn.grid(row=0, column=0, padx=(10, 20))

        headline = tk.Label(top_frame, text="Place Customer Order", font=("Arial", 20, "bold"), bg="white")
        headline.grid(row=0, column=1, sticky='w', padx=(400, 0))

        # ====== Main Frames ======
        main_frame = tk.Frame(root, bg="white")
        main_frame.pack(padx=40, pady=20, fill='both', expand=True)

        left_frame = tk.Frame(main_frame, bg="white")
        left_frame.grid(row=0, column=0, sticky="n")

        center_frame = tk.Frame(main_frame, bg="white")
        center_frame.grid(row=0, column=1, padx=40, sticky="n")

        right_frame = tk.Frame(main_frame, bg="white")
        right_frame.grid(row=0, column=2, padx=40, sticky="n")

        # ====== Left Form Inputs ======
        # ====== Left Form Inputs ======
        self.customer_name = tk.StringVar()
        self.phone = tk.StringVar()
        self.quantity_var = tk.IntVar()
        self.item_var = tk.StringVar()

        # Customer Name
        name_label = tk.Label(left_frame, text="Customer Name:", bg="white", font=("Segoe UI", 12))
        name_label.grid(row=0, column=0, sticky='w', pady=(5, 0))
        name_entry = tk.Entry(left_frame, textvariable=self.customer_name, font=("Segoe UI", 12), width=30)
        name_entry.grid(row=1, column=0, pady=(0, 10))
        name_entry.bind("<Return>", lambda e: phone_entry.focus())

        # Phone
        phone_label = tk.Label(left_frame, text="Phone:", bg="white", font=("Segoe UI", 12))
        phone_label.grid(row=2, column=0, sticky='w')
        phone_entry = tk.Entry(left_frame, textvariable=self.phone, font=("Segoe UI", 12), width=30)
        phone_entry.grid(row=3, column=0, pady=(0, 10))
        phone_entry.bind("<Return>", lambda e: self.item_dropdown.focus())

        # Select Item
        item_label = tk.Label(left_frame, text="Select Item:", bg="white", font=("Segoe UI", 12))
        item_label.grid(row=4, column=0, sticky='w')
        self.item_dropdown = ttk.Combobox(left_frame, textvariable=self.item_var, font=("Segoe UI", 12), width=28)
        self.item_dropdown.grid(row=5, column=0, pady=(0, 10),padx=(5,0))
        self.item_dropdown.bind("<<ComboboxSelected>>", self.update_stock_info)
        self.item_dropdown.bind("<Return>", lambda e: quantity_entry.focus())

        # Stock Info
        self.stock_info = tk.Label(left_frame, text="", bg="white", fg="green", font=("Segoe UI", 10, "italic"))
        self.stock_info.grid(row=6, column=0, sticky='w', pady=(0, 10),padx=(5,0))

        # Quantity
        quantity_label = tk.Label(left_frame, text="Quantity:", bg="white", font=("Segoe UI", 12))
        quantity_label.grid(row=7, column=0, sticky='w')
        quantity_entry = tk.Entry(left_frame, textvariable=self.quantity_var, font=("Segoe UI", 12), width=30)
        quantity_entry.grid(row=8, column=0, pady=(0, 10),padx=(5,0))
        quantity_entry.bind("<Return>", lambda e: add_btn.focus())

        # Add Item Button
        add_btn = tk.Button(left_frame, text="Add Item", command=self.add_item_to_order,
                            bg="#4ade80", fg="black", font=("Segoe UI", 12), width=22)
        add_btn.grid(row=9, column=0, pady=(5, 10))
        add_btn.bind("<Return>", lambda e: place_btn.focus())

        # Place Order Button
        place_btn = tk.Button(left_frame, text="Place Order", command=self.place_order,
                              bg="#2563eb", fg="white", font=("Segoe UI", 12), width=22)
        place_btn.grid(row=10, column=0, pady=(5, 10))

        # ====== Right Summary Box ======
        tk.Label(center_frame, text="Order Summary", bg="white", font=("Arial", 14, "bold")).pack()
        self.order_summary = tk.Text(center_frame, height=20, width=50, font=("Courier", 11))
        self.order_summary.pack(pady=10)

        tk.Label(right_frame, text="Customer Bill", bg="white", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        self.bill_display = tk.Text(right_frame, height=20, width=50, font=("Courier", 11))
        self.bill_display.pack()

        self.load_items()

    def update_stock_info(self, event=None):
        item_text = self.item_var.get()
        if item_text:
            try:
                item_id = int(item_text.split(" - ")[0])
                self.cursor.execute("SELECT quantity_in_stock FROM items WHERE item_id = %s", (item_id,))
                result = self.cursor.fetchone()
                if result:
                    stock = result[0]
                    bg_color = "red" if stock < 5 else "yellow"
                    txt_color = "white" if stock < 5 else "black"
                    self.stock_info.config(
                        text=f"In Stock: {stock}",
                        bg=bg_color,
                        fg=txt_color  # Make text readable on colored background
                    )
                else:
                    self.stock_info.config(text="Item not found", bg="red", fg="white")
            except:
                self.stock_info.config(text="Error loading stock info", bg="red", fg="white")

    def generate_bill(self, order_id, customer_name, phone, items, total_amount):
        now = datetime.now()
        bill_date = now.strftime("%Y-%m-%d %H:%M:%S")

        bill_content = []
        bill_content.append("         SuperMart POS System        ")
        bill_content.append("         ---------------------       ")
        bill_content.append(f"Date: {bill_date}")
        bill_content.append(f"Customer: {customer_name}")
        bill_content.append(f"Phone: {phone}")
        bill_content.append(f"Order ID: {order_id}")
        bill_content.append("-------------------------------------")
        bill_content.append("Item              Qty  Price  Total")
        bill_content.append("-------------------------------------")

        for item in items:
            name, qty, price, total = item[1], item[3], item[2], item[4]
            bill_content.append(f"{name:<17} {qty:<4} {price:<6.2f} {total:.2f}")

        bill_content.append("-------------------------------------")
        bill_content.append(f"Total Amount:               Rs {total_amount:.2f}")
        bill_content.append("\n        Thank you for shopping!      ")

        bill_text = "\n".join(bill_content)

        # Update bill on UI
        self.bill_display.delete("1.0", tk.END)
        self.bill_display.insert(tk.END, bill_text)

    def load_items(self):
        self.cursor.execute("SELECT item_id, name FROM items")
        self.items = self.cursor.fetchall()
        item_names = [f"{item[0]} - {item[1]}" for item in self.items]
        self.item_dropdown['values'] = item_names

    def go_back(self):
        self.root.destroy()
        import main
        main.start_main_ui()

    def add_item_to_order(self):
        item_text = self.item_var.get()
        quantity = self.quantity_var.get()

        if not item_text or quantity <= 0:
            messagebox.showwarning("Error", "Please select a valid item and quantity.")
            return

        item_id = int(item_text.split(" - ")[0])
        self.cursor.execute("SELECT name, price, quantity_in_stock FROM items WHERE item_id = %s", (item_id,))
        item = self.cursor.fetchone()

        if not item or item[2] < quantity:
            messagebox.showerror("Out of Stock", "Not enough stock for this item.")
            return

        name, price, _ = item
        total_price = price * quantity
        self.selected_items.append((item_id, name, price, quantity, total_price))
        self.order_summary.insert(tk.END, f"{name} x {quantity} @ {price} = {total_price:.2f}\n")

    def place_order(self):
        name = self.customer_name.get()
        phone = self.phone.get()

        if not name:
            messagebox.showerror("Missing Info", "Customer name is required.")
            return

        self.cursor.execute("SELECT customer_id FROM customers WHERE name = %s AND phone = %s", (name, phone))
        result = self.cursor.fetchone()

        if result:
            customer_id = result[0]
        else:
            self.cursor.execute("INSERT INTO customers (name, phone) VALUES (%s, %s)", (name, phone))
            self.db.commit()
            customer_id = self.cursor.lastrowid

        total_amount = sum([item[4] for item in self.selected_items])
        self.cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
                            (customer_id, total_amount))
        self.db.commit()
        order_id = self.cursor.lastrowid

        for item_id, name, price, qty, total in self.selected_items:
            self.cursor.execute("""
                INSERT INTO order_items (order_id, item_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item_id, qty, price))
            self.cursor.execute("UPDATE items SET quantity_in_stock = quantity_in_stock - %s WHERE item_id = %s",
                                (qty, item_id))
            self.cursor.execute("UPDATE items SET total_sold = total_sold + %s WHERE item_id = %s", (qty, item_id))
            self.cursor.execute("SELECT price, cost_price, total_sold FROM items WHERE item_id = %s", (item_id,))
            item_data = self.cursor.fetchone()
            if item_data:
                updated_price, cost_price, total_sold = item_data
                new_utility_score = (updated_price - cost_price) * total_sold
                self.cursor.execute("UPDATE items SET utility_score = %s WHERE item_id = %s",
                                    (new_utility_score, item_id))
            self.cursor.execute("INSERT INTO transactions_log (item_id, quantity) VALUES (%s, %s)", (item_id, qty))

        self.db.commit()
        messagebox.showinfo("Success", "Order placed successfully!")
        self.generate_bill(order_id, name, phone, self.selected_items, total_amount)
        self.selected_items.clear()
        self.order_summary.delete(1.0, tk.END)
        self.customer_name.set("")
        self.phone.set("")
        self.item_var.set("")
        self.quantity_var.set(0)
        self.stock_info.config(text="")
        self.stock_info.config(text="", bg="white", fg="green")

        self.load_items()
