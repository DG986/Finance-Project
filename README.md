# 📈 C$50 Finance: A Stock Trading Simulator

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

This web application is a virtual stock trading platform built as part of **Harvard's CS50x course**. It empowers users to manage a portfolio of stocks using simulated money, providing a hands-on experience with stock market mechanics and web application development.

---

## ✨ Core Features

* **👤 User Authentication**: Secure user registration and login system with password hashing.
* **💹 Real-Time Quotes**: Fetch and display up-to-date stock prices using the IEX Cloud API.
* **💸 Buy & Sell**: Seamlessly "buy" and "sell" shares of stocks, with all transactions reflected in the user's virtual portfolio.
* **📊 Portfolio Dashboard**: A clear, dynamic overview of the user's stock holdings, current valuations, and available cash.
* **📜 Transaction History**: A detailed log of all past trades, including the type, stock symbol, price, and timestamp.

---

## 🛠️ Tech Stack

* **Backend**:
    * **Framework**: Flask
    * **Language**: Python
* **Database**:
    * **System**: SQLite
* **Frontend**:
    * **Templating**: Jinja
    * **Structure**: HTML & CSS
* **External Services**:
    * **API**: IEX Cloud for real-time stock data (proxied via CS50).

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.x
* pip package manager

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Set Up a Virtual Environment** (Recommended)
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    py -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application**
    ```bash
    flask run
    ```

5.  Open your browser and navigate to `http://127.0.0.1:5000`.

> **Note**
> The application is configured to use CS50's finance API proxy, so a personal IEX API key is not required for it to function as is.

---

## Database Schema

The application uses a simple SQLite database with two main tables:

1.  `users`: Stores user credentials and cash balance.
2.  `transactions`: Logs every buy and sell action for each user.

> ⚠️ **Important Security Note**
> The `finance.db` file should **not** be committed to a public repository as it can contain sensitive user information. It is best practice to add `*.db` to your `.gitignore` file.

