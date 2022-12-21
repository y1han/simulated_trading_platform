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
    price: 下单价格
    time_submitted: 提交时间
    strike_price: 平均成交价格
    matched_quantity: 已成交数量
    remaining_quantity: 未成交数量
    time_finished: 完成时间
    # active: 是否启用
    is_ours: 是否为我们的订单
    """
    uid: int
    is_buy: bool
    quantity: int = 0
    price: float = 0
    time_submitted: Optional[datetime.datetime] = None
    strike_price: Optional[float] = None
    matched_quantity: int = 0
    time_finished: Optional[datetime.datetime] = None
    # active: Optional[bool] = True
    is_ours: Optional[bool] = False

    @property
    def remaining_quantity(self):
        return self.quantity - self.matched_quantity

    def __str__(self):
        return {
            "订单序号": self.uid,
            "是否为买": self.is_buy,
            "数量": self.quantity,
            "已成交数量": self.matched_quantity,
            "未成交数量": self.remaining_quantity,
            "下单价格": self.price,
            "平均成交价格": self.strike_price,
            "提交时间": self.time_submitted,
            "完成时间": self.time_finished,
            # "是否激活": self.active,
            "是否为本方订单": self.is_ours
        }
