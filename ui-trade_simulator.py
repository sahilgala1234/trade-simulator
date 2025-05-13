import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QLineEdit, QPushButton, QDoubleSpinBox,
                             QGroupBox, QFormLayout, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from collections import deque
import time


class TradeSimulatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Trade Simulator")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize data structures
        self.order_book = {'bids': [], 'asks': []}
        self.latency_history = deque(maxlen=100)
        self.last_update_time = time.time()
        
        self.setup_ui()
        self.setup_connections()
        self.simulate_data_stream()  # For demo purposes
        
    def setup_ui(self):
        """Initialize all UI components"""
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left Panel - Input Parameters
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout()
        
        # Exchange Selection
        exchange_group = QGroupBox("Exchange Parameters")
        exchange_layout = QFormLayout()
        
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["OKX", "Binance", "Coinbase", "Kraken"])
        
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"])
        
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["Tier 1 (<1M USD)", "Tier 2 (1-10M USD)", "Tier 3 (>10M USD)"])
        
        exchange_layout.addRow("Exchange:", self.exchange_combo)
        exchange_layout.addRow("Symbol:", self.symbol_combo)
        exchange_layout.addRow("Fee Tier:", self.fee_tier_combo)
        exchange_group.setLayout(exchange_layout)
        
        # Order Parameters
        order_group = QGroupBox("Order Parameters")
        order_layout = QFormLayout()
        
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit"])
        
        self.side_combo = QComboBox()
        self.side_combo.addItems(["Buy", "Sell"])
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0.001, 1000)
        self.quantity_input.setValue(0.1)
        self.quantity_input.setSuffix(" BTC")
        
        self.usd_value_label = QLabel("≈ $0.00")
        
        order_layout.addRow("Order Type:", self.order_type_combo)
        order_layout.addRow("Side:", self.side_combo)
        order_layout.addRow("Quantity:", self.quantity_input)
        order_layout.addRow("USD Value:", self.usd_value_label)
        order_group.setLayout(order_layout)
        
        # Market Parameters
        market_group = QGroupBox("Market Parameters")
        market_layout = QFormLayout()
        
        self.volatility_slider = QDoubleSpinBox()
        self.volatility_slider.setRange(0.1, 10.0)
        self.volatility_slider.setValue(2.5)
        self.volatility_slider.setSuffix("%")
        
        self.liquidity_label = QLabel("High")
        
        market_layout.addRow("Volatility:", self.volatility_slider)
        market_layout.addRow("Liquidity:", self.liquidity_label)
        market_group.setLayout(market_layout)
        
        # Control Buttons
        self.start_button = QPushButton("Start Simulation")
        self.stop_button = QPushButton("Stop Simulation")
        self.stop_button.setEnabled(False)
        
        left_layout.addWidget(exchange_group)
        left_layout.addWidget(order_group)
        left_layout.addWidget(market_group)
        left_layout.addWidget(self.start_button)
        left_layout.addWidget(self.stop_button)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        
        # Right Panel - Output Display
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Order Book Visualization (simplified)
        self.order_book_widget = QLabel("Order Book will be displayed here")
        self.order_book_widget.setAlignment(Qt.AlignCenter)
        self.order_book_widget.setStyleSheet("background-color: #f0f0f0; padding: 20px;")
        
        # Results Tabs
        results_tabs = QTabWidget()
        
        # Cost Estimation Tab
        cost_tab = QWidget()
        cost_layout = QFormLayout()
        
        self.slippage_label = QLabel("0.00%")
        self.fees_label = QLabel("$0.00")
        self.market_impact_label = QLabel("0.00%")
        self.total_cost_label = QLabel("$0.00")
        
        cost_layout.addRow("Expected Slippage:", self.slippage_label)
        cost_layout.addRow("Expected Fees:", self.fees_label)
        cost_layout.addRow("Market Impact:", self.market_impact_label)
        cost_layout.addRow("Total Estimated Cost:", self.total_cost_label)
        cost_tab.setLayout(cost_layout)
        
        # Advanced Metrics Tab
        metrics_tab = QWidget()
        metrics_layout = QFormLayout()
        
        self.maker_taker_ratio_label = QLabel("50% / 50%")
        self.latency_label = QLabel("0.0 ms")
        self.throughput_label = QLabel("0 updates/s")
        self.order_book_depth_label = QLabel("0 levels")
        
        metrics_layout.addRow("Maker/Taker Ratio:", self.maker_taker_ratio_label)
        metrics_layout.addRow("Processing Latency:", self.latency_label)
        metrics_layout.addRow("Throughput:", self.throughput_label)
        metrics_layout.addRow("Order Book Depth:", self.order_book_depth_label)
        metrics_tab.setLayout(metrics_layout)
        
        results_tabs.addTab(cost_tab, "Cost Estimation")
        results_tabs.addTab(metrics_tab, "Advanced Metrics")
        
        right_layout.addWidget(self.order_book_widget)
        right_layout.addWidget(results_tabs)
        right_panel.setLayout(right_layout)
        
        # Assemble main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status Bar
        self.statusBar().showMessage("Ready to connect to exchange...")
        
    def setup_connections(self):
        """Connect UI signals to slots"""
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.quantity_input.valueChanged.connect(self.update_usd_value)
        self.exchange_combo.currentTextChanged.connect(self.update_symbols)
        
    def update_usd_value(self):
        """Update USD value based on BTC price"""
        # In a real implementation, this would use the current market price
        btc_price = 50000  # Example price
        usd_value = self.quantity_input.value() * btc_price
        self.usd_value_label.setText(f"≈ ${usd_value:,.2f}")
        
    def update_symbols(self):
        """Update available symbols based on selected exchange"""
        exchange = self.exchange_combo.currentText()
        self.symbol_combo.clear()
        
        # Simplified example - in reality you'd fetch this from the exchange API
        if exchange == "OKX":
            self.symbol_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"])
        elif exchange == "Binance":
            self.symbol_combo.addItems(["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"])
        else:
            self.symbol_combo.addItems(["BTC-USD", "ETH-USD", "LTC-USD"])
    
    def start_simulation(self):
        """Start the simulation/connection"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage(f"Connected to {self.exchange_combo.currentText()} - Simulating...")
        
    def stop_simulation(self):
        """Stop the simulation/connection"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage("Simulation stopped")
        
    def simulate_data_stream(self):
        """Simulate incoming WebSocket data for demo purposes"""
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.generate_mock_data)
        self.sim_timer.start(100)  # Update every 100ms
        
    def generate_mock_data(self):
        """Generate mock order book data"""
        # Generate random bids and asks
        mid_price = 50000 + np.random.normal(0, 50)
        spread = 5 + abs(np.random.normal(0, 2))
        
        bids = []
        asks = []
        
        # Generate 10 levels each
        for i in range(10):
            bid_price = mid_price - (i * spread/2) - np.random.uniform(0, spread/4)
            bid_size = max(0.1, np.random.exponential(5))
            bids.append([bid_price, bid_size])
            
            ask_price = mid_price + (i * spread/2) + np.random.uniform(0, spread/4)
            ask_size = max(0.1, np.random.exponential(5))
            asks.append([ask_price, ask_size])
        
        # Update order book
        self.order_book = {
            'bids': sorted(bids, key=lambda x: -x[0]),  # Descending for bids
            'asks': sorted(asks, key=lambda x: x[0]),    # Ascending for asks
            'timestamp': time.time()
        }
        
        # Calculate metrics
        self.calculate_metrics()
        
        # Update latency tracking
        current_time = time.time()
        self.latency_history.append(current_time - self.last_update_time)
        self.last_update_time = current_time
        
    def calculate_metrics(self):
        """Calculate and update all metrics based on current order book"""
        if not self.order_book['bids'] or not self.order_book['asks']:
            return
        
        # Get best bid and ask
        best_bid = self.order_book['bids'][0][0]
        best_ask = self.order_book['asks'][0][0]
        mid_price = (best_bid + best_ask) / 2
        
        # Update order book display
        book_text = "BIDS:\n"
        for price, size in self.order_book['bids'][:5]:
            book_text += f"{price:,.2f} | {size:.4f}\n"
        
        book_text += "\nASKS:\n"
        for price, size in self.order_book['asks'][:5]:
            book_text += f"{price:,.2f} | {size:.4f}\n"
        
        self.order_book_widget.setText(book_text)
        
        # Calculate slippage (simplified)
        order_size = self.quantity_input.value()
        total_qty = 0
        avg_price = 0
        levels = self.order_book['asks'] if self.side_combo.currentText() == "Buy" else self.order_book['bids']
        
        for price, size in levels:
            fill_qty = min(order_size - total_qty, size)
            avg_price += price * fill_qty
            total_qty += fill_qty
            if total_qty >= order_size:
                break
        
        if total_qty > 0:
            avg_price /= total_qty
            ref_price = best_ask if self.side_combo.currentText() == "Buy" else best_bid
            slippage = (avg_price - ref_price) / ref_price * 100
            self.slippage_label.setText(f"{slippage:.2f}%")
        else:
            self.slippage_label.setText("N/A")
        
        # Calculate fees (simplified)
        fee_tier = self.fee_tier_combo.currentIndex()
        taker_fee = [0.001, 0.0007, 0.0005][fee_tier]
        fee_amount = order_size * mid_price * taker_fee
        self.fees_label.setText(f"${fee_amount:,.2f}")
        
        # Calculate market impact (simplified Almgren-Chriss)
        volatility = self.volatility_slider.value() / 100
        duration = 1.0  # Assume 1 second execution
        gamma = 0.01
        eta = 0.1
        
        perm_impact = gamma * order_size * volatility
        temp_impact = eta * (order_size ** 2) / (duration * mid_price)
        total_impact = (perm_impact + temp_impact) / mid_price * 100
        self.market_impact_label.setText(f"{total_impact:.2f}%")
        
        # Total cost
        slippage_cost = (slippage / 100) * order_size * mid_price if total_qty > 0 else 0
        total_cost = slippage_cost + fee_amount + (total_impact / 100 * order_size * mid_price)
        self.total_cost_label.setText(f"${total_cost:,.2f}")
        
        # Advanced metrics
        maker_taker_ratio = np.random.uniform(0.3, 0.7)
        self.maker_taker_ratio_label.setText(f"{maker_taker_ratio*100:.1f}% / {(1-maker_taker_ratio)*100:.1f}%")
        
        avg_latency = np.mean(self.latency_history) * 1000 if self.latency_history else 0
        self.latency_label.setText(f"{avg_latency:.1f} ms")
        
        throughput = 1 / np.mean(self.latency_history) if self.latency_history else 0
        self.throughput_label.setText(f"{throughput:.1f} updates/s")
        
        self.order_book_depth_label.setText(f"{len(self.order_book['bids'])} / {len(self.order_book['asks'])}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradeSimulatorUI()
    window.show()
    sys.exit(app.exec_())