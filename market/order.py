import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    """
    单个订单
    uid: 交易所编号
    is_buy: 是否是买单
    quantity: 下单数量
    outstanding_quantity: 未成交数量
    price: 下单价格
    time_submitted: 提交时间
    active: 是否启用
    is_ours: 是否为我们的订单
    """
    uid: int
    is_buy: bool
    quantity: int
    price: float
    timestamp: datetime.datetime
    is_ours: Optional[bool]

    def __post_init__(self):
        self.remaining_quantity = self.quantity

    def __str__(self):
        return {
            "订单序号": self.uid,
            "是否为买": self.is_buy,
            "数量": self.quantity,
            "未成交数量": self.remaining_quantity,
            "价格": self.price,
            "提交时间": self.timestamp,
            "是否为本方订单": self.is_ours
        }
