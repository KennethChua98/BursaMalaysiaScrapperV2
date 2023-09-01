# Credit to: Lai Khee Jiunn
# Author: Kenneth Chua

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
from tqdm import tqdm
import time
from user_agent import options


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

    # Unique case: add a new row to the dataframe for KLCC Property Holdings Berhad & KLCC Real Estate Investment Trust
    df = df.append(
        {
            "code": "5235SS",
            "name": "KLCC__PROPERTY__HOLDINGS__BERHAD & KLCC__REAL__ESTATE__INVESTMENT__TRUST",
        },
        ignore_index=True,
    )

    df.to_csv("code.csv", index=False)

    driver.quit()


def getFinancialData():
    driver = webdriver.Chrome(options=options)
    columns = [
        "Stock Code",
        "Financial Year",
        "Announcement Date",
        "Quarter",
        "Revenue ('000)",
        "PBT ('000)",
        "NP ('000)",
        "NP to SH ('000)",
        "NP Margin",
        "ROE",
        "EPS",
        "DPS",
        "NAPS",
        "QoQ",
        "YoY",
    ]

    result = []
    # read the csv file
    df = pd.read_csv("code.csv")
    stock_code = df["code"].tolist()

    for i in tqdm(stock_code):
        try:
            driver.get(
                f"https://klse.i3investor.com/web/stock/financial-quarter/{i.format('04d')}"
            )

            table = driver.find_element(By.ID, "dttable-fin-quarter")
            rows = table.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME, "tr"
            )

            for row in rows:
                row_data = []
                cells = row.find_elements(By.TAG_NAME, "td")
                for cell in cells:
                    if cell.text.startswith("Financial Year:"):
                        financial_year = cell.text.split(":")[1].strip()
                    else:
                        row_data.append(cell.text)
                if len(row_data) > 0:
                    # append the stock code and financial year to the row data
                    result.append([i, financial_year] + row_data)
                    # write to csv
                    df = pd.DataFrame(result, columns=columns)
                    df.to_csv("financial_data.csv", index=False)
        except Exception as e:
            # write stock code to error.txt
            with open("error.txt", "a") as f:
                f.write(f"{i}\n")
    driver.quit()


try:
    pd.read_csv("code.csv")
except:
    getStockList()

getFinancialData()
