mp=dict()

payment_methods=dict()

shops=dict()
carts=dict()


class KEYS:
    CMD_ROLE = 'cmd_role'
    EMBED_COLOR = 'embed_color'
    
def set(guild:str,key:str,value):
    global mp
    mp[guild+key]=value

def get(guild:str,key:str):
    global mp
    return mp.get(guild+key)

def getshop(guild_id: str,user_id: str):
    print("inside getshop")
    if shops.get(guild_id)==None:return None
    if shops[guild_id].get(user_id)==None: return None
    return shops[guild_id][user_id]
    return

def writeshop(guild_id: str,user_id:str,data):
    print("inside writeshop")
    if shops.get(guild_id)==None:shops[guild_id]=dict()
    shops[guild_id][user_id]=data
    return

def add_item(guild_id,user_id,data,item_name,item):
    print("inside add_item")
    if data.get("items")==None:data["items"]=dict()
    data["items"][item_name]=item
    writeshop(guild_id, user_id, data)
    return

def remove_item(guild_id,user_id,data,item_name):
    print("inside remove item")
    if data.get("items")==None or data["items"].get(item_name)==None:raise Exception(f"No such item {item_name}")
    data["items"].pop(item_name)
    writeshop(guild_id, user_id, data)
    return

def add_stock(guild_id,user_id,item_name,stock):
    data = getshop(guild_id, user_id)
    if data==None or data.get("items")==None or data["items"].get(item_name)==None:raise Exception(f"No such item {item_name}")
    item=data["items"][item_name]
    amount=item[1]
    if amount==1000000:amount=0
    amount = amount+stock
    item[1]=amount
    data["items"][item_name]=item
    writeshop(guild_id, user_id, data)
    return

def remove_stock(guild_id,user_id,item_name,stock):
    data = getshop(guild_id, user_id)
    if data==None or data.get("items")==None or data["items"].get(item_name)==None:raise Exception(f"No such item {item_name}")
    item=data["items"][item_name]
    amount=item[1]
    if amount==1000000:amount=0
    amount = amount-stock
    if amount<0:raise Exception(f"Stocks cannot go below 0")
    item[1]=amount
    data["items"][item_name]=item
    writeshop(guild_id, user_id, data)
    return