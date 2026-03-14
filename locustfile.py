from locust import HttpUser, task, between
import random
import uuid

class MemeStrategyUser(HttpUser):
    # 模擬使用者在操作之間的思考時間 (1~3秒)
    wait_time = between(1, 3)

    def on_start(self):
        """
        每次產出一個新的虛擬使用者時執行：
        為這個使用者隨機產生一組帳密，先註冊，然後登入。
        這樣就不會發生 50 個人同時搶同一個帳號導致的 Session 錯亂。
        """
        # 產生獨一無二的帳號，例如 user_a1b2c3d4
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.email = f"{self.username}@test.com"
        self.password = "pass1234"

        # 1. 執行註冊 (不會標記在報表上的錯誤，因為我們只在乎後續操作)
        with self.client.post("/api/auth/register", json={
            "email": self.email,
            "username": self.username,
            "password": self.password
        }, catch_response=True) as response:
            if response.status_code in [201, 409]:
                response.success()
            else:
                response.failure(f"Register failed: {response.text}")

        # 2. 執行登入 (Locust 會自動把 response 的 Session Cookie 存起來)
        with self.client.post("/api/auth/login", json={
            "email": self.email,
            "password": self.password
        }, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")

    @task(4)
    def view_market_prices(self):
        """模擬使用者頻繁查看市場價格 (讀取操作，權重 4)"""
        self.client.get("/api/market/prices")

    @task(3)
    def view_dashboard(self):
        """模擬使用者查看自己的錢包與績效 (讀取操作，權重 3)"""
        self.client.get("/api/wallet")

    @task(2)
    def view_fund_info(self):
        """模擬使用者查看 Pokemon Fund 資訊 (讀取操作，權重 2)"""
        self.client.get("/api/fund/info")

    @task(1)
    def trade_crypto(self):
        """模擬偶爾進行買入交易 (寫入操作，權重 1，最容易觸發 DB Lock)"""
        assets = ["BTC", "ETH", "SOL", "MEMESTR"]
        self.client.post("/api/trade", json={
            "symbol": random.choice(assets),
            "side": "buy",
            "quantity": 0.01
        })
