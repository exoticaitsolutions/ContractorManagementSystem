import csv
import json
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QTextEdit, QMessageBox,QDesktopWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from LogsPrint import print_the_output_statement
from web_driver import initialize_driver

# Specify the download directory
download_dir = r'C:\Users\hp\Desktop\ContractorManagementSystem020824\ContractorManagement'
os.makedirs(download_dir, exist_ok=True)

# Function to read the contractor trades from a JSON file
def read_contractors_from_json(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
            trades = data.get("contractor_trades", [])
            return trades
    print(f"File not found: {file_name}")
    return []

# Function to read business types from a JSON file
def read_business_types_from_json(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
            business_types = data.get("businessTypes", [])
            return business_types
    print(f"File not found: {file_name}")
    return []

class ScrapeThread(QThread):
    scrape_finished = pyqtSignal(str)

    def __init__(self, code, business_type_code, text_area):
        super().__init__()
        self.code = code
        self.business_type_code = business_type_code
        self.text_area = text_area

    def run(self):
        self.scrape_data()

    def scrape_data(self):
        try:
            self.driver = initialize_driver()
            print_the_output_statement(self.text_area, "Opening site")
            self.driver.get("https://www.nj.gov/treasury/dpmc/contract_search.shtml")
            print("Page loaded")

            wait = WebDriverWait(self.driver, 30)

            # Wait for the first dropdown to be present and interactable
            dropdown_1_xpath = '/html/body/div[6]/div[1]/div/form/div/div[1]/div[2]/div/select'
            try:
                dropdown_1 = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_1_xpath)))
                print("First dropdown found")
            except Exception as e:
                print(f"Error locating the first dropdown: {e}")
                return

            # Select the corresponding option by the code
            select_1 = Select(dropdown_1)
            select_1.select_by_value(self.code)
            print(f"First dropdown option '{self.code}' selected")

            dropdown_2_xpath = '/html/body/div[6]/div[1]/div/form/div/div[1]/div[3]/div/select'
            try:
                dropdown_2 = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_2_xpath)))
                print("Second dropdown found")
            except Exception as e:
                print(f"Error locating the second dropdown: {e}")
                return

            # Select the option based on the selected business type
            if self.business_type_code:
                select_2 = Select(dropdown_2)
                select_2.select_by_value(self.business_type_code)
                print(f"Second dropdown option '{self.business_type_code}' selected")

                # Click the search button
                button_xpath = '/html/body/div[6]/div[1]/div/form/div/div[2]/div/div/input[1]'
                try:
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
                    print("Search button found")
                    button.click()
                    print("Search button clicked")
                except Exception as e:
                    print(f"Error locating or clicking the search button: {e}")
                    return

                # Wait for iframe and switch to it
                iframe_xpath = '//*[@id="results"]'
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, iframe_xpath)))
                    print("Entering the iframe...")
                    self.driver.switch_to.frame(self.driver.find_element(By.XPATH, iframe_xpath))
                except Exception as e:
                    print(f"Error locating or switching to iframe: {e}")
                    return

                # Extracting table data
                table_xpath = '//table'
                try:
                    table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    table_data = []

                    for row in rows:
                        cells = row.find_elements(By.XPATH, ".//td | .//th")
                        cell_data = [cell.text for cell in cells]
                        table_data.append(cell_data)

                    structured_data = []

                    # Process table data to extract structured information
                    for row_data in table_data:
                        if len(row_data) > 1:
                            if "Company Information" in row_data[0]:
                                # print("Skipping header row:", row_data)
                                continue

                            company_info = row_data[0].strip().split('\n')

                            # Ensure the company_info has the expected number of lines
                            try:
                                company_name = company_info[0] if len(company_info) > 0 else ''
                                address = ' '.join(company_info[1:5]).strip() if len(company_info) > 4 else ''
                                address_parts = address.split()

                                # Extract and organize the address components
                                if len(address_parts) >= 4:
                                    street = ' '.join(address_parts[:-3])
                                    country = address_parts[-3]
                                    zip_code = address_parts[-2]
                                else:
                                    street = country = zip_code = ''

                                phone_number_1 = company_info[4].strip() if len(company_info) > 4 else ''
                                phone_number_2 = company_info[5].strip() if len(company_info) > 5 else ''
                                email = company_info[6].strip() if len(company_info) > 6 else ''
                                expiration_date = company_info[8].split(': ')[1].strip() if len(company_info) > 8 and ': ' in company_info[8] else ''

                                # Extract Aggregate Amount and Bond Capacity
                                aggregate_amount = company_info[10].split(': ')[1].strip() if len(company_info) > 10 and ': ' in company_info[10] else ''
                                bond_capacity = company_info[11].strip() if len(company_info) > 11 else ''

                                # Extract Approved Date and Code
                                approved_date_and_code = row_data[1].strip() if len(row_data) > 1 else ''

                                # Combine into a structured format
                                structured_row = {
                                    'Company Name': company_name,
                                    'Address': street,
                                    'Country': country,
                                    'Zip code': zip_code,
                                    'Phone Number 1': phone_number_1,
                                    'Phone Number 2': phone_number_2,
                                    'Email': email,
                                    'Expiration Date': expiration_date,
                                    'Aggregate Amount': aggregate_amount,
                                    'Bond Capacity': bond_capacity,
                                    'Approved Date and Code': approved_date_and_code
                                }

                                # Append to the structured data list
                                # print("Data extracted:", structured_row)
                                structured_data.append(structured_row)
                            except IndexError as e:
                                print(f"Index error processing row: {row_data} - {e}")
                            except Exception as e:
                                print(f"Error processing row: {row_data} - {e}")
                        else:
                            print("Row does not have enough columns:", row_data)

                    # Write the structured data to a CSV file in the specified download directory
                    if structured_data:
                        csv_file_path = os.path.join(download_dir, 'table_data.csv')
                        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                            # Create a CSV writer object
                            fieldnames = ['Company Name', 'Address', 'Country', 'Zip code', 'Phone Number 1',
                                          'Phone Number 2', 'Email', 'Expiration Date', 'Aggregate Amount',
                                          'Bond Capacity', 'Approved Date and Code']
                            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(structured_data)

                        print("Data successfully written to:", csv_file_path)
                    else:
                        print("No data to write to CSV.")

                except Exception as e:
                    print(f"Error extracting table data: {e}")

                # Switch back to the main document if needed
                self.driver.switch_to.default_content()

        except Exception as e:
            print(f"An error occurred during scraping: {e}")

        finally:
            self.driver.quit()

        self.scrape_finished.emit("Scraping finished!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.code_mapping = {trade['name']: trade['code'] for trade in read_contractors_from_json('ContractorsbyTrade.json')}

    def initUI(self):
        self.setWindowTitle("Contractor Management")
        self.setGeometry(600, 400, 600, 400)
        self.center_window()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

         # Add heading at the top
        heading = QLabel("<h1>Contractor Management System</h1>")
        heading.setAlignment(Qt.AlignCenter)  
        layout.addWidget(heading)

        # Contractors by Trade Drop-down
        self.contractor_trade_combo = QComboBox()
        self.contractor_trade_combo.addItem("Select Contractor Trade", None)
        layout.addWidget(QLabel("<b>Contractors by Trade:</b>"))

        contractor_trades = read_contractors_from_json('ContractorsbyTrade.json')
        for trade in contractor_trades:
            self.contractor_trade_combo.addItem(trade['name'])
        layout.addWidget(self.contractor_trade_combo)

        self.business_type_combo = QComboBox()
        self.business_type_combo.addItem("Select Business Type", None)
        layout.addWidget(QLabel("<b>Business Type:</b>"))

        business_types = read_business_types_from_json('BusinessType.json')
        for business_type in business_types:
            self.business_type_combo.addItem(business_type['name'])
        layout.addWidget(self.business_type_combo)

        self.start_scrape_button = QPushButton("Start Scraping")
        self.start_scrape_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_scrape_button)

        self.start_scrape_button = QPushButton("Close Windows")
        self.start_scrape_button.clicked.connect(self.Close_Windows)
        layout.addWidget(self.start_scrape_button)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def Close_Windows(self):
        print("close windows")
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to close the application?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()  

    def start_scraping(self):
        selected_trade = self.contractor_trade_combo.currentText()
        code = self.code_mapping.get(selected_trade, "")

        selected_business_type = self.business_type_combo.currentText()
        business_type_code = self.get_business_type_code(selected_business_type)

        if not code:
            QMessageBox.warning(self, "Warning", "Please select a valid contractor trade.")
            return

        if not business_type_code:
            QMessageBox.warning(self, "Warning", "Please select a valid business type.")
            return

        # Start the scraping thread if both selections are valid
        self.thread = ScrapeThread(code, business_type_code, self.text_area)
        self.thread.scrape_finished.connect(self.on_scrape_finished)
        self.thread.start()

    def on_scrape_finished(self, message):
        self.text_area.append(message)

    def get_business_type_code(self, business_type_name):
        business_types = read_business_types_from_json('BusinessType.json')
        for business_type in business_types:
            if business_type['name'] == business_type_name:
                return business_type['business_type_code']
        return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
