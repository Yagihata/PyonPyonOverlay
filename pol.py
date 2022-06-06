import sys
import discord
from discord import app_commands
import random, string
import time
import os
import threading
import asyncio
import configparser
import json
import traceback

list_width = {} #key->guildID
list_height = {} #key->guildID
list_brightness = {} #key->guildID
list_duration = {} #key->guildID
list_loop = {} #key->guildID
list_enable = {} #key->guildID
list_pixel = {} #key->guildID
list_lastmsg = {} #key->guildID

list_lastcss = {} #key->guildID
list_targetimg = {} #key->guildID
DEFAULT_CONFIG_FILE = 'pol.cfg'
default_config = {
	'list_width': '{}',
	'list_height': '{}',
	'list_brightness': '{}',
	'list_duration': '{}',
	'list_enable': '{}',
	'list_pixel': '{}'
}
config = configparser.ConfigParser(default_config)
try:
	config.read(DEFAULT_CONFIG_FILE)
	list_width = json.loads(config.get('DEFAULT', 'list_width'))
	list_height = json.loads(config.get('DEFAULT', 'list_height'))
	list_brightness = json.loads(config.get('DEFAULT', 'list_brightness'))
	list_duration = json.loads(config.get('DEFAULT', 'list_duration'))
	list_enable = json.loads(config.get('DEFAULT', 'list_enable'))
	list_pixel = json.loads(config.get('DEFAULT', 'list_pixel'))
except:
	traceback.print_exc()

print(discord.__version__)
print(discord.version_info)
print('START => load')

intents = discord.Intents(message_content=True)
client = discord.Client(heartbeat_timeout=6)
tree = app_commands.CommandTree(client)
MY_GUILD_ID = 'GUILD ID'

