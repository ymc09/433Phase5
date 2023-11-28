query = """
            SELECT *
            FROM (
                SELECT * FROM "Ordered By Clothing"
                WHERE customer_email = %s
                UNION
                SELECT * FROM "Ordered By Cosmetic"
                WHERE customer_email = %s
            ) AS combined_orders
            ORDER BY date_of_placement
        """
        cursor.execute(query, (session['user_id'], session['user_id']))
        all_orders = cursor.fetchall()

        # Fetch details of items for each order
        order_details = {}
        for order in all_orders:
            date_of_placement = order[3]  # Assuming date_of_placement is at index 3
            if date_of_placement not in order_details:
                order_details[date_of_placement] = []

            if "clothing_RefNb" in order:
                cursor.execute('SELECT "clothing_name","size" FROM "Clothing/Accessory item" WHERE "status" = "competed" and "clothing_RefNb" = %s', (order["clothing_RefNb"],))
            elif "cosmetic_RefNb" in order:
                cursor.execute('SELECT "cosmetic_name" FROM "Cosmetic item" WHERE "status" = "competed" and "cosmetic_RefNb" = %s', (order["cosmetic_RefNb"],))
            item_details = cursor.fetchone()
            order_details[date_of_placement].append(item_details)