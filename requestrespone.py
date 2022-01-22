from order import *
from voucher import *


class BillRequestObject:
    def __init__(self,shipping_fee,vouchers,orders):
        self.shipping_fee=shipping_fee
        self.vouchers=vouchers
        self.orders=orders

class BillRequest:
    def __init__(self,json_request:str) -> None:
        data=json_request['data']
        shipping_fee=data['shipping']
        list_vouchers=data['vouchers']
        list_orders=data['orders']
        

        self.shipping_fee=shipping_fee
        self.orders=[]
        self.vouchers=[]
        for  order_string  in list_orders:
            order=OrderParser(order_string).getDish()
            self.orders.append(order)
        
        for voucher_string in list_vouchers:
            voucher=VoucherParser(voucher_string).getVoucer()
            self.vouchers.append(voucher)
    
    def getObject(self)->BillRequestObject:
        return BillRequestObject(self.shipping_fee,self.vouchers,self.orders)
        



class BillResponeObject:
    def __init__(self,voucher,orders):
        
        self.voucher=voucher
        self.orders=orders
        
class BillRespone(BaseEntity):
    def __init__(self,bills,total,discounted,shiping):
        self.bills=bills
        self.total=total
        self.discounted=discounted
        self.shiping=shiping
    def getJSONString(self):
        return super().getJSONString()

    
        