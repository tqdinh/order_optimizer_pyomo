from pyomo.environ import *
from requestrespone import BillRespone, BillResponeObject
from voucher import Voucher

from order import Order
import sys
import json
import numpy as np



NUMBER_OF_BILL_SPLITTED=5
INF=10240000
class BillOptimizer:
   def __init__(self,shipping_fee,orders,vouchers):

      self.shipping_fee=shipping_fee
      self.orders=orders
      self.vouchers=vouchers
      
        
   def optimize(self):
      model = ConcreteModel()
      model.consts=ConstraintList()
        

      num_of_voucher=len(self.vouchers)# equal to number of bill we apply
      
      num_of_order=len(self.orders)

      model.shippings=RangeSet(0, NUMBER_OF_BILL_SPLITTED-1)
      model.vShippings=Var(model.shippings,domain=Binary) 

      model.DiscountType =RangeSet(0,num_of_voucher-1)

      model.Orders = RangeSet(0,num_of_order-1)        
      model.vOrders=Var(model.Orders,domain=NonNegativeReals)
        
      model.VoucherApplied = RangeSet(0, NUMBER_OF_BILL_SPLITTED-1)
      model.vVoucherApplied=Var(model.VoucherApplied,domain=NonNegativeReals) 
      
      model.bValueApply=Var(model.VoucherApplied*model.DiscountType*model.DiscountType ,domain=Binary)
      model.vValueApply=Var(model.VoucherApplied*model.DiscountType*model.DiscountType ,domain=NonNegativeReals)
      
      model.max_lim=RangeSet(0,1)
      model.bMaxLim=Var(model.VoucherApplied*model.DiscountType*model.DiscountType  ,domain=Binary)
      model.vMaxLim=Var(model.VoucherApplied*model.DiscountType*model.DiscountType * model.max_lim ,domain=NonNegativeReals)
      
      

      for k in model.VoucherApplied:
         for i in model.DiscountType :
            for j in RangeSet(0,i):
               voucher_j:Voucher=self.vouchers[j]

               model.consts.add(model.vValueApply[k,i,j] * voucher_j.percent == sum(model.vMaxLim[k,i,j,l] for l in model.max_lim) )
               model.consts.add( model.vMaxLim[k,i,j,0]<=voucher_j.max_applied)
               model.consts.add( voucher_j.max_applied *  model.bMaxLim[k,i,j] <= model.vMaxLim[k,i,j,0] )
               model.consts.add( model.vMaxLim[k,i,j,1]<=model.bMaxLim[k,i,j] * INF)
      
      for k in model.VoucherApplied:
         for i in model.DiscountType :
            for j in RangeSet(0,i):
               voucher_i:Voucher=self.vouchers[i]

               model.consts.add( voucher_i.range_from *   model.bValueApply[k,i,j]    <= model.vValueApply[k,i,j]  )
               model.consts.add(           model.vValueApply[k,i,j] <= voucher_i.range_to *  model.bValueApply[k,i,j] )
      
         model.consts.add(1== sum(model.bValueApply[k,i,j] for i in model.DiscountType for j in RangeSet(0,i) ))
      
         model.consts.add(model.vVoucherApplied[k] == sum(model.vValueApply[k,i,j] for i in model.DiscountType for j in RangeSet(0,i) ))


 
 
 
      model.vDiscountType=Var(model.DiscountType,domain=NonNegativeReals)
      model.vCrossDishes=Var(model.VoucherApplied * model.Orders ,domain=Binary,bounds=(0,1))
      model.vCrossUseVoucher=Var(model.VoucherApplied*model.DiscountType,domain=Binary,bounds=(0,1))

      model.vListPriceBaseOnDiscounted=Var(model.VoucherApplied*model.DiscountType,domain=NonNegativeReals)
 
# each dish pick by one voucher
      for i in model.Orders:
         model.consts.add(sum(model.vCrossDishes[j,i] for j in model.VoucherApplied)==1)
 
#each voucer apply for one type of bill ex from #if 50 ->100 discount 10  #if 100 ->200 discount 20 #if 200 ->500 discount 50
      for i in model.VoucherApplied:
         model.consts.add( sum(  model.vCrossUseVoucher[i,j] for j in model.DiscountType)<=1)
         model.consts.add( sum(  model.vCrossUseVoucher[i,j] for j in model.DiscountType)>=0)
 
 
#may be no need to use ######################
      for i in model.VoucherApplied:
         model.consts.add(sum(model.vListPriceBaseOnDiscounted[i,j] for j in model.DiscountType)==sum(model.vCrossDishes[i,j]* self.orders[j].price for j in model.Orders ))
