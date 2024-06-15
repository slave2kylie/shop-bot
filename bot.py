from typing import Optional, Union, List

import discord
import os
from discord import app_commands
from dotenv import load_dotenv
from discord.ext import commands
import random
import db

load_dotenv()
os.system("color")
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True
client = commands.Bot(intents=intents,command_prefix='/')

def is_owner(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        return True
    else:
        return False

def check_command_permission(interaction: discord.Interaction):
    cmdrole = db.get(str(interaction.guild_id),db.KEYS.CMD_ROLE)
    for role in interaction.user.roles:
        if(role.name == cmdrole):
            return True
    return False

async def item_autocomplete(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    keys=[]
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    data = db.getshop(guild_id, user_id)
    if data!=None and data.get('items')!=None:
        for k,v in data['items'].items():
            keys.append(k)
    print(f"keys:{keys}")
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in keys if current.lower() in msg.lower()
    ]

async def item_autocomplete_ns(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    keys=[]
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.namespace.user.id)
    data = db.getshop(guild_id, user_id)
    if data!=None and data.get('items')!=None:
        for k,v in data['items'].items():
            keys.append(k)
    print(f"keys:{keys}")
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in keys if current.lower() in msg.lower()
    ]


async def item_autocomplete_cart(interaction: discord.Interaction,current: str) -> List[app_commands.Choice[str]]:
    keys=[]
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    data = dict()
    if db.carts.get(guild_id)!=None and db.carts[guild_id].get(user_id)!=None:
        data=db.carts[guild_id][user_id]

    if data!=None and data.get('items')!=None:
        for k,v in data['items'].items():
            keys.append(k)
    print(f"keys:{keys}")
    return [
        app_commands.Choice(name=msg, value=msg)
        for msg in keys if current.lower() in msg.lower()
    ]


@client.tree.command(name='setup')
@app_commands.check(is_owner)
async def setup(interaction: discord.Interaction,embed_color: str,role: discord.Role):
    """Set up shop bot for this server"""
    await interaction.response.defer(ephemeral=True)
    print("inside setup")
    embed_color="0x"+embed_color
    embed_color_int=int(embed_color,16)
    role_name=role.name
    guild_id=str(interaction.guild_id)
    db.set(guild_id,db.KEYS.EMBED_COLOR,embed_color_int)
    db.set(guild_id,db.KEYS.CMD_ROLE,role_name)
    print(db.get(guild_id,db.KEYS.CMD_ROLE))
    print(db.get(guild_id,db.KEYS.EMBED_COLOR))
    await interaction.followup.send('Set up complete',ephemeral=True)
    return

@setup.error
async def setup_error(interaction: discord.Interaction,error):
    print("setup_error",error)
    await interaction.response.send_message("Only the server owner can access this command",ephemeral=True)
    return


def get_shop_keys(interaction: discord.Interaction):
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    return guild_id,user_id

def get_shop_data(interaction: discord.Interaction):
    guild_id,user_id=get_shop_keys(interaction)
    shop_data=db.getshop(guild_id, user_id)
    return guild_id, user_id, shop_data

@client.tree.command(name="setup-shop")
@app_commands.checks.has_role("Domme")
async def setup_shop(interaction: discord.Interaction,name: str,header:str):
    """Set up a shop for a user"""
    await interaction.response.defer(ephemeral=True)
    print("inside setup_shop")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    shop_data=db.getshop(guild_id, user_id)
    if shop_data!=None:
        await interaction.followup.send("Shop already created fot this user")
        return
    shop_data=dict()
    shop_data["name"]=name
    shop_data["header"]=header
    db.writeshop(guild_id, user_id, shop_data)
    await interaction.followup.send("Created a shop for this user")
    return

