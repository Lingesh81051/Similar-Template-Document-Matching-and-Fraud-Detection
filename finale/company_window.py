from tkinter import Toplevel, Label, Button, Entry, Listbox, Scrollbar, END, messagebox
import csv
import os
import subprocess
from tkinter import simpledialog


class CompanyWindowInterface:
    def __init__(self, master):
        self.master = master

        self.master.title("Company Users")
        self.master.geometry("300x500")

        self.label_title = Label(master, text="Company Users", font=("Helvetica", 14))
        self.label_title.pack(pady=10)

        self.label_search = Label(master, text="Search:")
        self.label_search.pack()
        self.entry_search = Entry(master)
        self.entry_search.pack()

        self.listbox_users = Listbox(master, width=30)
        self.listbox_users.pack(pady=10, expand=True, fill="both")



        self.button_add_user = Button(master, text="Add User", command=self.add_user)
        self.button_add_user.pack(pady=5, fill="x")

        self.button_delete_user = Button(master, text="Delete User", command=self.delete_user)
        self.button_delete_user.pack(pady=5, fill="x")

        self.button_view_all = Button(master, text="View All Users", command=self.view_all_users)
        self.button_view_all.pack(pady=5, fill="x")

        self.button_view_genuine = Button(master, text="View Genuine Files", command=self.view_genuine_users)
        self.button_view_genuine.pack(pady=5, fill="x")

        self.button_view_fraud = Button(master, text="View Fraud Files", command=self.view_fraud_users)
        self.button_view_fraud.pack(pady=5, fill="x")

        self.button_close = Button(master, text="Close", command=master.destroy)
        self.button_close.pack(pady=10, fill="x")


        self.view_all_users()

        # Bind Enter key to search functionality
        self.entry_search.bind("<Return>", lambda event: self.search_users())


    
    def view_all_users(self):
        self.listbox_users.delete(0, END)
        with open('company_users.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.listbox_users.insert(END, row[0])


    def delete_user(self):
        selected_index = self.listbox_users.curselection()
        if selected_index:
            user_to_delete = self.listbox_users.get(selected_index)
            confirmation = messagebox.askyesno("Delete User", f"Are you sure you want to delete user '{user_to_delete}'?")
            if confirmation:
                with open('company_users.csv', 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    users = [row[0] for row in reader]
                users.remove(user_to_delete)
                with open('company_users.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    for user in users:
                        writer.writerow([user])
                self.listbox_users.delete(selected_index)
                messagebox.showinfo("Success", f"User '{user_to_delete}' deleted successfully.")
        else:
            messagebox.showinfo("Delete User", "Please select a user to delete.")
            
    def add_user(self):
        # Prompt the user to enter data for the new user
        new_user_data = simpledialog.askstring("Add User", "Enter the name and other info of the new user separated by commas (e.g., Name, Info):")
        if new_user_data:
            # Split the entered data into name and other info
            new_user_data = new_user_data.split(",")
            if len(new_user_data) >= 2:
                new_user_name = new_user_data[0].strip()
                new_user_info = ",".join(new_user_data[1:]).strip()  # Join the remaining data if any

                with open('company_users.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([new_user_name, new_user_info])
                self.listbox_users.insert(END, f"{new_user_name} ({new_user_info})")
                messagebox.showinfo("Success", f"User '{new_user_name}' added successfully.")
            else:
                messagebox.showinfo("Invalid Data", "Please enter at least the name and one other piece of information for the new user.")
        else:
            messagebox.showinfo("No Data Entered", "No data entered for the new user.")


    def view_genuine_users(self):
        self.listbox_users.delete(0, END)
        genuine_folder = "genuine"
        genuine_files = self.get_files_list(genuine_folder)
        for file in genuine_files:
            self.listbox_users.insert(END, file)
        self.bind_file_selection()  # Bind double-click event after populating the listbox

    def view_fraud_users(self):
        self.listbox_users.delete(0, END)
        fraud_folder = "fraud"
        fraud_files = self.get_files_list(fraud_folder)
        for file in fraud_files:
            self.listbox_users.insert(END, file)
        self.bind_file_selection() 

    def get_files_list(self, folder):
        if os.path.exists(folder):
            return os.listdir(folder)
        else:
            return []

    def view_file_contents(self, event):
        selected_file = self.listbox_users.get(self.listbox_users.curselection())
        if selected_file:
            folder = "genuine" if self.listbox_users.get(0).startswith("genuine") else "genuine"
            file_path = os.path.join(folder, selected_file)
            try:
                subprocess.Popen([file_path], shell=True)
            
            finally:""
        
        if selected_file:
            folder = "genuine" if self.listbox_users.get(0).startswith("genuine") else "fraud"
            file_path = os.path.join(folder, selected_file)
            try:
                subprocess.Popen([file_path], shell=True)
            finally:""





    def bind_file_selection(self):
        self.listbox_users.bind("<Double-Button-1>", self.view_file_contents)
    def search_users(self):
        search_term = self.entry_search.get().strip()
        if search_term:
            matching_users = []
            with open('company_users.csv', 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if search_term.lower() in row[0].lower():
                        matching_users.append(row[0])
            if matching_users:
                self.listbox_users.delete(0, END)
                for user in matching_users:
                    self.listbox_users.insert(END, user)
            else:
                messagebox.showinfo("Search Results", "No matching users found.")



