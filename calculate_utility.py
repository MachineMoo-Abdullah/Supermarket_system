def update_utility_scores(self):
    try:
        self.cursor.execute('''
            SELECT
                i.item_id,
                COALESCE(SUM(oi.quantity), 0) AS total_sold
            FROM items i
            LEFT JOIN order_items oi ON i.item_id = oi.item_id
            GROUP BY i.item_id
        ''')
        item_sales = self.cursor.fetchall()

        for item_id, total_sold in item_sales:
            self.cursor.execute('''
                UPDATE items
                SET utility_score = %s
                WHERE item_id = %s
            ''', (total_sold, item_id))

        self.conn.commit()
        messagebox.showinfo("Success", "Utility scores updated successfully!")
        self.load_items()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update utility scores.\n{str(e)}")
