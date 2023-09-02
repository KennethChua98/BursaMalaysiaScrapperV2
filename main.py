# Credit to: Lai Khee Jiunn
# Author: Kenneth Chua

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
from tqdm import tqdm
import time
from chrome_options import options
from constants import *
import datetime


def getStockList():
    driver = webdriver.Chrome(options=options)
    driver.get(
        "http://www.bursamalaysia.com/market/listed-companies/list-of-companies/main-market/"
    )

    code, name = [], []

    select = Select(driver.find_element(By.NAME, "DataTables_Table_0_length"))
    select.select_by_index(3)  # select all companies

    time.sleep(5)

    elements = driver.find_element(By.ID, "DataTables_Table_0").find_elements(
        By.TAG_NAME, "a"
    )

    for i in tqdm(elements):
        href = i.get_attribute("href")
        href = href.split("stock_code=")
        if len(href) > 1:
            code.append(href[1])
            name.append(i.text)
        else:
            continue

    # use panda to combine the code and name and write to csv
    df = pd.DataFrame({"code": code, "name": name})

    # remove duplicate code and name if any
    df.drop_duplicates(subset="code", keep=False, inplace=True)

    # remove row if there is any null value
    df.dropna(inplace=True)

    # remove abnormal rows
    df = df[df["code"] != "KLCC__PROPERTY__HOLDINGS__BERHAD__stapled__5235SS"]
    df = df[df["code"] != "KLCC__REAL__ESTATE__INVESTMENT__TRUST__stapled__5235SS"]

    # Unique case: add a new row to the dataframe for KLCC Property Holdings Berhad & KLCC Real Estate Investment Trust
    df.loc[len(df.index)] = [
        "5235SS",
        "KLCC PROPERTY HOLDINGS BERHAD & KLCC REAL ESTATE INVESTMENT TRUST",
    ]

    df.to_csv("stock_list.csv", index=False)

    driver.quit()


def getFinancialData():
    current_year = datetime.datetime.now().year
    six_years_ago = int(current_year - 6)

    driver = webdriver.Chrome(options=options)

    result = []
    # read the csv file
    df = pd.read_csv("stock_list.csv")
    stock_codes = df["code"].tolist()

    for stock_code in stock_codes:
        old_data = False
        try:
            driver.get(
                f"https://klse.i3investor.com/web/stock/financial-quarter/{stock_code.format('04d')}"
            )

            table = driver.find_element(By.ID, "dttable-fin-quarter")
            rows = table.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME, "tr"
            )

            for row in rows:
                # skip if the data is older than 5 years
                if old_data:
                    break

                row_data = []
                cells = row.find_elements(By.TAG_NAME, "td")
                for cell in cells:
                    if cell.text.startswith("Financial Year:"):
                        financial_year_str = cell.text.split(":")[1].strip()
                        financial_year = datetime.datetime.strptime(
                            financial_year_str, "%d-%b-%Y"
                        ).year

                        if financial_year < six_years_ago:
                            old_data = True
                            break
                    else:
                        row_data.append(cell.text)

                if len(row_data) > 0:
                    # append the stock code and financial year to the row data
                    result.append([stock_code, financial_year_str] + row_data)
            df = pd.DataFrame(result, columns=columns)
            df.to_csv("financial_data.csv", index=False)
        except Exception as e:
            # write to log file
            with open("error.txt", "a") as f:
                f.write(f"{stock_code}: {e}\n")
            continue
    driver.quit()


def main():
    try:
        pd.read_csv("stock_list.csv")
    except:
        getStockList()
    getFinancialData()


if __name__ == "__main__":
    main()
