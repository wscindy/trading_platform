"""
MemeStrategy Digital Asset Platform - MVP Backend
Flask API server with simulated digital asset trading,
wallet management, and Pokemon card tokenized fund.
"""
import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memestrategy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    wallets = db.relationship("Wallet", backref="user", lazy=True)
    orders = db.relationship("Order", backref="user", lazy=True)
    fund_holdings = db.relationship("FundHolding", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    asset_symbol = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "asset_symbol": self.asset_symbol,
            "balance": self.balance,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    asset_symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(4), nullable=False)       # "buy" or "sell"
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="filled")   # filled / pending / cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "asset_symbol": self.asset_symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FundHolding(db.Model):
    """User's holding in the Pokemon Card Tokenized Fund."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fund_id = db.Column(db.String(20), default="PKM-VGP-001")
    tokens = db.Column(db.Float, default=0.0)
    avg_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "tokens": self.tokens,
            "avg_price": self.avg_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# ---------------------------------------------------------------------------
# Simulated market data
# ---------------------------------------------------------------------------
ASSETS = {
    "BTC": {"name": "Bitcoin", "base_price": 87250.00, "icon": "₿"},
    "ETH": {"name": "Ethereum", "base_price": 2180.00, "icon": "Ξ"},
    "SOL": {"name": "Solana", "base_price": 142.50, "icon": "◎"},
    "MEMESTR": {"name": "MemeStrategy Token", "base_price": 0.0235, "icon": "🎭"},
}

POKEMON_FUND = {
    "fund_id": "PKM-VGP-001",
    "name": "Van Gogh Pikachu Tokenized Fund",
    "description": "Tokenized fund backed by PSA 10-rated 'Pikachu with Grey Felt Hat' cards. Each token represents fractional ownership of authenticated, insured cards stored in Grade10 museum-grade vaults.",
    "card_name": "Pikachu with Grey Felt Hat",
    "psa_grade": "PSA 10",
    "total_cards_target": 11750,
    "cards_acquired": 3842,
    "token_price": 20.00,
    "total_tokens": 1000000,
    "tokens_sold": 487320,
    "vault_provider": "Grade10 Vault",
    "audit_firm": "Big Four Accounting Firm",
    "next_audit_date": "2026-06-30",
    "min_investment_tokens": 10,
    "nav_per_token": 20.00,
}


def get_simulated_price(symbol):
    """Return a simulated price with small random fluctuation."""
    asset = ASSETS.get(symbol)
    if not asset:
        return None
    base = asset["base_price"]
    fluctuation = random.uniform(-0.02, 0.02)
    return round(base * (1 + fluctuation), 6)


def get_fund_nav():
    """Simulated NAV per token with small daily fluctuation."""
    base = POKEMON_FUND["nav_per_token"]
    fluctuation = random.uniform(-0.01, 0.015)
    return round(base * (1 + fluctuation), 2)


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    # Validation
    errors = {}
    if not email:
        errors["email"] = "Email is required"
    elif "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "Invalid email format"

    if not username:
        errors["username"] = "Username is required"
    elif len(username) < 3:
        errors["username"] = "Username must be at least 3 characters"
    elif len(username) > 30:
        errors["username"] = "Username must be at most 30 characters"
    elif not username.isalnum() and not all(c.isalnum() or c == '_' for c in username):
        errors["username"] = "Username can only contain letters, numbers, and underscores"

    if not password:
        errors["password"] = "Password is required"
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Validation failed", "details": {"email": "Email already registered"}}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Validation failed", "details": {"username": "Username already taken"}}), 409

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Create default wallets with some simulated balance
    for symbol in ASSETS:
        starting = {"BTC": 0.5, "ETH": 5.0, "SOL": 50.0, "MEMESTR": 10000.0}
        wallet = Wallet(user_id=user.id, asset_symbol=symbol,
                        balance=starting.get(symbol, 0))
        db.session.add(wallet)

    # USD wallet
    usd_wallet = Wallet(user_id=user.id, asset_symbol="USD", balance=100000.0)
    db.session.add(usd_wallet)

    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Login successful", "user": user.to_dict()})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
@login_required
def get_me():
    return jsonify({"user": request.current_user.to_dict()})


# ---------------------------------------------------------------------------
# Wallet / Portfolio routes
# ---------------------------------------------------------------------------
@app.route("/api/wallet", methods=["GET"])
@login_required
def get_wallet():
    wallets = Wallet.query.filter_by(user_id=request.current_user.id).all()
    portfolio = []
    total_value_usd = 0.0

    for w in wallets:
        if w.asset_symbol == "USD":
            portfolio.append({
                **w.to_dict(),
                "name": "US Dollar",
                "current_price": 1.0,
                "value_usd": w.balance,
                "icon": "$",
            })
            total_value_usd += w.balance
        else:
            asset = ASSETS.get(w.asset_symbol, {})
            price = get_simulated_price(w.asset_symbol) or 0
            value = w.balance * price
            portfolio.append({
                **w.to_dict(),
                "name": asset.get("name", w.asset_symbol),
                "current_price": price,
                "value_usd": round(value, 2),
                "icon": asset.get("icon", ""),
            })
            total_value_usd += value

    # Include fund holdings value
    fund_holdings = FundHolding.query.filter_by(user_id=request.current_user.id).all()
    for fh in fund_holdings:
        nav = get_fund_nav()
        fund_value = fh.tokens * nav
        total_value_usd += fund_value

    return jsonify({
        "portfolio": portfolio,
        "total_value_usd": round(total_value_usd, 2),
    })


# ---------------------------------------------------------------------------
# Market data routes
# ---------------------------------------------------------------------------
@app.route("/api/market/prices", methods=["GET"])
def get_prices():
    prices = {}
    for symbol, asset in ASSETS.items():
        price = get_simulated_price(symbol)
        change_pct = round(random.uniform(-5, 5), 2)
        prices[symbol] = {
            "symbol": symbol,
            "name": asset["name"],
            "icon": asset["icon"],
            "price": price,
            "change_24h_pct": change_pct,
        }
    return jsonify({"prices": prices})


@app.route("/api/market/price/<symbol>", methods=["GET"])
def get_price(symbol):
    symbol = symbol.upper()
    if symbol not in ASSETS:
        return jsonify({"error": f"Unknown asset: {symbol}"}), 404
    asset = ASSETS[symbol]
    price = get_simulated_price(symbol)
    change_pct = round(random.uniform(-5, 5), 2)
    return jsonify({
        "symbol": symbol,
        "name": asset["name"],
        "icon": asset["icon"],
        "price": price,
        "change_24h_pct": change_pct,
    })


@app.route("/api/market/history/<symbol>", methods=["GET"])
def get_price_history(symbol):
    """Generate simulated 30-day price history."""
    symbol = symbol.upper()
    if symbol not in ASSETS:
        return jsonify({"error": f"Unknown asset: {symbol}"}), 404

    base = ASSETS[symbol]["base_price"]
    history = []
    current = base * random.uniform(0.85, 0.95)
    now = datetime.now(timezone.utc)

    for i in range(30, 0, -1):
        day = now - timedelta(days=i)
        change = random.uniform(-0.03, 0.035)
        current = current * (1 + change)
        history.append({
            "date": day.strftime("%Y-%m-%d"),
            "price": round(current, 6),
            "volume": round(random.uniform(1000000, 50000000), 0),
        })

    return jsonify({"symbol": symbol, "history": history})


# ---------------------------------------------------------------------------
# Trading routes
# ---------------------------------------------------------------------------
@app.route("/api/trade", methods=["POST"])
@login_required
def place_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    symbol = (data.get("symbol") or "").upper()
    side = (data.get("side") or "").lower()
    quantity = data.get("quantity")

    # Validation
    errors = {}
    if symbol not in ASSETS:
        errors["symbol"] = f"Unknown asset: {symbol}"
    if side not in ("buy", "sell"):
        errors["side"] = "Side must be 'buy' or 'sell'"
    if quantity is None:
        errors["quantity"] = "Quantity is required"
    else:
        try:
            quantity = float(quantity)
            if quantity <= 0:
                errors["quantity"] = "Quantity must be greater than 0"
        except (ValueError, TypeError):
            errors["quantity"] = "Quantity must be a number"

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    price = get_simulated_price(symbol)
    total = round(quantity * price, 2)
    user = request.current_user

    usd_wallet = Wallet.query.filter_by(user_id=user.id, asset_symbol="USD").first()
    asset_wallet = Wallet.query.filter_by(user_id=user.id, asset_symbol=symbol).first()

    if not usd_wallet or not asset_wallet:
        return jsonify({"error": "Wallet not found"}), 500

    if side == "buy":
        if usd_wallet.balance < total:
            return jsonify({"error": "Insufficient USD balance",
                            "details": {"balance": usd_wallet.balance, "required": total}}), 400
        usd_wallet.balance = round(usd_wallet.balance - total, 2)
        asset_wallet.balance = round(asset_wallet.balance + quantity, 6)
    else:
        if asset_wallet.balance < quantity:
            return jsonify({"error": "Insufficient asset balance",
                            "details": {"balance": asset_wallet.balance, "required": quantity}}), 400
        asset_wallet.balance = round(asset_wallet.balance - quantity, 6)
        usd_wallet.balance = round(usd_wallet.balance + total, 2)

    order = Order(
        user_id=user.id,
        asset_symbol=symbol,
        side=side,
        quantity=quantity,
        price=price,
        total=total,
        status="filled",
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "Order filled", "order": order.to_dict()}), 201


@app.route("/api/orders", methods=["GET"])
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=request.current_user.id)\
        .order_by(Order.created_at.desc()).limit(50).all()
    return jsonify({"orders": [o.to_dict() for o in orders]})


# ---------------------------------------------------------------------------
# Pokemon Card Tokenized Fund routes
# ---------------------------------------------------------------------------
@app.route("/api/fund/info", methods=["GET"])
def get_fund_info():
    nav = get_fund_nav()
    fund = {**POKEMON_FUND, "current_nav": nav}
    fund["acquisition_progress_pct"] = round(
        fund["cards_acquired"] / fund["total_cards_target"] * 100, 1
    )
    fund["tokens_available"] = fund["total_tokens"] - fund["tokens_sold"]
    return jsonify({"fund": fund})


@app.route("/api/fund/subscribe", methods=["POST"])
@login_required
def subscribe_fund():
    """Buy tokens of the Pokemon Card Tokenized Fund."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    tokens = data.get("tokens")
    errors = {}

    if tokens is None:
        errors["tokens"] = "Number of tokens is required"
    else:
        try:
            tokens = float(tokens)
            if tokens < POKEMON_FUND["min_investment_tokens"]:
                errors["tokens"] = f"Minimum investment is {POKEMON_FUND['min_investment_tokens']} tokens"
            if tokens != int(tokens):
                errors["tokens"] = "Token quantity must be a whole number"
            else:
                tokens = int(tokens)
        except (ValueError, TypeError):
            errors["tokens"] = "Tokens must be a number"

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    nav = get_fund_nav()
    cost = round(tokens * nav, 2)
    user = request.current_user

    usd_wallet = Wallet.query.filter_by(user_id=user.id, asset_symbol="USD").first()
    if not usd_wallet or usd_wallet.balance < cost:
        return jsonify({"error": "Insufficient USD balance",
                        "details": {"balance": usd_wallet.balance if usd_wallet else 0,
                                    "required": cost}}), 400

    available = POKEMON_FUND["total_tokens"] - POKEMON_FUND["tokens_sold"]
    if tokens > available:
        return jsonify({"error": "Insufficient fund tokens available",
                        "details": {"available": available, "requested": tokens}}), 400

    # Execute
    usd_wallet.balance = round(usd_wallet.balance - cost, 2)

    holding = FundHolding.query.filter_by(user_id=user.id, fund_id="PKM-VGP-001").first()
    if holding:
        old_total = holding.tokens * holding.avg_price
        new_total = old_total + cost
        holding.tokens += tokens
        holding.avg_price = round(new_total / holding.tokens, 2)
    else:
        holding = FundHolding(user_id=user.id, fund_id="PKM-VGP-001",
                              tokens=tokens, avg_price=nav)
        db.session.add(holding)

    POKEMON_FUND["tokens_sold"] += tokens
    db.session.commit()

    return jsonify({
        "message": "Fund subscription successful",
        "subscription": {
            "tokens": tokens,
            "nav_per_token": nav,
            "total_cost": cost,
            "holding": holding.to_dict(),
        },
    }), 201


