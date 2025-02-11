import tkinter as tk # This line imports Tkinter with the name tk, so you can use Tkinter components (Button, Label, etc.) with this abbreviation. (kısaltma)
from tkinter.ttk import Combobox, Treeview #This line imports Combobox and Treeview widgets from Tkinter's ttk (themed Tkinter) module. #! Combobox:Allows the user to make a selection Treeview:Can be used to list database data.
from tkinter import messagebox, Entry, Label, Button #This line Imports various components (Entry,label,etc.)of the Tkinter library  #! messagebox: Used to display information, error or warning messages to the user.
                                    #! Entry: Used to get information from the user. Label: Used to show text or labels on the screen. Button: : Creates a button on the screen.Enables a specific function to run when this button is clicked.
import pyodbc

# DATABASE CONNECTION
server = r'VICTUS\SQLEXPRESS'
database = 'Trendora'
username = 'sa'
password = 'nazlan'

try:
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    )
    print("Connection successful!")
except pyodbc.Error as e:
    print(f"Error connecting to database: {e}")
    conn = None

cursor = conn.cursor()

# TABLE CREATION

#creating product table
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='product' AND xtype='U')
    CREATE TABLE product (
        product_id INT IDENTITY(1,1) PRIMARY KEY,
        product_name NVARCHAR(100),
        product_price FLOAT,
    );
""")
#creating stock table
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='stock' AND xtype='U')
    CREATE TABLE stock (
        stock_id INT IDENTITY(1,1) PRIMARY KEY,
        product_id INT ,
        quantity INT,
        FOREIGN KEY (product_id) REFERENCES product(product_id)
    );
""")
#creating customer table
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='customer' AND xtype='U')
    CREATE TABLE customer (
        cust_id INT IDENTITY(1,1) PRIMARY KEY,
        cust_name NVARCHAR(100),
        cust_address NVARCHAR(200), 
        phone_number BIGINT
    );
""")
# creating orders table
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='orders' AND xtype='U')
    CREATE TABLE orders (
        order_id INT IDENTITY(1,1) PRIMARY KEY,
        product_id INT,
        cust_id INT,
        FOREIGN KEY (product_id) REFERENCES product(product_id),
        FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
    );
""")

# creating cargo table
cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='cargo' AND xtype='U')
    CREATE TABLE cargo (
        cargo_id INT IDENTITY(1,1) PRIMARY KEY,
        cust_id INT,
        cust_name NVARCHAR(100),
        cust_address NVARCHAR(200),
        shipment_date DATE,
        FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
    );