@setup_shop.error
async def setup_shop_error(interaction: discord.Interaction,error):
    print("inside setup_shop_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

async def shop_name_base(interaction,guild_id,user_id,shop_data,name):
    if shop_data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    shop_data["name"]=name
    db.writeshop(guild_id, user_id, shop_data)
    await interaction.followup.send("Updated shop name")
    return

@client.tree.command(name="shop-name")
@app_commands.checks.has_role("Domme")
async def shop_name(interaction:discord.Interaction,name: str):
    """ Set the name for your shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside shop_name")
    guild_id, user_id, shop_data = get_shop_data(interaction)
    await shop_name_base(interaction,guild_id, user_id, shop_data, name)
    return

@shop_name.error
async def shop_name_error(interaction: discord.Interaction,error):
    print("inside shop_name_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return


@client.tree.command(name="admin-shop-name")
@app_commands.check(check_command_permission)
async def admin_shop_name(interaction:discord.Interaction,user: discord.Member,name: str):
    """Admin change shop name"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_shop_name")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    shop_data=db.getshop(guild_id, user_id)
    await shop_name_base(interaction,guild_id, user_id, shop_data, name)
    return

@admin_shop_name.error
async def admin_shop_name_error(interaction: discord.Interaction,error):
    print("inside admin_shop_name_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

async def change_header_base(interaction,guild_id,user_id,shop_data,header):
    if shop_data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    shop_data["header"]=header
    db.writeshop(guild_id, user_id, shop_data)
    await interaction.followup.send("Updated shop header")


@client.tree.command(name="change-header")
@app_commands.checks.has_role("Domme")
async def change_header(interaction:discord.Interaction,header: str):
    """ Set the header for your shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside change_header")
    guild_id, user_id, shop_data = get_shop_data(interaction)
    await change_header_base(interaction, guild_id, user_id, shop_data, header)
    return

@change_header.error
async def change_header_error(interaction: discord.Interaction,error):
    print("inside change_header_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-change-header")
@app_commands.check(check_command_permission)
async def admin_change_header(interaction:discord.Interaction,user: discord.Member,header: str):
    """Set the header of a user's shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_change_header")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    shop_data=db.getshop(guild_id, user_id)
    await change_header_base(interaction, guild_id, user_id, shop_data, header)
    return

@admin_change_header.error
async def admin_change_header_error(interaction: discord.Interaction,error):
    print("inside admin_change_header_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return


async def clear_shop_base(interaction,guild_id,user_id,shop_data):
    if shop_data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    new_data=dict()
    new_data["name"]=shop_data["name"]
    new_data["header"]=shop_data["header"]
    db.writeshop(guild_id, user_id, new_data)
    await interaction.followup.send("Cleared all items")
    return

@client.tree.command(name="clear-shop")
@app_commands.checks.has_role("Domme")
async def clear_shop(interaction: discord.Interaction):
    """Clear all data from your shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside clear_shop")
    guild_id, user_id, shop_data = get_shop_data(interaction)
    await clear_shop_base(interaction, guild_id, user_id, shop_data)
    return

@clear_shop.error
async def clear_shop_error(interaction: discord.Interaction,error):
    print("inside clear_shop_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-clear-shop")
@app_commands.check(check_command_permission)
async def admin_clear_shop(interaction: discord.Interaction,user: discord.Member):
    """Clear all data from a shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_clear_shop")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    shop_data=db.getshop(guild_id, user_id)
    await clear_shop_base(interaction, guild_id, user_id, shop_data)
    return

@admin_clear_shop.error
async def admin_clear_shop_error(interaction: discord.Interaction,error):
    print("inside admin_clear_shop_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

async def add_item_base(interaction,guild_id,user_id,shop_data,name,price,stock):
    if shop_data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    item=[price,stock]
    db.add_item(guild_id, user_id, shop_data, name, item)
    await interaction.followup.send("Item added to shop")

@client.tree.command(name="add-item")
@app_commands.checks.has_role("Domme")
async def add_item(interaction: discord.Interaction,name: str,price: int,stock: Optional[int]=1000000):
    """ Add an item to your shop """
    await interaction.response.defer(ephemeral=True)
    print("inside add_item")
    guild_id, user_id, shop_data = get_shop_data(interaction)
    await add_item_base(interaction, guild_id, user_id, shop_data, name, price, stock)
    return

@add_item.error
async def add_item_error(interaction: discord.Interaction,error):
    print("inside add_item_error")
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-add-item")
@app_commands.check(check_command_permission)
async def admin_add_item(interaction: discord.Interaction,user: discord.Member,name: str,price: int,stock: Optional[int]=1000000):
    """ Add an item to a shop """
    await interaction.response.defer(ephemeral=True)
    print("inside admin_add_item")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    shop_data=db.getshop(guild_id, user_id)
    await add_item_base(interaction, guild_id, user_id, shop_data, name, price, stock)
    return

@admin_add_item.error
async def admin_add_item_error(interaction: discord.Interaction,error):
    print("inside admin_add_item_error")
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

async def remove_item_base(interaction,guild_id,user_id,shop_data,item_name):
    if shop_data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    try:
        db.remove_item(guild_id, user_id, shop_data, item_name)
    except Exception as e:
        await interaction.followup.send(e)
        return
    await interaction.followup.send("Item removed from shop")
    return

@client.tree.command(name="remove-item")
@app_commands.autocomplete(item_name=item_autocomplete)
@app_commands.checks.has_role("Domme")
async def remove_item(interaction: discord.Interaction,item_name: str):
    """Remove an item from your shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside remove_item")
    guild_id, user_id, shop_data = get_shop_data(interaction)
    await remove_item_base(interaction, guild_id, user_id, shop_data, item_name)
    return

@remove_item.error
async def remove_item_error(interaction: discord.Interaction,error):
    print("inside remove_item_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-remove-item")
@app_commands.autocomplete(item_name=item_autocomplete_ns)
@app_commands.check(check_command_permission)
async def admin_remove_item(interaction: discord.Interaction,user: discord.Member,item_name: str):
    """Remove an item from a shop"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_remove_item")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    shop_data=db.getshop(guild_id, user_id)
    await remove_item_base(interaction, guild_id, user_id, shop_data, item_name)
    return

@admin_remove_item.error
async def admin_remove_item_error(interaction: discord.Interaction,error):
    print("inside admin_remove_item_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

async def add_stock_base(interaction,guild_id,user_id,item_name,amount):
    try:
        db.add_stock(guild_id, user_id, item_name, amount)
    except Exception as e:
        await interaction.followup.send(e)
        return
    await interaction.followup.send("Stocks added to item")
    return

@client.tree.command(name="add-stock")
@app_commands.autocomplete(item_name=item_autocomplete)
@app_commands.checks.has_role("Domme")
async def add_stock(interaction: discord.Interaction,item_name: str,amount: int):
    """Add stock to item"""
    await interaction.response.defer(ephemeral=True)
    print("inside add_stock")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    await add_stock_base(interaction, guild_id, user_id, item_name, amount)
    return

@add_stock.error
async def add_stock_error(interaction: discord.Interaction,error):
    print("inside add_stock_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-add-stock")
@app_commands.autocomplete(item_name=item_autocomplete_ns)
@app_commands.check(check_command_permission)
async def admin_add_stock(interaction: discord.Interaction,user:discord.Member,item_name: str,amount: int):
    """Add stock to item"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_add_stock")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    await add_stock_base(interaction, guild_id, user_id, item_name, amount)
    return

@admin_add_stock.error
async def admin_add_stock_error(interaction: discord.Interaction,error):
    print("inside admin_add_stock_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

async def remove_stock_base(interaction,guild_id,user_id,item_name,amount):
    try:
        db.remove_stock(guild_id, user_id, item_name, amount)
    except Exception as e:
        await interaction.followup.send(e)
        return
    await interaction.followup.send("Stocks removed from item")
    return

@client.tree.command(name="remove-stock")
@app_commands.autocomplete(item_name=item_autocomplete)
@app_commands.checks.has_role("Domme")
async def remove_stock(interaction: discord.Interaction,item_name: str,amount: int):
    """Remove stock from item"""
    await interaction.response.defer(ephemeral=True)
    print("inside remove_stock")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    await remove_stock_base(interaction, guild_id, user_id, item_name, amount)
    return

@remove_stock.error
async def remove_stock_error(interaction: discord.Interaction,error):
    print("inside remove_stock_error",error)
    await interaction.response.send_message("You need to be a Domme to perform this command",ephemeral=True)
    return

@client.tree.command(name="admin-remove-stock")
@app_commands.autocomplete(item_name=item_autocomplete_ns)
@app_commands.check(check_command_permission)
async def admin_remove_stock(interaction: discord.Interaction,user:discord.Member,item_name: str,amount: int):
    """Remove stock from item"""
    await interaction.response.defer(ephemeral=True)
    print("inside admin_remove_stock")
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    await remove_stock_base(interaction, guild_id, user_id, item_name, amount)
    return

@admin_remove_stock.error
async def admin_remove_stock_error(interaction: discord.Interaction,error):
    print("inside admin_remove_stock_error",error)
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

@client.tree.command(name="add-to-cart")
@app_commands.autocomplete(item_name=item_autocomplete_ns)
@app_commands.checks.has_role("Sub")
async def add_to_cart(interaction: discord.Interaction,user: discord.Member,item_name:str,amount: Optional[int]=1):
    await interaction.response.defer(ephemeral=True)
    print("inside add_to_cart")
    guild_id,user_id=get_shop_keys(interaction)
    dom_id=str(user.id)
    if db.carts.get(guild_id)==None:db.carts[guild_id]=dict()
    if db.carts[guild_id].get(user_id)==None:db.carts[guild_id][user_id]=dict()
    if db.carts[guild_id][user_id].get("domme")==None:db.carts[guild_id][user_id]["domme"]=dom_id
    if db.carts[guild_id][user_id]["domme"]!=dom_id:
        await interaction.followup.send("You can only add items from one domme at a time to cart")
        return
    dom_data=db.getshop(guild_id,dom_id)
    if dom_data.get("items")==None or dom_data["items"].get(item_name)==None:
        await interaction.followup.send("There is no such item in the shop")
        return
    if db.carts[guild_id][user_id].get("items")==None:db.carts[guild_id][user_id]["items"]=dict()
    cnt = 0
    if db.carts[guild_id][user_id]["items"].get(item_name)!=None:cnt=db.carts[guild_id][user_id]["items"][item_name]
    rcnt =cnt+amount
    acnt=dom_data["items"][item_name][1]
    if acnt<rcnt:
        await interaction.followup.send("There arent enough stocks for the item")
        return
    db.carts[guild_id][user_id]["items"][item_name]=rcnt
    await interaction.followup.send("The item has been added to the cart")
    return

@add_to_cart.error
async def add_to_cart_error(interaction: discord.Interaction,error):
    print("inside add_to_cart_error",error)
    await interaction.response.send_message("You need to be a Sub to perform this command",ephemeral=True)
    return

@client.tree.command(name="remove-from-cart")
@app_commands.autocomplete(item_name=item_autocomplete_cart)
@app_commands.checks.has_role("Sub")
async def remove_from_cart(interaction: discord.Interaction,item_name:str,amount: Optional[int]=1):
    await interaction.response.defer(ephemeral=True)
    print("inside remove_from_cart")
    guild_id,user_id=get_shop_keys(interaction)
    if db.carts.get(guild_id)==None or db.carts[guild_id].get(user_id)==None or db.carts[guild_id][user_id].get("items")==None:
        await interaction.followup.send("Cart is already empty")
        return
    if db.carts[guild_id][user_id]["items"].get(item_name)==None:
        await interaction.followup.send("There is no such item in the cart")
        return
    amnt=db.carts[guild_id][user_id]["items"][item_name]
    if amnt<amount:
        await interaction.followup.send("Cannot remove more items than present in the cart")
        return
    if amnt==amount:
        db.carts[guild_id][user_id]["items"].pop(item_name)
    else:
        db.carts[guild_id][user_id]["items"][item_name]=amnt-amount
    await interaction.followup.send(f"Removed the item by {amount} from the cart")
    return

@remove_from_cart.error
async def remove_from_cart_error(interaction: discord.Interaction,error):
    print("Inside remove_from_cart_error",error)
    await interaction.response.send_message("You need to be a Sub to perform this command",ephemeral=True)
    return

@client.tree.command()
@app_commands.checks.has_role("Sub")
async def roulette(interaction: discord.Interaction,user: discord.Member,budget: Optional[int]=1000000):
    await interaction.response.defer(ephemeral=True)
    print("inside roulette")
    guild_id,user_id=get_shop_keys(interaction)
    dom_id=str(user.id)
    if db.carts.get(guild_id)==None:db.carts[guild_id]=dict()
    if db.carts[guild_id].get(user_id)==None:db.carts[guild_id][user_id]=dict()
    if db.carts[guild_id][user_id].get("items")==None:db.carts[guild_id][user_id]["items"]=dict()
    if db.carts[guild_id][user_id].get("domme")!=None and db.carts[guild_id][user_id]["domme"]!=dom_id:
        await interaction.followup.send("Cart is set to an other domme.Please clear cart before trying this operation")
        return

    dom_data=db.getshop(guild_id, dom_id)
    if dom_data==None or dom_data.get("items")==None:
        await interaction.followup.send("There are no items in the shop for the user")
        return

    flist=[]
    for k,v in dom_data["items"].items():
        if v[0]<=budget:
            cv=0
            if db.carts[guild_id][user_id]["items"].get(k)!=None:
                cv=db.carts[guild_id][user_id]["items"][k]
            if cv<v[1]:
                flist.append(k)
    if len(flist)==0:
        await interaction.followup.send("can't add any item within budget")
        return
    db.carts[guild_id][user_id]["domme"]=dom_id
    key=flist[random.randint(0,len(flist)-1)]
    if db.carts[guild_id][user_id]["items"].get(key)==None:
        db.carts[guild_id][user_id]["items"][key]=1
    else:
        db.carts[guild_id][user_id]["items"][key]+=1
    await interaction.followup.send("Added a random item from the user")
    return

@roulette.error
async def roulette_error(interaction: discord.Interaction,error):
    print("Inside roulette_error",error)
    await interaction.response.send_message("You need to be a Sub to perform this command",ephemeral=True)
    return

@client.tree.command(name="clear-cart")
@app_commands.checks.has_role("Sub")
async def clear_cart(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    print("inside clear_cart")
    guild_id,user_id=get_shop_keys(interaction)
    if db.carts.get(guild_id)!=None and db.carts[guild_id].get(user_id)!=None:
        db.carts[guild_id].pop(user_id)
    await interaction.followup.send("Cleared cart")
    return

@clear_cart.error
async def clear_cart_error(interaction: discord.Interaction,error):
    print("inside clear_cart_error",error)
    await interaction.response.send_message("You need to be a Sub to perform this command",ephemeral=True)
    return


@client.tree.command()
@app_commands.checks.has_role("Sub")
async def cart(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    print("inside cart")
    guild_id,user_id=get_shop_keys(interaction)
    embed=discord.Embed(color=db.get(guild_id,db.KEYS.EMBED_COLOR),title="Cart")
    if db.carts.get(guild_id)==None or db.carts[guild_id].get(user_id)==None or db.carts[guild_id][user_id].get("items")==None:
        embed.description="> Cart is empty"
        await interaction.followup.send(embed=embed)
        return
    dom_id=db.carts[guild_id][user_id]["domme"]
    dom_data=db.getshop(guild_id, dom_id)
    total=0
    for k,v in db.carts[guild_id][user_id]["items"].items():
        if dom_data.get("items")==None or dom_data["items"].get(k)==None:
            await interaction.followup.send(f"There is no item {k} in the shop")
            return
        item=dom_data["items"][k]
        total+=item[0]*v
        embed.add_field(name=f"{k}({v})", value=f"> {item[0]*v}$",inline=False)
    embed.add_field(name="Total", value=f"> {total}$",inline=False)
    await interaction.followup.send(embed=embed)
    return

@cart.error
async def cart_error(interaction: discord.Interaction,error):
    print("inside cart_error",error)
    await interaction.response.send_message("You need to be a Sub to perform this command",ephemeral=True)
    return

@client.tree.command(name="view-shop")
async def view_shop(interaction: discord.Interaction,member: discord.Member):
    """View shop details of a user"""
    await interaction.response.defer(ephemeral=True)
    print("inside view_shop")
    guild_id=str(interaction.guild_id)
    user_id=str(member.id)
    data=db.getshop(guild_id, user_id)
    if data==None:
        await interaction.followup.send("There is no shop created for this user")
        return
    embed=discord.Embed(color=db.get(guild_id,db.KEYS.EMBED_COLOR),title=data["header"])
    embed.description=data["name"]
    #embed.description="\033[94m Hello \033[0m"
    if data.get("items") !=None:
        for k,v in data["items"].items():
            if k!= "name" and k!="header":
                if v[1]!=1000000:
                    embed.add_field(name=k, value=f"price :{v[0]},stock:{v[1]}",inline=False)
                else:
                    embed.add_field(name=k, value=f"price :{v[0]}",inline=False)
    await interaction.followup.send(embed=embed)
    return

@client.tree.command(name="add-payment-link")
@app_commands.check(check_command_permission)
async def add_payment_link(interaction:discord.Interaction,payment_method:str,payment_link:str):
    """Add a payment link"""
    await interaction.response.defer(ephemeral=True)
    print("inside add_payment_link")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    if db.payment_methods.get(guild_id)==None: db.payment_methods[guild_id]=dict()
    if db.payment_methods[guild_id].get(user_id)==None: db.payment_methods[guild_id][user_id]=dict()
    db.payment_methods[guild_id][user_id][payment_method]=payment_link
    await interaction.followup.send(f'Payment method {payment_method} has been added',ephemeral=True)
    return

@add_payment_link.error
async def add_payment_link_error(interaction: discord.Interaction,error):
    print('inside add_payment_link_error')
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

@client.tree.command(name='remove-payment-link')
@app_commands.check(check_command_permission)
async def remove_payment_link(interaction:discord.Interaction,payment_method:str):
    """Remove payment link"""
    await interaction.response.defer(ephemeral=True)
    print("inside remove_payment_link")
    guild_id=str(interaction.guild_id)
    user_id=str(interaction.user.id)
    if db.payment_methods.get(guild_id)==None or db.payment_methods[guild_id].get(user_id)==None or db.payment_methods[guild_id][user_id].get(payment_method)==None:
        await interaction.followup.send("There is no such payment method set",ephemeral=True)
        return
        
    db.payment_methods[guild_id][user_id].pop(payment_method)
    await interaction.followup.send(f'Payment method {payment_method} removed',ephemeral=True)
    return

@remove_payment_link.error
async def remove_payment_link_error(interaction: discord.Interaction,error):
    print('inside remove_payment_link_error')
    await interaction.response.send_message("You do not have permission for this command",ephemeral=True)
    return

@client.tree.command()
async def links(interaction:discord.Interaction,user: discord.Member):
    """Get the payment method links"""
    await interaction.response.defer(ephemeral=True)
    print('inside links')
    guild_id=str(interaction.guild_id)
    user_id=str(user.id)
    if db.payment_methods.get(guild_id)==None: db.payment_methods[guild_id]=dict()
    if db.payment_methods[guild_id].get(user_id)==None:db.payment_methods[guild_id][user_id]=dict()
    nm=user.nick
    if nm==None:nm=user.name
    tm=f"{nm}**'s Payment Methods**"
    if len(db.payment_methods[guild_id][user_id])==0: tm="This user has not added any payment methods"
    embed=discord.Embed(color=db.get(guild_id,db.KEYS.EMBED_COLOR),title=tm)
    for k,v in db.payment_methods[guild_id][user_id].items():
        embed.add_field(name=k, value=v,inline=False)
    await interaction.followup.send(embed=embed,ephemeral=True)
    return

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

    #print(cmdrole)
    #client.tree = app_commands.CommandTree(client)
    for guild in client.guilds:
        print("id: ",guild.id,"name: ",guild.name)
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
    return

@client.event
async def on_guild_join(guild):
    print("on_guild_join")
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    return




client.run(TOKEN)