@app.route("/api/fund/redeem", methods=["POST"])
@login_required
def redeem_fund():
    """Sell/redeem tokens from the fund."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    tokens = data.get("tokens")
    errors = {}

    if tokens is None:
        errors["tokens"] = "Number of tokens is required"
    else:
        try:
            tokens = float(tokens)
            if tokens <= 0:
                errors["tokens"] = "Token quantity must be greater than 0"
            if tokens != int(tokens):
                errors["tokens"] = "Token quantity must be a whole number"
            else:
                tokens = int(tokens)
        except (ValueError, TypeError):
            errors["tokens"] = "Tokens must be a number"

    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    user = request.current_user
    holding = FundHolding.query.filter_by(user_id=user.id, fund_id="PKM-VGP-001").first()
    if not holding or holding.tokens < tokens:
        return jsonify({"error": "Insufficient fund tokens",
                        "details": {"holding": holding.tokens if holding else 0,
                                    "requested": tokens}}), 400

    nav = get_fund_nav()
    proceeds = round(tokens * nav, 2)

    holding.tokens -= tokens
    if holding.tokens == 0:
        db.session.delete(holding)

    POKEMON_FUND["tokens_sold"] -= tokens

    usd_wallet = Wallet.query.filter_by(user_id=user.id, asset_symbol="USD").first()
    usd_wallet.balance = round(usd_wallet.balance + proceeds, 2)

    db.session.commit()

    return jsonify({
        "message": "Fund redemption successful",
        "redemption": {
            "tokens": tokens,
            "nav_per_token": nav,
            "total_proceeds": proceeds,
        },
    })


@app.route("/api/fund/holdings", methods=["GET"])
@login_required
def get_fund_holdings():
    holdings = FundHolding.query.filter_by(user_id=request.current_user.id).all()
    result = []
    for h in holdings:
        nav = get_fund_nav()
        result.append({
            **h.to_dict(),
            "current_nav": nav,
            "current_value": round(h.tokens * nav, 2),
            "pnl": round(h.tokens * (nav - h.avg_price), 2),
        })
    return jsonify({"holdings": result})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


# ---------------------------------------------------------------------------
# Init DB & Run
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