class pol(app_commands.Group):

	settings = app_commands.Group(name='settings', description='ぴょんぴょんオーバーレイの設定を変更するコマンドです')
	css = app_commands.Group(name='css', description='ぴょんぴょんオーバーレイのCSSを生成するコマンドです')
	@app_commands.command(description='ぴょんぴょんオーバーレイをこのサーバーで有効化します')
	async def enable(self, interaction: discord.Interaction):
		list_enable[str(interaction.guild.id)] = 0
		set_config("list_enable", list_enable)
		await interaction.response.send_message(f"このサーバーでのBOTの使用を有効化しました。")
		print(f"Registered new server -> {interaction.guild.id}")

	@settings.command(description='立ち絵の横幅を設定します')
	@app_commands.describe(value='横幅の値')
	async def width(self, interaction: discord.Interaction, value: int):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("width", value, list_width, "list_width", interaction)

	@settings.command(description='立ち絵の高さを設定します')
	@app_commands.describe(value='高さの値')
	async def height(self, interaction: discord.Interaction, value: int):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("height", value, list_height, "list_height", interaction)

	@settings.command(description='喋っていないときの立ち絵の明るさを設定します')
	@app_commands.describe(value='明るさの値(0~100)')
	async def brightness(self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("brightness", value, list_brightness, "list_brightness", interaction)

	@settings.command(description='跳ねるのにかかる時間をミリ秒単位で設定します')
	@app_commands.describe(value='ミリ秒の値')
	async def duration(self, interaction: discord.Interaction, value: int):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("duration", value, list_duration, "list_duration", interaction)

	@settings.command(description='跳ねる高さをピクセル単位で設定します')
	@app_commands.describe(value='ジャンプする高さのピクセル数')
	async def pixel(self, interaction: discord.Interaction, value: int):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("pixel", value, list_pixel, "list_pixel", interaction)

	@settings.command(description='跳ねる動作が喋っている間ループするかを設定します')
	@app_commands.describe(value='Trueでループさせる/Falseで一度のみ')
	async def loop(self, interaction: discord.Interaction, value: bool):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		await config_cmd("loop", value, list_loop, "list_loop", interaction)

	@app_commands.command(description='オーバーレイ用のURLを生成します(VC参加時のみ)')
	@app_commands.describe(option='[-n][-name] : 立ち絵の下に名前を表示します')
	async def url(self, interaction: discord.Interaction, option:str=None):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		if(not interaction.user.voice):
			await interaction.response.send_message("VCに参加している状態で使用してください。", ephemeral=True)
			return
		message_str = "```"
		message_str = message_str + "https://streamkit.discord.com/overlay/voice/" + str(interaction.guild.id) + "/" + str(interaction.user.voice.channel.id)
		hidename_str = "?hide_names=true"
		if(option):
			arr = option.split(' ')
			if("-n" in arr or "-name" in arr):
				hidename_str = "?hide_names=false"
		message_str = message_str + hidename_str
		message_str = message_str + "```"
		await interaction.response.send_message(message_str, ephemeral=False)

	@css.command(description='オーバーレイ用のCSSを新しく生成します')
	@app_commands.describe(user='喋っているかを取得する対象のユーザー', main_image='立ち絵の画像', sub_image='指定すると、喋っている間立ち絵の画像がこの画像に切り替わります。',option='[-r][-rawimg] : 立ち絵の画像のサイズを元のサイズにします')
	async def new(self, interaction: discord.Interaction, user: discord.Member, main_image: discord.Attachment, sub_image: discord.Attachment=None, option:str=None):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		if(not main_image.content_type.startswith('image/')):
			await interaction.response.send_message("画像のみ添付してください。", ephemeral=True)
			return
		if(sub_image is not None and not sub_image.content_type.startswith('image/')):
			await interaction.response.send_message("画像のみ添付してください。", ephemeral=True)
			return
		await create_css(interaction, user, main_image, sub_image, option)

	@css.command(description='最後に生成したCSSを再生成します')
	@app_commands.describe(option='[-r][-rawimg] : 立ち絵の画像のサイズを元のサイズにします')
	async def last(self, interaction: discord.Interaction, option:str=None):
		if(str(interaction.guild.id) not in list_enable or list_enable[str(interaction.guild.id)] is False):
			await interaction.response.send_message("BOTの使い方は https://negura-karasu.net/archives/1564 を御覧ください。", ephemeral=True)
			return
		if(interaction.guild.id not in list_lastcss):
			await interaction.response.send_message("最後に生成したCSSが見つからないか、存在しません。", ephemeral=True)
			return
		last_data = list_lastcss[interaction.guild.id]
		await create_css(interaction, last_data['user'], last_data['main_image'], last_data['sub_image'], option)

tree.add_command(pol())

async def create_css(interaction: discord.Interaction, user: discord.Member, main_image: discord.Attachment, sub_image: discord.Attachment, option:str):
	arr = []
	if(option is not None):
		arr = option.split(" ")

	width = get_value_from_config(str(interaction.guild.id), list_width, 1000)
	height = get_value_from_config(str(interaction.guild.id), list_height, 1000)
	brightness = get_value_from_config(str(interaction.guild.id), list_brightness, 85)
	duration = get_value_from_config(str(interaction.guild.id), list_duration, 300)
	pixel = get_value_from_config(str(interaction.guild.id), list_pixel, 10)
	loop = "infinite" if get_value_from_config(str(interaction.guild.id), list_loop, False) else "1"
	size = f"?width={width}&height={height}"
	if("-r" in arr or "-rawimg" in arr):
		size = ""
	sub_image_url = ""
	if(sub_image is not None):
		sub_image_url = f"content: url(\"{sub_image.url}{size}\");"
	css = f'''
body {{ background-color: rgba(0, 0, 0, 0); margin: 0px auto; overflow: hidden; }}
li.voice-state:not([data-reactid*=\"{user.id}\"]) {{ display:none; }}
.avatar {{
  content:url(\"{main_image.url}{size}\");
  height:auto !important;
  width:auto !important;
  border-radius:0 !important;
  filter: brightness({brightness}%);
}}
.speaking {{
  border-color:rgba(0,0,0,0) !important;
  position:relative;
  animation-name: speak-now;
  animation-duration: {duration}ms;
  animation-fill-mode:forwards;
  filter: brightness(100%);
  animation-iteration-count:{loop};
  {sub_image_url}
}}
 
@keyframes speak-now {{
  0% {{ bottom:0px; }}
  50% {{ bottom:{pixel}px; }}
  100% {{ bottom:0px; }}
}}
li.voice-state{{ position: static; text-align: center;}}
div.user{{ display: none; }}
body {{ background-color: rgba(0, 0, 0, 0); overflow: hidden; }}
			'''
	message_str = "```"
	message_str = message_str + css
	message_str = message_str + "```"
	await interaction.response.send_message(message_str, ephemeral=False)
	list_lastcss[interaction.guild.id] = {
		"user": user,
		"main_image": main_image,
		"sub_image": sub_image
	}

@client.event
async def on_ready():
	await tree.sync()

async def startup():
	await client.login('TOKEN')
	await client.connect()
	client.clear()

async def logout():
	print("Shutdown.")

def set_config(name, array):
	try:
		config.set('DEFAULT', name, json.dumps(array))
		config.write(open(DEFAULT_CONFIG_FILE, 'w'))
	except:
		traceback.print_exc()
	return

async def config_cmd(arg_long, value, list, list_name, inter):
	list[str(inter.guild.id)] = value
	set_config(list_name, list)
	await inter.response.send_message(f"このサーバーの\"{arg_long}\"の設定を{value}にしました。", ephemeral=True)

def get_value_from_config(key, arr, def_value):
	if(key in arr):
		return arr[key]
	else:
		return def_value
loop = asyncio.get_event_loop()

try:
	loop.run_until_complete(startup())
except KeyboardInterrupt:
	loop.run_until_complete(logout())
finally:
	loop.close()
