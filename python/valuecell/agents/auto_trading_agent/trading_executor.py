"""Trading execution and position management (refactored)"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any
from urllib.parse import urlparse

import httpx

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .exchanges import ExchangeBase, Order, OrderStatus, PaperTrading
from .models import (
    AutoTradingConfig,
    PortfolioValueSnapshot,
    Position,
    PositionHistorySnapshot,
    TechnicalIndicators,
    TradeAction,
    TradeHistoryRecord,
    TradeType,
)
from .position_manager import PositionManager
from .trade_recorder import TradeRecorder

logger = logging.getLogger(__name__)


class TradingExecutor:
    """
    Orchestrates trade execution using specialized modules.

    This is the main facade that coordinates:
    - Position management (via PositionManager)
    - Trade recording (via TradeRecorder)
    - Cash management (via PositionManager)
    """

    def __init__(
        self,
        config: AutoTradingConfig,
        exchange: Optional[ExchangeBase] = None,
    ):
        """
        Initialize trading executor.

        Args:
            config: Auto trading configuration
        """
        self.config = config
        self.initial_capital = config.initial_capital

        # Exchange adapter (defaults to in-memory paper trading)
        self.exchange: ExchangeBase = exchange or PaperTrading(
            initial_balance=config.initial_capital
        )
        self.exchange_type = self.exchange.exchange_type

        # Use specialized modules
        self._position_manager = PositionManager(config.initial_capital)
        self._trade_recorder = TradeRecorder()

    def _build_payload(self,symbol: str,action: str) -> Dict[str, Any]:
        """Build request payload"""
        import os
        logger.info("TradingExecutor: _build_payload")
        # Format timestamp as ISO 8601 string (yyyy-MM-ddTHH:mm:ssZ)
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Get signal token from environment
        signal_token = os.getenv("OKX_SIGNAL_TOKEN", "")
        instrument = symbol + "T-SWAP"
        logger.info(f"TradingExecutor: _build_payload instrument: {instrument}")
        payload = {
            "action": action,  # ENTER_LONG, EXIT_LONG, ENTER_SHORT, EXIT_SHORT
            "instrument": instrument,
            "signalToken": signal_token,
            "timestamp": timestamp,
            "maxLag": "300",
            "orderType": "market",
            "orderPriceOffset": "",
            "investmentType": "percentage_balance",
            "amount": "100",
        }

        return payload
    
    def _print_request_info(self, action: str, proxy: str,network: str,payload: Dict[str, Any]) -> None:
        """Print request information"""
        endpoint = (
        "https://www.okx.com/pap/algo/signal/trigger"
        if network == "paper"
        else "https://www.okx.com/algo/signal/trigger"
    )

        print("=" * 60)
        print("OKX Signal Test")
        print("=" * 60)
        print(f"Endpoint: {endpoint}")
        print(f"Action: {action}")
        print(f"Instrument: {payload.instrument}")
        print(f"Timestamp: {payload['timestamp']}")
        print(f"Investment Type: {payload.investment_type}")
        print(f"Amount: {payload.amount}")
        print(f"Order Type: {payload.order_type}")
        #if args.order_price_offset:
        #    print(f"Order Price Offset: {args.order_price_offset}%")
        #print(f"Paper Trading: {'Yes' if args.paper else 'No'}")
        if proxy:
            print(f"Proxy: {proxy}")
        print("=" * 60)
        print("\nPayload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("\nSending request...\n")

    def _send_request(self, payload: Dict[str, Any]) -> httpx.Response:
        """Send HTTP request to OKX"""
        import os
        logger.info("TradingExecutor: _send_request")
        # Determine endpoint based on network configuration
        network = os.getenv("OKX_NETWORK", "paper")
        endpoint = (
            "https://www.okx.com/pap/algo/signal/trigger"
            if network == "paper"
            else "https://www.okx.com/algo/signal/trigger"
        )

        # Build comprehensive browser-like headers to avoid 403 errors
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.okx.com",
            "Referer": "https://www.okx.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        }

        # Configure proxy from environment
        proxy = os.getenv("OKX_SIGNAL_PROXY")
        if proxy:
            logger.info(f"Using proxy: {proxy}")

        # Create client with timeout and proxy support
        client = httpx.Client(
        headers=headers,
        proxy=proxy,
        timeout=10.0,
        follow_redirects=True,
        )
 
        try:
            response = client.post(endpoint, json=payload)
            return response
        finally:
            client.close()

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle and print response"""
        logger.info(f"Response Status: {response.status_code}")
        logger.info(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")
        logger.info("\nResponse Body:")

        try:
            json_body = response.json()
            logger.info(json.dumps(json_body, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            logger.info(response.text)

        if 200 <= response.status_code < 300:
            logger.info("\n✅ SUCCESS: Signal sent successfully!")
        elif response.status_code == 403:
            logger.info(
                f"\n❌ FAILED: Server returned status {response.status_code} (Forbidden)"
            )
            logger.info("\n可能的原因：")
            logger.info("1. IP地址被OKX限制或拒绝访问")
            logger.info("   - 错误信息显示您的IP地址被拒绝")
            logger.info("   - 解决方案：使用 --proxy 参数设置代理服务器")
            logger.info(
                '   - 示例: python test_okx_signal.py --token "xxx" --proxy "http://proxy.example.com:8080"'
            )
            logger.info("\n2. 请求头不完整或不符合OKX要求")
            logger.info("   - 已添加完整的浏览器请求头，但可能仍需要代理")
            logger.info("\n3. 信号令牌无效或过期")
            logger.info("   - 请检查信号令牌是否正确")
            logger.info("   - 确保使用正确的端点（实盘 vs 模拟交易）")
        else:
            logger.info(f"\n❌ FAILED: Server returned status {response.status_code}")
       


    async def execute_trade(
        self,
        symbol: str,
        action: TradeAction,
        trade_type: TradeType,
        indicators: TechnicalIndicators,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a trade (open or close position).

        Args:
            symbol: Trading symbol
            action: Trade action (buy/sell)
            trade_type: Trade type (long/short)
            indicators: Current technical indicators

        Returns:
            Trade execution details or None if execution failed
        """
        #try:
        #    current_price = indicators.close_price
        #    timestamp = datetime.now(timezone.utc)

        #    if action == TradeAction.BUY:
        #        return await self._execute_buy(
        #            symbol, trade_type, current_price, timestamp
        #        )
        #    if action == TradeAction.SELL:
        #        return await self._execute_sell(
        #            symbol, trade_type, current_price, timestamp
        #        )

        #    return None

        #except Exception as e:
        #    logger.error(f"Failed to execute trade for {symbol}: {e}")
        #    return None

        logger.info(f"TradingExector execute_trade symbol: {symbol}")
        # Map TradeAction and TradeType to OKX signal action
        # ENTER_LONG, EXIT_LONG, ENTER_SHORT, EXIT_SHORT
        if action == TradeAction.BUY and trade_type == TradeType.LONG:
            okx_action = "ENTER_LONG"
        elif action == TradeAction.SELL and trade_type == TradeType.LONG:
            okx_action = "EXIT_LONG"
        elif action == TradeAction.SELL and trade_type == TradeType.SHORT:
            okx_action = "ENTER_SHORT"
        elif action == TradeAction.BUY and trade_type == TradeType.SHORT:
            okx_action = "EXIT_SHORT"
        else:
            logger.error(f"Invalid action/type combination: {action}/{trade_type}")
            return None

        # Build payload
        payload = self._build_payload(symbol,okx_action)

        # Send request
        response = self._send_request(payload)

        # Handle response
        self._handle_response(response)

        return None

    async def _execute_buy(
        self,
        symbol: str,
        trade_type: TradeType,
        current_price: float,
        timestamp: datetime,
    ) -> Optional[Dict[str, Any]]:
        """Open a new position"""
        # Check if we already have a position
        if self._position_manager.get_position(symbol) is not None:
            logger.info(f"Position already exists for {symbol}, skipping")
            return None

        # Check max positions limit
        if self._position_manager.get_positions_count() >= self.config.max_positions:
            logger.info(f"Max positions reached ({self.config.max_positions})")
            return None

        # Calculate position size
        available_cash = self._position_manager.get_available_cash()
        risk_amount = available_cash * self.config.risk_per_trade
        quantity = risk_amount / current_price if current_price > 0 else 0.0
        if quantity <= 0:
            logger.warning("Calculated quantity is non-positive; skipping trade")
            return None
        notional = quantity * current_price

        # Check if we have enough cash
        if notional > available_cash:
            logger.warning(
                f"Insufficient cash: need ${notional:.2f}, have ${available_cash:.2f}"
            )
            return None

        side = "buy" if trade_type == TradeType.LONG else "sell"
        order = await self._submit_order(
            symbol=symbol,
            side=side,
            quantity=abs(quantity),
            trade_type=trade_type,
        )

        if order is None or order.status in {
            OrderStatus.REJECTED,
            OrderStatus.CANCELLED,
        }:
            logger.warning("Exchange rejected open order for %s", symbol)
            return None

        fill_price = order.price or current_price
        notional = abs(quantity) * fill_price

        # Create and open position
        position = Position(
            symbol=symbol,
            entry_price=fill_price,
            quantity=abs(quantity) if trade_type == TradeType.LONG else -abs(quantity),
            entry_time=timestamp,
            trade_type=trade_type,
            notional=notional,
        )

        if not self._position_manager.open_position(symbol, position):
            return None

        # Record trade
        portfolio_value = self.get_portfolio_value()
        trade_record = TradeHistoryRecord(
            timestamp=timestamp,
            symbol=symbol,
            action="opened",
            trade_type=trade_type.value,
            price=fill_price,
            quantity=abs(position.quantity),
            notional=notional,
            pnl=None,
            portfolio_value_after=portfolio_value,
            cash_after=self._position_manager.get_available_cash(),
        )
        self._trade_recorder.record_trade(trade_record)

        return {
            "action": "opened",
            "trade_type": trade_type.value,
            "symbol": symbol,
            "entry_price": fill_price,
            "quantity": position.quantity,
            "notional": notional,
            "timestamp": timestamp,
            "order_id": order.order_id,
            "exchange": self.exchange_type.value,
        }

    async def _execute_sell(
        self,
        symbol: str,
        trade_type: TradeType,
        current_price: float,
        timestamp: datetime,
    ) -> Optional[Dict[str, Any]]:
        """Close an existing position"""
        # Get position
        position = self._position_manager.get_position(symbol)
        if position is None:
            return None

        # Check if trade type matches
        if position.trade_type != trade_type:
            return None

        side = "sell" if trade_type == TradeType.LONG else "buy"
        order = await self._submit_order(
            symbol=symbol,
            side=side,
            quantity=abs(position.quantity),
            trade_type=trade_type,
        )

        if order is None:
            logger.warning("Failed to close position on %s via exchange", symbol)
            return None

        exit_price = order.price or current_price
        pnl = self._position_manager.calculate_position_pnl(position, exit_price)
        exit_notional = abs(position.quantity) * exit_price

        # Close position locally
        self._position_manager.close_position(symbol)
        self._position_manager.release_cash(position.notional, pnl)

        # Record trade
        holding_time = timestamp - position.entry_time
        portfolio_value = self.get_portfolio_value()
        trade_record = TradeHistoryRecord(
            timestamp=timestamp,
            symbol=symbol,
            action="closed",
            trade_type=trade_type.value,
            price=exit_price,
            quantity=abs(position.quantity),
            notional=exit_notional,
            pnl=pnl,
            portfolio_value_after=portfolio_value,
            cash_after=self._position_manager.get_available_cash(),
        )
        self._trade_recorder.record_trade(trade_record)

        return {
            "action": "closed",
            "trade_type": trade_type.value,
            "symbol": symbol,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "quantity": position.quantity,
            "entry_notional": position.notional,
            "exit_notional": exit_notional,
            "pnl": pnl,
            "holding_time": holding_time,
            "timestamp": timestamp,
            "order_id": order.order_id,
            "exchange": self.exchange_type.value,
        }

    async def _submit_order(
        self,
        *,
        symbol: str,
        side: str,
        quantity: float,
        trade_type: TradeType,
        order_type: str = "market",
    ) -> Optional[Order]:
        try:
            if not self.exchange.is_connected:
                await self.exchange.connect()
            return await self.exchange.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=None,
                order_type=order_type,
                trade_type=trade_type,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Order submission failed (%s %s %s): %s",
                side,
                quantity,
                symbol,
                exc,
            )
            return None

    # ============ Portfolio Queries ============

    def get_portfolio_value(self) -> float:
        """Get total portfolio value"""
        total_value, _, _ = self._position_manager.calculate_portfolio_value()
        return total_value

    def get_portfolio_summary(self) -> Dict:
        """Get complete portfolio summary"""
        return self._position_manager.get_portfolio_summary()

    def get_current_capital(self) -> float:
        """Get available cash"""
        return self._position_manager.get_available_cash()

    @property
    def current_capital(self) -> float:
        """Property for backward compatibility"""
        return self._position_manager.get_available_cash()

    @property
    def positions(self) -> Dict[str, Position]:
        """Property for backward compatibility"""
        return self._position_manager.get_all_positions()

    # ============ History Management ============

    def snapshot_positions(self, timestamp: datetime):
        """Take a snapshot of all positions"""
        self._position_manager.snapshot_positions(timestamp)

    def snapshot_portfolio(self, timestamp: datetime):
        """Take a snapshot of portfolio value"""
        self._position_manager.snapshot_portfolio(timestamp)

    def get_trade_history(self) -> List[TradeHistoryRecord]:
        """Get all trade history"""
        return self._trade_recorder.get_all_trades()

    def get_position_history(self) -> List[PositionHistorySnapshot]:
        """Get all position snapshots"""
        return self._position_manager.get_position_history()

    def get_portfolio_history(self) -> List[PortfolioValueSnapshot]:
        """Get all portfolio snapshots"""
        return self._position_manager.get_portfolio_history()

    # ============ Statistics ============

    def get_trade_statistics(self) -> Dict:
        """Get trading statistics"""
        return self._trade_recorder.get_trade_statistics()

    def get_symbol_statistics(self, symbol: str) -> Dict:
        """Get statistics for a symbol"""
        return self._trade_recorder.get_symbol_statistics(symbol)

    def get_daily_statistics(self) -> Dict[str, Dict]:
        """Get daily P&L breakdown"""
        return self._trade_recorder.get_daily_statistics()

    # ============ Management ============

    def reset(self, initial_capital: float):
        """Reset executor state"""
        self._position_manager.reset(initial_capital)
        self._trade_recorder.reset()
