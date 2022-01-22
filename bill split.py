from pyomo.environ import *
 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os
import json
 
 
model = ConcreteModel()
model.consts=ConstraintList()
M=102400

 
#pricing= [210]# price for each dishes
pricing= [21,31,41,51,61,100]# price for each dishes
#pricing= [13]# price for each dishes
 
 
discountedRange= {
     0:{'pecent':0.0001  ,'range':{'from':0,'to':50},'max':0.0001}
   , 1:{'pecent':0.15 ,'range':{'from':50,'to':M},'max':10}
   , 2:{'pecent':0.45 ,'range':{'from':100,'to':M},'max':50}
   , 3:{'pecent':0.40 ,'range':{'from':200,'to':M},'max':80}
   }# price for each dishes
 
mVoucher=7# use 3 voucer
mShipingFee=20
 
model.DiscountType =RangeSet(0,len(discountedRange)-1)
model.Dishes = RangeSet(0,len(pricing)-1)
model.vDishes=Var(model.Dishes,domain=NonNegativeReals)
 
model.VoucherApplied = RangeSet(0, mVoucher-1)
 
model.vVoucherApplied=Var(model.VoucherApplied,domain=NonNegativeReals)
###################
 
model.bValueApply=Var(model.VoucherApplied*model.DiscountType*model.DiscountType ,domain=Binary)
model.vValueApply=Var(model.VoucherApplied*model.DiscountType*model.DiscountType ,domain=NonNegativeReals)
 
 
 
 
 
model.max_lim=RangeSet(0,1)
model.bMaxLim=Var(model.VoucherApplied*model.DiscountType*model.DiscountType  ,domain=Binary)
model.vMaxLim=Var(model.VoucherApplied*model.DiscountType*model.DiscountType * model.max_lim ,domain=NonNegativeReals)
 
 
for k in model.VoucherApplied:
   for i in model.DiscountType :
       for j in RangeSet(0,i):
           model.consts.add(model.vValueApply[k,i,j] * discountedRange[j]["pecent"] == sum(model.vMaxLim[k,i,j,l] for l in model.max_lim) )
           model.consts.add( model.vMaxLim[k,i,j,0]<=discountedRange[j]['max'])
           model.consts.add( discountedRange[j]['max'] *  model.bMaxLim[k,i,j] <= model.vMaxLim[k,i,j,0] )
           model.consts.add( model.vMaxLim[k,i,j,1]<=model.bMaxLim[k,i,j] * M)
          
 
for k in model.VoucherApplied:
   for i in model.DiscountType :
       for j in RangeSet(0,i):
           model.consts.add( discountedRange[i]["range"]["from"] *   model.bValueApply[k,i,j]    <= model.vValueApply[k,i,j]  )
           model.consts.add(           model.vValueApply[k,i,j] <= discountedRange[i]["range"]["to"] *  model.bValueApply[k,i,j] )
 
   model.consts.add(1== sum(model.bValueApply[k,i,j] for i in model.DiscountType for j in RangeSet(0,i) ))
 
   model.consts.add(model.vVoucherApplied[k] == sum(model.vValueApply[k,i,j] for i in model.DiscountType for j in RangeSet(0,i) ))
 
###################
 
 
 
model.vDiscountType=Var(model.DiscountType,domain=NonNegativeReals)
model.vCrossDishes=Var(model.VoucherApplied * model.Dishes ,domain=Binary,bounds=(0,1))
model.vCrossUseVoucher=Var(model.VoucherApplied*model.DiscountType,domain=Binary,bounds=(0,1))
 
model.vListPriceBaseOnDiscounted=Var(model.VoucherApplied*model.DiscountType,domain=NonNegativeReals)
 
# each dish pick by one voucher
for i in model.Dishes:
   model.consts.add(sum(model.vCrossDishes[j,i] for j in model.VoucherApplied)==1)
 
#each voucer apply for one type of bill ex from #if 50 ->100 discount 10  #if 100 ->200 discount 20 #if 200 ->500 discount 50
for i in model.VoucherApplied:
   model.consts.add( sum(  model.vCrossUseVoucher[i,j] for j in model.DiscountType)<=1)
   model.consts.add( sum(  model.vCrossUseVoucher[i,j] for j in model.DiscountType)>=0)
 
 
#may be no need to use ######################
for i in model.VoucherApplied:
   model.consts.add(sum(model.vListPriceBaseOnDiscounted[i,j] for j in model.DiscountType)==sum(model.vCrossDishes[i,j]*pricing[j] for j in model.Dishes ))
##################################################################
 
 
model.total=Var(domain=NonNegativeReals)
model.amountOfDiscounted=Var(domain=NonNegativeReals)
model.consts.add(model.total== mShipingFee * mVoucher + sum(model.vListPriceBaseOnDiscounted[i,j]  for j in model.DiscountType for i in model.VoucherApplied))
 
 
 