""")

conn.commit()

# HELPER FUNCTIONS
def show_message(title, message, error=False):
    if error:
        messagebox.showerror(title, message) # if true display showerror
    else:
        messagebox.showinfo(title, message) # if false display showinfo 

def refresh_combo(combo): # ComboBox widget to be updated.
    cursor.execute("SELECT product_name FROM product")
    combo['values'] = [row[0] for row in cursor.fetchall()] # cursor.fetchall()--> Gets all rows in the query result and returns a list.

# MAIN MENU
def main_menu():
    #!! The interface is cleaned and a new interface or form can be presented to the user.
    for widget in root.winfo_children():# returns a list of all subcomponents (e.g. buttons, labels) contained within it.
        widget.destroy() # It destroys each widget one by one and removes it from the screen. 

    root.title("Main Menu")

    Label(root, text="Trendora", bg="#FFC0CB", fg="#000000", font=("Helvetica", 36)).place(x=120, y=20, width=350, height=100)

    Button(root, text="Product Screen", command=product_menu, bg="#48d1cc", fg="#F3E5F5", font=("Helvetica", 16)).place(x=50, y=140, width=200, height=80)
    Button(root, text="Stock Screen", command=stock_menu, bg="#48d1cc", fg="#F3E5F5", font=("Helvetica", 16)).place(x=350, y=140, width=200, height=80)
    Button(root, text="Customer Screen", command=customer_menu, bg="#48d1cc", fg="#F3E5F5", font=("Helvetica", 16)).place(x=50, y=250, width=200, height=80)
    Button(root, text="Cargo Screen", command=cargo_menu, bg="#48d1cc", fg="#F3E5F5", font=("Helvetica", 16)).place(x=350, y=250, width=200, height=80)


# PRODUCT MENU
def product_menu():
    def add_product():
        product_name = entry_name.get() # retrieves data
        product_price = entry_price.get()
        

        if not product_name or not product_price: # if empty: 
            show_message("Error", "Please fill in all fields.", error=True)
            return

        cursor.execute("SELECT product_name FROM product WHERE product_name = ?", (product_name,)) # Checks if there is a product with the same name in the database.
        if cursor.fetchone(): # if product already exists
            show_message("Error", "Product with this name already exists.", error=True)
            return

        cursor.execute( # if product is not exist, insert
            "INSERT INTO product (product_name, product_price) VALUES (?, ?)", #! ? --> Provides protection against SQL injections. 
            (product_name, float(product_price))
        )
        conn.commit() # changes are permanent 

        cursor.execute("SELECT product_id FROM product WHERE product_name = ?", (product_name,)) #Finds the line matching product_name 
        product_id = cursor.fetchone()[0] # Gets the first row returned from the query.

        cursor.execute("INSERT INTO stock (product_id, quantity) VALUES (?, 0)", (product_id,)) # Adds the newly added product to the stock table and initial quantity=0
        conn.commit() # save database 

        show_message("Success", "Product added successfully.")
        entry_name.delete(0, tk.END) #!! Clears input boxes so that the user can fill the form again !!
        entry_price.delete(0, tk.END)
        refresh_list() # updates the list 

    def refresh_list(): 
        #allows old data to be purged before it is refreshed (yenilenmeden önce temizlemeyi sağlar)
      for item in list_view.get_children(): # returns all items in the list view
        list_view.delete(item) ##! Clear current list

      cursor.execute("""
        SELECT stock.stock_id, product.product_name, product.product_price
        FROM stock
        JOIN product ON stock.product_id = product.product_id
       """)
      for row in cursor.fetchall(): # retrieves all data as a list
        list_view.insert("", "end", values=(row[0], row[1], row[2])) #Adds a new line to end of the list.
        #row[0]: stock_id
        #row[1]: product_name
        #row[2]: product_price
    
    def delete_product():
      try:
        # Get selected item from Treeview
        selected_item = list_view.selection()[0]
        values = list_view.item(selected_item)['values'] #Returns all data for the selected item
        print(f"Selected values: {values}")  # For debug in case of error

        # Get the first value product_id
        product_id = values[0]

        # If product_id is a string, convert it to int
        if isinstance(product_id, str): 
            product_id = int(product_id.strip())

        print(f"Product ID: {product_id} (type: {type(product_id)})") #! for debug

        # Deletes product from database 
        cursor.execute("DELETE FROM stock WHERE product_id = ?", (product_id,))
        cursor.execute("DELETE FROM product WHERE product_id = ?", (product_id,))
        conn.commit() # makes permanent 
       

        list_view.delete(selected_item) #Removes the selected item from the user interface in Treeview.

        show_message("Success", "Product deleted successfully.")
      except IndexError:
        show_message("Error", "Please select a product to delete.", error=True) #If the user tries to delete a product in Treeview without selecting it
      except ValueError:
        show_message("Error", "Invalid product ID format.", error=True) # If product_id cannot be converted to an integer
      except Exception as e:
        show_message("Error", f"An unexpected error occurred: {str(e)}", error=True) # When any unexpected error occurs

    for widget in root.winfo_children(): # Clear all available widgets
        widget.destroy() #!! The interface is cleaned and a new interface or form can be presented to the user.

    root.title("Product Menu")

    Label(root, text="Product Name", font=("Helvetica", 12)).place(x=225, y=20)
    Label(root, text="Product Price", font=("Helvetica", 12)).place(x=230, y=60)

    entry_name = Entry(root, width=35) #? Entry: Allows the user to enter text 
    entry_name.place(x=330, y=20, height=28)
    entry_price = Entry(root, width=35)#price area
    entry_price.place(x=330, y=60, height=28)#correct placement
 

    Button(root, text="MAIN MENU", command=main_menu, bg="#add8e6", font=("Helvetica", 12)).place(x=10, y=20, width=100, height=40)
    Button(root, text="SAVE", command=add_product, bg="#add8e6", font=("Helvetica", 12)).place(x=120, y=20, width=100, height=40)
    Button(root, text="DELETE", command=delete_product, bg="#add8e6", font=("Helvetica", 12)).place(x=10, y=80, width=100, height=40)
#column#
    list_view = Treeview(root, columns=("ID", "Name", "Price"), show="headings") #! With Treeview, products are listed in a table. Shows only column headings
    list_view.heading("ID", text="ID")
    list_view.heading("Name", text="Product Name")
    list_view.heading("Price", text="Product Price")
   
    list_view.column("ID", width=50)
    list_view.column("Name", width=300)
    list_view.column("Price", width=100)
   
    list_view.place(x=15, y=140, width=520, height=250) # Treeview yerleşimi (Treeview Overlay)

    refresh_list()



# STOCK MENU
def stock_menu():
    def refresh_list():
        for item in list_view.get_children(): #! Clear current list
            list_view.delete(item)

        cursor.execute("""
            SELECT stock.stock_id, product.product_name, stock.quantity
            FROM stock
            JOIN product ON stock.product_id = product.product_id
        """) 
        for row in cursor.fetchall():  # retrieves all data as a list
            list_view.insert("", "end", values=(row[0],row[1],row[2])) #Adds a new line to end of the list.

    def update_stock(add):
     product_name = combo.get()
     quantity = entry_quantity.get()

     quantity = int(quantity) #integer

     # Find the product ID
     cursor.execute("SELECT product_id FROM product WHERE product_name = ?", (product_name,))
     result = cursor.fetchone()

     if not result: ## if not found
        show_message("Error", "Selected product not found.", error=True)
        return #terminated

     product_id = result[0]

     # Get current stock quantity
     cursor.execute("SELECT quantity FROM stock WHERE product_id = ?", (product_id,))
     result = cursor.fetchone() # Executes SQL query
     if result:
        current_quantity = result[0]
     else:
        show_message("Error", "Product not found in stock.", error=True)
        return

     # Calculate new stock quantity
     new_quantity = current_quantity + quantity if add else current_quantity - quantity
     

     # Update stock
     cursor.execute("UPDATE stock SET quantity = ? WHERE product_id = ?", (new_quantity, product_id))
     conn.commit() #makes permanent

     show_message("Success", "Stock updated.")
     refresh_list()

    for widget in root.winfo_children(): #!! The interface is cleaned and a new interface or form can be presented to the user.(Arayüz temizlenir ve kullanıcıya yeni bir arayüz veya form sunulabilir.)
        widget.destroy()

    root.title("Stock Menu")

    Label(root, text="Product Name", font=("Helvetica", 12)).place(x=230, y=40)
    Label(root, text="Product Quantity", font=("Helvetica", 12)).place(x=230, y=80)

    combo = Combobox(root, width=28) #! is a component used to create a drop-down menu (açılır pencere) 
    # enables them to choose from the available products
    combo.place(x=350, y=40, height=30)

    refresh_combo(combo) #Combobox is updated when products change

    entry_quantity = Entry(root, width=31) #? Entry: Allows the user to enter text 
    entry_quantity.place(x=350, y=80, height=30)

    Button(root, text="Add Stock", command=lambda: update_stock(True), bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=20, width=180, height=30) #lambda: anonymous function True: add
    Button(root, text="Remove Product", command=lambda: update_stock(False), bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=60, width=180, height=30) #false: remove 
    Button(root, text="MAIN MENU", command=main_menu, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=100, width=180, height=30)

    list_view = Treeview(root, columns=("ID", "Name", "Quantity"), show="headings")
    list_view.heading("ID", text="ID")
    list_view.heading("Name", text="Product Name")
    list_view.heading("Quantity", text="Quantity")
    list_view.column("ID", width=50)
    list_view.column("Name", width=150)
    list_view.column("Quantity", width=80)
    list_view.place(x=15, y=140, width=520, height=250)

    refresh_list()

#CUSTOMER MENU
def customer_menu():
    def refresh_list():
        #! Clear current list
        for item in list_view.get_children():
            list_view.delete(item)

        # Pull data from customer table
        cursor.execute("""
            SELECT cust_id, cust_name, cust_address, phone_number
            FROM customer
        """)
        for row in cursor.fetchall():  # retrieves all data as a list
            list_view.insert("", "end", values=row) #Adds a new line to end of the list.

    def add_customer():
            # Receive new customer information 
            new_name = entry_cust_name.get()
            new_address = entry_cust_address.get()
            new_phone = entry_cust_phone.get()

            # Check if the fields are fill
            if not new_name or not new_address or not new_phone.isdigit():
                show_message("Error", "Please fill in all fields correctly.", error=True)
                return

            # Add new customer
            cursor.execute("""
                INSERT INTO customer (cust_name, cust_address, phone_number)
                VALUES (?, ?, ?)
            """, (new_name, new_address, int(new_phone)))
            conn.commit()

            show_message("Success", "New customer added successfully.")
            refresh_list()
    # Clear all widgets
    for widget in root.winfo_children(): #!! The interface is cleaned and a new interface or form can be presented to the user.
        widget.destroy()

    root.title("Customer Menu")

    Label(root, text="Customer Name", font=("Helvetica", 12)).place(x=230, y=40)
    Label(root, text="Customer Address", font=("Helvetica", 12)).place(x=230, y=80)
    Label(root, text="Phone Number", font=("Helvetica", 12)).place(x=230, y=120)

    entry_cust_name = Entry(root, width=31) #? Entry: Allows the user to enter text 
    entry_cust_name.place(x=400, y=40, height=30)

    entry_cust_address = Entry(root, width=31)
    entry_cust_address.place(x=400, y=80, height=30)

    entry_cust_phone = Entry(root, width=31)
    entry_cust_phone.place(x=400, y=120, height=30)

    Button(root, text="Add Customer", command=add_customer, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=40, width=180, height=30)
    Button(root, text="MAIN MENU", command=main_menu, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=80, width=180, height=30)

    
    list_view = Treeview(root, columns=("ID", "Name", "Address", "Phone"), show="headings")
    list_view.heading("ID", text="Customer ID")
    list_view.heading("Name", text="Customer Name")
    list_view.heading("Address", text="Customer Address")
    list_view.heading("Phone", text="Phone Number")
    list_view.column("ID", width=50)
    list_view.column("Name", width=150)
    list_view.column("Address", width=200)
    list_view.column("Phone", width=100)
    list_view.place(x=15, y=200, width=550, height=200)


    refresh_list()


    def update_customer():
        # Retrieve customer information
        cust_id = entry_cust_id.get()
        new_name = entry_cust_name.get().strip()
        new_address = entry_cust_address.get().strip()
        new_phone = entry_cust_phone.get().strip()

        if not cust_id.isdigit() or not new_name or not new_address or not new_phone.isdigit():
            show_message("Error", "Please fill in all fields correctly.", error=True)
            return

        # Customer ID check
        cursor.execute("SELECT 1 FROM customer WHERE cust_id = ?", (int(cust_id),))
        if not cursor.fetchone():
            show_message("Error", "Customer ID not found.", error=True)
            return

        # Update customer information
        cursor.execute("""
            UPDATE customer
            SET cust_name = ?, cust_address = ?, phone_number = ?
            WHERE cust_id = ?
        """, (new_name, new_address, int(new_phone), int(cust_id)))
        conn.commit()

        show_message("Success", "Customer information updated.")
        refresh_list()

    # Clear all widgets
    for widget in root.winfo_children():
        widget.destroy() #!! The interface is cleaned and a new interface or form can be presented to the user.

    root.title("Customer Menu")


    Label(root, text="Customer ID", font=("Helvetica", 12)).place(x=230, y=40)
    Label(root, text="Customer Name", font=("Helvetica", 12)).place(x=230, y=80)
    Label(root, text="Customer Address", font=("Helvetica", 12)).place(x=230, y=120)
    Label(root, text="Phone Number", font=("Helvetica", 12)).place(x=230, y=160)

    entry_cust_id = Entry(root, width=31) #? Entry: Allows the user to enter text 
    entry_cust_id.place(x=400, y=40, height=30)

    entry_cust_name = Entry(root, width=31)
    entry_cust_name.place(x=400, y=80, height=30)

    entry_cust_address = Entry(root, width=31)
    entry_cust_address.place(x=400, y=120, height=30)

    entry_cust_phone = Entry(root, width=31)
    entry_cust_phone.place(x=400, y=160, height=30)

    
    Button(root, text="Add Customer", command=add_customer, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=40, width=180, height=30)
    Button(root, text="Update Customer", command=update_customer, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=80, width=180, height=30)
    Button(root, text="MAIN MENU", command=main_menu, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=120, width=180, height=30)

   
    list_view = Treeview(root, columns=("ID", "Name", "Address", "Phone"), show="headings")
    list_view.heading("ID", text="Customer ID")
    list_view.heading("Name", text="Customer Name")
    list_view.heading("Address", text="Customer Address")
    list_view.heading("Phone", text="Phone Number")
    list_view.column("ID", width=50)
    list_view.column("Name", width=150)
    list_view.column("Address", width=200)
    list_view.column("Phone", width=100)
    list_view.place(x=15, y=200, width=550, height=200)

   
    refresh_list()

#CARGO NENU#
def cargo_menu():
    def show_message(title, message, error=False):
        from tkinter import messagebox
        if error:  # if true display showerror
            messagebox.showerror(title, message)
        else: #if false display showinfo 
            messagebox.showinfo(title, message)

    def refresh_list():
        #! Clear current list
        for item in list_view.get_children():
            list_view.delete(item)

        # Pull data from the cargo table
        cursor.execute("""
            SELECT cargo_id, cust_id,cust_name, cust_address, shipment_date 
            FROM cargo
        """)
        for row in cursor.fetchall():  # retrieves all data as a list
            list_view.insert("", "end", values=row) #Adds a new line to end of the list.

    def add_cargo():
            # Get new shipping information
            new_name = entry_cust_name.get()
            new_address = entry_cust_address.get()
            delivery_date = entry_shipment_date.get()

            if not new_name or not new_address or not delivery_date: # check is it empty?
                show_message("Error", "Please fill in all fields.", error=True)
                return
        
            # Add new cargo
            cursor.execute("""
                INSERT INTO cargo (cust_name, cust_address, shipment_date)
                VALUES (?, ?, ?)
              """, (new_name, new_address, delivery_date))

            conn.commit()

            show_message("Success", "New cargo added successfully.")
            refresh_list()

            
    def update_cargo():
        
            # Get updated shipping information
            cargo_id = entry_cargo_id.get()
            new_name = entry_cust_name.get()
            new_address = entry_cust_address.get()
            delivery_date = entry_shipment_date.get()

            
            if not cargo_id.isdigit() or not new_name or not new_address or not delivery_date: # checks is empty??
                show_message("Error", "Please fill in all fields correctly.", error=True)
                return

            # Cargo ID check
            cursor.execute("SELECT 1 FROM cargo WHERE cargo_id = ?", (int(cargo_id),))
            if not cursor.fetchone(): # if not found, show message
                show_message("Error", "Cargo ID not found.", error=True)
                return
            
            # Update shipping information
            cursor.execute("""
                UPDATE cargo
                SET cust_name = ?, cust_address = ?, shipment_date = ?
                WHERE cargo_id = ?
              """, (new_name, new_address, delivery_date, int(cargo_id)))
            conn.commit() #makes permanent 

            show_message("Success", "Cargo information updated.")
            refresh_list()

            
    # Clear all widgets
    for widget in root.winfo_children():
        widget.destroy() #!! The interface is cleaned and a new interface or form can be presented to the user.

    root.title("Cargo Menu")

    Label(root, text="Cargo ID", font=("Helvetica", 12)).place(x=230, y=40)
    Label(root, text="Customer Name", font=("Helvetica", 12)).place(x=230, y=80)
    Label(root, text="Address", font=("Helvetica", 12)).place(x=230, y=120)
    Label(root, text="Delivery Date (YYYY-MM-DD)", font=("Helvetica", 12)).place(x=190, y=160)

    entry_cargo_id = Entry(root, width=31) #? Entry: Allows the user to enter text 
    entry_cargo_id.place(x=400, y=40, height=30)

    entry_cust_name = Entry(root, width=31)
    entry_cust_name.place(x=400, y=80, height=30)

    entry_cust_address = Entry(root, width=31)
    entry_cust_address.place(x=400, y=120, height=30)

    entry_shipment_date = Entry(root, width=35)
    entry_shipment_date.place(x=400, y=160, height=30)

    Button(root, text="Add Cargo", command=add_cargo, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=40, width=180, height=30)
    Button(root, text="Update Cargo", command=update_cargo, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=80, width=180, height=30)
    Button(root, text="MAIN MENU", command=main_menu, bg="#add8e6", font=("Helvetica", 12)).place(x=20, y=120, width=180, height=30)

    list_view = Treeview(root, columns=("ID", "Name", "Address", "Date"), show="headings")
    list_view.heading("ID", text="Cargo ID")
    list_view.heading("Name", text="Customer Name")
    list_view.heading("Address", text="Address")
    list_view.heading("Date", text="Delivery Date")
    list_view.column("ID", width=50)
    list_view.column("Name", width=150)
    list_view.column("Address", width=200)
    list_view.column("Date", width=100)
    list_view.place(x=15, y=220, width=550, height=200)
    

     # Refresh list        #(I wrote this function because Customer name was NONE)
    def refresh_list():
     for item in list_view.get_children():
        list_view.delete(item) #! Clear current list

     cursor.execute("""
        SELECT cargo_id, cust_name, cust_address, shipment_date 
        FROM cargo
     """)
     for row in cursor.fetchall():
        # convert shipment_date to string format
        formatted_date = row[3].strftime('%Y-%m-%d') if row[3] else "N/A" 
         # Add to Listview
        list_view.insert("", "end", values=(row[0], row[1], row[2], formatted_date)) #Adds a new line to end of the list.
    refresh_list()
     

# MAIN WINDOW
root = tk.Tk() #? creates the main window. This window represents the main window that will host all the other widgets (buttons, labels, etc.).
root.geometry("600x400+500+200") #sets the size and position of the window on the screen (width:600px height:400px 500px to the right and 200px above the screen)
root.resizable(False, False) #!  prevents the dimensions of the window from being changed by the user. (pencere boyutlarının kullanıcı tarafından değiştirilmesini engeller.)
main_menu()
root.mainloop() #Starts the Tkinter application and ensures that the program runs continuously. #! This function is required for the application to remain active.(Uygulamanın etkin kalması için gerekli)
