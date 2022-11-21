import asyncio
import base64
import getpass
import time

import gd
from gd.api import Editor

blank = Editor()
client = gd.Client()
async def test():
	try:
		f = open("credentials.txt", "r")
	except:
		username = input("Username: ")
		password = getpass.getpass()
		await client.login(username, password)
		f = open("credentials.txt", "w")
		f.write(base64.b64encode((username + "\n" + password).encode("ascii")).decode("ascii"))
	else:
		print("Logging in...")
		try:
			username, password = base64.b64decode(f.read()).decode('ascii').splitlines()
			await client.login(username, password)
		except:
			while True:
				print("Failed to log in, retrying in 10s")
				time.sleep(10)
				continue


	target_level = int(input("Level ID: "))
	starttime = time.time()	
	reference = await client.get_level(85916710)
	if target_level < 128:
		level = gd.Level.official(target_level)
		default = True
	else:
		level = await client.get_level(target_level)
		default = False
	editor = reference.open_editor()
	reference2 = level.open_editor()
	print(f"Selected level: {level.name}, {level.objects} objects")

	editor = Editor()
	header = gd.api.Header()
	header2 = level.open_editor().header
	header.gamemode, header.speed, header.audio_track, header.song_offset, header.song_fade_in, header.song_fade_out, header.minimode, header.flip_gravity, header.dual_mode, header.two_player_mode = header2.gamemode, header2.speed, header2.audio_track, header2.song_offset, header2.song_fade_in, header2.song_fade_out, header2.minimode, header2.flip_gravity, header2.dual_mode, header2.two_player_mode
	editor.header = header
	
	nextgrp = reference2.get_free_group()
	reqobjs = []
	reqgrps = []
	miscobjs = []
	print("Queueing hitbox objects and center groups...")
	for layobj in reference.open_editor().get_objects():
		for allobj in reference2.get_objects():
			if allobj.id == layobj.id:
				allobj.color_1_hsv_enabled = False
				allobj.color_2_hsv_enabled = False
				allobj.color_1 = 1
				allobj.color_2 = 1
				reqobjs.append(allobj)
			if allobj.follow_target_pos_center_id != None:
				reqgrps.append(allobj.follow_target_pos_center_id)
	reqgrps = set(reqgrps)
	print("Center groups: " + str(reqgrps))
	print("Finding center objects...")
	for grp in reqgrps:
		for allobj in reference2.get_objects():
			if allobj.groups != None:
				if grp in allobj.groups:
					miscobjs.append(allobj)
	print("Queuing center objects...")
	for obj in miscobjs:
		if obj not in reqobjs:
			obj.add_groups(nextgrp)
		reqobjs.append(obj)
	reqobjs = set(reqobjs)
	print("Adding all objects...")
	for obj in reqobjs:
		editor.add_objects(obj)
	print("Adding alpha trigger for center objects...")
	editor.add_objects(gd.api.Object(x=-10, y=50, id=1007, target_group_id=nextgrp, duration=0, opacity=0))

	new_name = level.name
	if len(level.name) <= 16:
		new_name = level.name + " LDM"
	if default == True:
		song = gd.Song.official(level.id - 1)
	else:
		song = level.song
	final = gd.Level(data = editor.dump(), name = new_name, client=client, song=song, copyable=True, description=f'Layout of {level.name} by {level.creator}, {len(editor.objects)} objects', coins=level.coins, original = level.id)
	print(f"Generation time: {round(time.time() - starttime)} seconds")
	while True:
		try:
			print("Uploading level...")
			await final.upload()
		except:
			print("Failed to upload a level. Retrying in 20s")
			time.sleep(20)
			continue
		else:
			print(f"Level uploaded: {final.name}, {final.objects} objects")
			break
	
asyncio.run(test())