##################################################################
 
 
     # model.total=Var(domain=NonNegativeReals)
      model.amountOfDiscounted=Var(domain=NonNegativeReals)
     # model.consts.add(model.total==self.shipping_fee * num_of_voucher + sum(model.vListPriceBaseOnDiscounted[i,j]  for j in model.DiscountType for i in model.VoucherApplied))
 
 
 
      model.ab=RangeSet(0,1)
      model.vVDA=Var(model.VoucherApplied*model.DiscountType*model.ab,domain=NonNegativeReals )
      model.vBooleanAB=Var(model.VoucherApplied*model.DiscountType,domain=Binary )
      for i in model.VoucherApplied:
         model.consts.add(model.vVoucherApplied[i]  ==  sum(model.vListPriceBaseOnDiscounted[i,j]  for j in model.DiscountType) )
      
      for shipping_index in model.shippings:
         model.consts.add(sum(model.vCrossDishes[shipping_index,j1]  for j1 in  model.Orders) <=model.vShippings[shipping_index]*INF)

      
      model.discountedVal=Objective(expr=  sum(model.vMaxLim[k,i,j,0] for k in model.VoucherApplied for i in model.DiscountType  for j in RangeSet(0,i) ) - sum(self.shipping_fee * model.vShippings[vship] for vship in model.shippings ),sense=maximize)
 

      SolverFactory('scip', executable='/usr/local/bin/scipampl').solve(model).write()
 
      # kk=sum(self.shipping_fee * model.vShippings[vship]() for vship in model.shippings )
      # print(kk)
      # print(model.discountedVal())
      
      # for i in model.VoucherApplied:
      #    print("bill",i)
      #    for j in model.Orders:
      #       print("order",model.vCrossDishes[i,j]())

      bills=[]
      total_discounted=0
      for i in model.VoucherApplied:
            
         list_of_order_id=[]
         total_bill_i=0
         total_discounted_bill_i=0
         
         for j in model.Orders:
            order_j:Order=self.orders[j]
            if(0!=order_j.price*  model.vCrossDishes[i,j]()):
               list_of_order_id.append(order_j.id)
               total_bill_i+=order_j.price
               #print(order_j.price)
                  #sys.stdout.write(" {0} ".format(order_j.price))
         
         for k in model.DiscountType :     
            for jj in RangeSet(0,k):
                   
               if 0!=model.vValueApply[i,k,jj]():
                  value_apply=model.vValueApply[i,k,jj]()
               
               if 0!=model.bValueApply[i,k,jj]():
                  voucher_apply_type=jj

         use_voucher:Voucher=self.vouchers[voucher_apply_type]
         tmp=total_bill_i*use_voucher.percent
         if tmp>=use_voucher.max_applied:
            tmp=use_voucher.max_applied
         total_discounted_bill_i+=tmp

         total_discounted+=total_discounted_bill_i

         respone=BillResponeObject(use_voucher.id,list_of_order_id)
        
         if len(respone.orders)>0:
            bills.append(respone)
         
         print("bill{0} value aplly= {1} voucher_need_to_apply={2} total={3} discount={4}".format(i,list_of_order_id,str(use_voucher.percent),total_bill_i,total_discounted_bill_i))



      shipping_fee=0
      for zz in model.shippings:
         print(model.vShippings[zz]())
         shipping_fee+=model.vShippings[zz]()*self.shipping_fee


      
      total=  shipping_fee+    sum(model.vListPriceBaseOnDiscounted[i,j]()  for j in model.DiscountType for i in model.VoucherApplied)

      print("\n\navailable discounted = %d"%(total_discounted) )
      sys.stdout.write("total:{0} ({1} + {2} of shipping)".format(total,total-shipping_fee, shipping_fee))
      print("pecent =  %.3f (pecents) "%(total_discounted/total *100))
      print("\nCrossDishes")

      discounted_fee=total_discounted


      billrespone=BillRespone(bills,total=total,discounted= discounted_fee,shiping=shipping_fee)
      

      return billrespone.getJSONObject()
      # for k in model.VoucherApplied:
      #    order_ids=[]
      #    voucher_id=""   
         
         

      #    value_apply=-1
      #    voucher_apply_type=-1
      #    for i in model.DiscountType :     
      #       for j in RangeSet(0,i):
      #          if 0!=model.vValueApply[k,i,j]():
      #             value_apply=model.vValueApply[k,i,j]()
               
      #          if 0!=model.bValueApply[k,i,j]():
      #             voucher_apply_type=j
      #          #sys.stdout.write(" (%d .. %.2f) "%(model.vValueApply[k,i,j](),model.bValueApply[k,i,j]() ))
         
      #    use_voucher:Voucher=self.vouchers[voucher_apply_type]
      #    voucher_detail=use_voucher.getJSON()
      #    print("bill{0} value aplly= {1} voucher_need_to_apply={2}".format(k,value_apply,voucher_detail))

voucher0=Voucher("0",0.0001,0,50,0.0001)
voucher1=Voucher("1",0.15,50,INF,10)
voucher2=Voucher("2",0.45,100,INF,50)
voucher3=Voucher("3",0.40,200,INF,80)

vouchers=[]
vouchers.append(voucher0)
vouchers.append(voucher1)
vouchers.append(voucher2)
vouchers.append(voucher3)

order0=Order("0","dinh","com",25)
order1=Order("1","dinh","com",35)
order2=Order("2","dinh","com",42)
order3=Order("3","dinh","com",51)
order4=Order("4","dinh","com",61)
order5=Order("5","dinh","com",100)

orders=[]
orders.append(order0)
orders.append(order1)
orders.append(order2)
orders.append(order3)
orders.append(order4)
orders.append(order5)


shiping_fee=20
opimizer=BillOptimizer(shiping_fee,orders,vouchers)
opimizer.optimize()