model.ab=RangeSet(0,1)
model.vVDA=Var(model.VoucherApplied*model.DiscountType*model.ab,domain=NonNegativeReals )
model.vBooleanAB=Var(model.VoucherApplied*model.DiscountType,domain=Binary )
for i in model.VoucherApplied:
   model.consts.add(model.vVoucherApplied[i]  ==  sum(model.vListPriceBaseOnDiscounted[i,j]  for j in model.DiscountType) )
 
model.discountedVal=Objective(expr=sum(model.vMaxLim[k,i,j,0] for k in model.VoucherApplied for i in model.DiscountType  for j in RangeSet(0,i) ),sense=maximize)
 
#SolverFactory('ipopt').solve(model).write()
#SolverFactory('scip', executable='/Users/truongdinh/Downloads/scipoptsuite-7.0.3/scip/interfaces/ampl/bin/scipampl').solve(model).write()
SolverFactory('scip', executable='/usr/local/bin/scipampl').solve(model).write()
 
print("\n\navailable discounted = %d"%(model.discountedVal()) )
#print("total= %d"%(model.total() , mShipingFee *mShipingFee,)   )
sys.stdout.write("total:{0} ({1} + {2} of shipping)".format(model.total(),model.total()-mShipingFee *mVoucher,mShipingFee *mVoucher))
print("pecent =  %.3f (pecents) "%(model.discountedVal()/model.total() *100))
 
print("\nCrossDishes")
for i in model.VoucherApplied:
   print("\nBill %d total= %d "%(i,sum( pricing[j]*  model.vCrossDishes[i,j]() for j in model.Dishes)))
   for j in model.Dishes:
       if(0!=pricing[j]*  model.vCrossDishes[i,j]()):
            #sys.stdout.write(" {0} ".format(pricing[j]*  model.vCrossDishes[i,j]()))
            sys.stdout.write(" {0} ".format(pricing[j]))
 
 
print("\n----------------------------------")
 
print("\nvListPriceBaseOnDiscounted")
for j in model.DiscountType:
   sys.stdout.write(" {0}-{1} ".format(discountedRange[j]['range']['from'],discountedRange[j]['range']['to']))
 
for i in model.VoucherApplied:
   print("")
   for j in model.DiscountType:
       sys.stdout.write("   {0} ".format(   model.vListPriceBaseOnDiscounted[i,j]()))
       #sys.stdout.write("  %3f "%(model.vListPriceBaseOnDiscounted[i,j]()))
 
print("")
print("")
 
 
# for i in model.VoucherApplied:
#     print("\nuser %d order : "%i)
#     for j in model.Dishes:
#         sys.stdout.write(" dishes {0} - price{1} ".format( j ,(model.vCrossDishes[i,j]()*pricing[j]) ))
#         sys.stdout.write("  {0}  ".format( (model.vCrossDishes[i,j]()*pricing[j]) ))
#     sys.stdout.write("total : {0} discount= {1}".format(sum(model.vCrossDishes[i,j]()*pricing[j] for j in model.Dishes) , sum(model.vVDA[i,k,0]() for k in model.DiscountType   )))
#     print("")
 
 
print("....")
 
 
 

# for k in model.VoucherApplied:
#    print("")
#    for i in model.DiscountType :
#        print("")
#        for j in RangeSet(0,i):
#            sys.stdout.write(" (%d .. %.2f) "%(model.vValueApply[k,i,j](),model.bValueApply[k,i,j]() ))
 

for k in model.VoucherApplied:
   
   value_apply=-1
   voucher_apply_type=-1
   for i in model.DiscountType :     
      for j in RangeSet(0,i):
         if 0!=model.vValueApply[k,i,j]():
            value_apply=model.vValueApply[k,i,j]()
         
         if 0!=model.bValueApply[k,i,j]():
            voucher_apply_type=j
         #sys.stdout.write(" (%d .. %.2f) "%(model.vValueApply[k,i,j](),model.bValueApply[k,i,j]() ))
   
   voucher_detail=json.dumps(discountedRange[voucher_apply_type])
   print("bill{0} value aplly= {1} voucher_need_to_apply={2}".format(k,value_apply,voucher_detail))

   
 
      
 
# for k in model.VoucherApplied:
#    print("")
#    for i in model.DiscountType :
#        print("")
#        for j in RangeSet(0,i):
#            sys.stdout.write(" (%d = %d + %d ) "%(model.vValueApply[k,i,j](),model.vMaxLim[k,i,j,0](),model.vMaxLim[k,i,j,1]() ))
      


