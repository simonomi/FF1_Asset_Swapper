# ╭─────────────────────────────────────────────────────────────────────────╮
# │ FF1 Asset Swapper                                                       │
# │  by Simonomi                                                            │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ Hey! this is a tool I made to swap asset files in FF1.                  │
# │ In theory, it *should* be fully-featured for any nds ROM,               │
# │ but in practice it probably wouldn't be useful. Allow me                │
# │ to explain the way models are stored, which will hopefully              │
# │ help make this script make any sense:                                   │
# │                                                                         │
# │ Almost all files in the Fossil Fighters ROM are formatted in            │
# │ a proprietary format, then compressed into a proprietary format.        │
# │ Because this tool only swaps asset files, it doesn't bother             │
# │ encoding/decoding them, but it does require any two swapped files       │
# │ to be the same size.                                                    │
# │                                                                         │
# │ Luckily for us, the way 3D models are stored in FF1 is super            │
# │ convenient for this! Because 3D models often share a lot of             │
# │ data (for example, Hunter, with the same model in 8 different colors),  │
# │ the actual model data itself is stored in one large table, and each     │
# │ so-called 'asset file' just has a list of indexes into that table.      │
# │ For example, the entire asset file for T-Rex Hunter is as follows:      │
# │ (decompressed and formatted)                                            │
# │                                                                         │
# │   > MM3 25 28 26 32 27  36 6517345 6517345 6517345                      │
# │                                                                         │
# │ Now compare that to the asset file for Maiasaura Hunter:                │
# │                                                                         │
# │   > MM3 25 28 26 32 149 36 6517345 6517345 6517345                      │
# │                                                                         │
# │ The upshot of all this is that because each asset file                  │
# │ is the same size, we can swap them willy-nilly all we want!             │
# │ ...So long as they're in the same directory. Asset files                │
# │ only point to the table in the directory they're in,                    │
# │ and while it's most likely possible to modify the table itself,         │
# │ this isn't the tool for that job.                                       │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ Terms                                                                   │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ These are the terms I use to describe the character model naming        │
# │ convention. There are many exceptions. Thanks FF1 devs /s.              │
# │                                                                         │
# │ [Modeltype][CharacterNumber][Variation][SpecialTrait]_[AnimationNumber] │
# │                                                                         │
# │ Examples: cha01a_01, cha01b_01, cha02_01, cha02_02, cha02_ice_01,       │
# │           head01a, head01b, head02, head03a, head03b                    │
# │                                                                         │
# │ Model type                                                              │
# │     "cha" indicates a character's body,                                 │
# │     "head" is... well, obvious.                                         │
# │                                                                         │
# │ Character number                                                        │
# │     A number that indicates which character a model is.                 │
# │     This isn't literally a 'character' from the story,                  │
# │     for example, Duna/Human Duna, Rosie/Triconodonta Rosie,             │
# │     and Bullwort/B.B. Bullwort all have different character numbers.    │
# │     In addition, sometimes characters share the same character number,  │
# │     like Peggy/Tipper, Ty Tull/Shopkeeper, etc.                         │
# │                                                                         │
# │ Variation                                                               │
# │     An annoyingly inconsistently-used letter that indicates             │
# │     what 'variation' of a character is used. For example,               │
# │     Hunter's colors, Peggy/Tipper's clones, etc.                        │
# │                                                                         │
# │ Special trait                                                           │
# │     This is used only for Hunter, Rosie, Duna, Dr. Diggins,             │
# │     and Mr. Richmond to indicate some kind of special state:            │
# │     frozen (ice), fossilized (rock), or paralyzed (paralysis).          │
# │                                                                         │
# │     Note: The files `cha0102_rock_01` and `cha0108_rock_01` do *not*    │
# │           refer to characters 102 and 108 (which don't exist), but      │
# │           instead refer to characters 1-and-2 and 1-and-8. These are    │
# │           used for the stone sleep return from Guhnash.                 │
# │                                                                         │
# │ Animation number                                                        │
# │     This indicates which animation a model is in. For some reason,      │
# │     each separate animation is stored as a separate model. As a result, │
# │     it may be impossible to completely replace one character with       │
# │     another, as some animations will likely be missing.                 │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ Usage                                                                   │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ python ff1_asset_swapper.py [DEBUG] [CUSTOM_MODE] [WEIRD_SPRINT]        │
# │      input_nds_file output_name character_number[variation]             │
# │                                                                         │
# │ Note: At any point, all remaining arguments may be omitted, and will be │
# │       prompted for at runtime, but options that are provided MUST be    │
# │       given in the order shown above.                                   │
# │                                                                         │
# │ DEBUG                                                                   │
# │     Setting this to "debug" enables debug logging to the console.       │
# │                                                                         │
# │ CUSTOM_MODE                                                             │
# │     When this is set to "custom", 'custom mode' is activated.           │
# │     In custom mode, the default behavior is skipped, and all            │
# │     arguments after `WEIRD_SPRINT` are ignored. This allows custom      │
# │     commands to be added to the bottom of the script that will only     │
# │     be run in custom mode. For information on how to write custom       │
# │     commands, see `Commands` at the bottom of the script.               │
# │                                                                         │
# │ WEIRD_SPRINT                                                            │
# │     WEIRD_SPRINT is a feature that allows for moving characters         │
# │     without sprint animations. When moving character assets, if the     │
# │     source character doesn't have a sprint animation, but the           │
# │     destination one does, the source's walking animation will be used   │
# │     as a replacement. This looks pretty weird, hence the name, but      │
# │     it's better than reverting back to the original character every     │
# │     time you sprint.                                                    │
# │                                                                         │
# │     Setting this to "--disable-weird-sprint" or "-d" disables this      │
# │     functionality.                                                      │
# │                                                                         │
# │ input_nds_file                                                          │
# │     The input ROM that data is read to. This is expected to be          │
# │     unmodified, but should still work otherwise.                        │
# │                                                                         │
# │ output_name                                                             │
# │     Used to create the output ROM. Formatted as follows:                │
# │     '[input file name] - [output_name].nds'                             │
# │                                                                         │
# │ character_number                                                        │
# │     If CUSTOM_MODE is not enabled, Hunter's model (all variations) will │
# │     be replaced with this character's model and this character's model  │
# │     will be replaced by Deinonychus Hunter (This can easily             │
# │     be changed, see `Commands` at the bottom of the script).            │
# │                                                                         │
# │ variation                                                               │
# │     This optionally specifies which variation of the character's model  │
# │     will be used.                                                       │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ Examples                                                                │
# ├─────────────────────────────────────────────────────────────────────────┤
# │ Easiest use case, prompts for all arguments at runtime:                 │
# │                                                                         │
# │   > python ff1_asset_swapper.py                                         │
# │                                                                         │
# │ Second easiest use case, same as above but with weird sprint disabled:  │
# │                                                                         │
# │   > python ff1_asset_swapper.py --disable-weird-sprint                  │
# │                                                                         │
# │ Prompts for most arguments at runtime, but not input_nds_file:          │
# │                                                                         │
# │   > python ff1_asset_swapper.py "Fossil Fighters.nds"                   │
# │                                                                         │
# │ Skips prompts for input_nds_file or output_name:                        │
# │                                                                         │
# │   > python ff1_asset_swapper.py custom "Fossil Fighters.nds" "my mod"   │
# │                                                                         │
# │ Same as above but with weird sprint disabled:                           │
# │                                                                         │
# │   > python ff1_asset_swapper.py -d "Fossil Fighters.nds" "my mod"       │
# │                                                                         │
# │ Swaps Hunter and Rosie:                                                 │
# │                                                                         │
# │   > python ff1_asset_swapper.py "Fossil Fighters.nds" "Rosie mod" 2     │
# │                                                                         │
# │ Swaps Hunter and Triconodonta Rosie:                                    │
# │                                                                         │
# │   > python ff1_asset_swapper.py "Fossil Fighters.nds"                   │
# │                                             "Triconodonta Rosie mod" 11 │
# │                                                                         │
# │ Swaps Hunter and Triconodonta Rosie with a hat:                         │
# │                                                                         │
# │   > python ff1_asset_swapper.py "Fossil Fighters.nds"                   │
# │                                   "Triconodonta Rosie with hat mod" 11b │
# ╰─────────────────────────────────────────────────────────────────────────╯

from shutil import copyfile
from os import system
from os.path import isfile
from re import compile
from sys import argv
from glob import glob

character_regex = compile("(?P<model_type>cha|head)(?P<character_number>\\d+)(?P<variation>[a-h]?)_?(?P<special_trait>ice|rock|paralysis)?_?(?P<animation_number>\\d+)?")

def error(message):
	print(f"\033[31m{message}\033[0m")
	exit()

def inte(_bytes):
	return int.from_bytes(_bytes, "little")

class File:
	def __init__(self, name, id):
		self.name = name
		self.id = id
	
	def generate_offsets(self, file, allocation_table_offset):
		offset = self.id * 8
		file.seek(allocation_table_offset + offset)
		
		self.start_address = inte(file.read(4))
		end_address = inte(file.read(4))
		self.length = end_address - self.start_address
	
	def get_character_info(self, key):
		match = character_regex.match(self.name)
		
		dictionary = {}
		if match:
			dictionary = match.groupdict()
		
		value = dictionary.get(key)
		if value != None and key in ["character_number", "animation_number"]:
			return int(value)
		return value
	
	def get_path(self, path):
		return self
	
	def __repr__(self):
		return self.name

class Directory(File):
	def __init__(self, name, id, offset, first_child_id):
		File.__init__(self, name, id)
		self.offset = offset
		self.first_child_id = first_child_id
		self.children = []
	
	@classmethod
	def from_file(cls, file, id):
		offset = inte(file.read(4))
		first_child_id = inte(file.read(2))
		parent_id = inte(file.read(2))
		return Directory("", id, offset, first_child_id)
	
	def replace_file_children_with_directories(self, directories):
		for index, child in enumerate(self.children):
			matching_directory = [x for x in directories if x.id == child.id]
			if matching_directory != []:
				directories.remove(matching_directory[0])
				matching_directory[0].name = child.name
				self.children[index] = matching_directory[0]
				self.children[index].replace_file_children_with_directories(directories)
	
	def generate_offsets(self, file, allocation_table_offset):
		for child in self.children:
			File.generate_offsets(self, file, allocation_table_offset)
			child.generate_offsets(file, allocation_table_offset)
	
	def get_path(self, path):
		next_child_name = path.split("/")[0]
		rest_of_path = "/".join(path.split("/")[1:])
		
		if next_child_name == "":
			return self
		
		try:
			next_child = [x for x in self.children if x.name == next_child_name][0]
		except:
			error(f"Path not found. Failed at {next_child_name}")
		
		return next_child.get_path(rest_of_path)
	
	def __repr__(self):
		if self.name == "":
			return "/"
		else:
			return self.name + "/"

def create_file_structure(nds_file):
	with open(nds_file, "rb") as file:
		file.seek(0x40)
		
		name_table_offset = inte(file.read(4))
		name_table_length = inte(file.read(4))
		allocation_table_offset = inte(file.read(4))
		allocation_table_length = inte(file.read(4))
		
		file.seek(name_table_offset)
		
		offset = inte(file.read(4))
		first_child_id = inte(file.read(2))
		number_of_directories = inte(file.read(2))
		
		directories = [Directory("", 0xF000, offset, first_child_id)]
		
		for i in range(number_of_directories - 1):
			id = 0xf000 + i + 1
			directories.append(Directory.from_file(file, id))
		
		for directory in directories:
			file.seek(name_table_offset + directory.offset)
			
			while True:
				file_name_length = inte(file.read(1))
				if file_name_length == 0: break
				
				is_directory = file_name_length > 0x80
				if is_directory:
					file_name_length -= 0x80
				
				file_name = file.read(file_name_length).decode()
				
				if is_directory:
					id = inte(file.read(2))
				else:
					id = directory.first_child_id
					directory.first_child_id += 1
				
				directory.children.append(File(file_name, id))
		
		root = directories.pop(0)
		root.replace_file_children_with_directories(directories)
		root.generate_offsets(file, allocation_table_offset)
		
		return root

def move_path(path1, path2):
	return move(root.get_path(path1), root.get_path(path2))

def move(source, destination):
	if source.length != destination.length:
		error(f"{source} and {destination}'s sizes differ ({source.length} != {destination.length})")
	
	system(f'dd bs=1 conv=notrunc if="{input_nds_file}" of="{output_nds_file}" iseek={source.start_address} oseek={destination.start_address} count={source.length}')

def swap_path(path1, path2):
	return swap(root.get_path(path1), root.get_path(path2))

def swap(source, destination):
	move(source, destination),
	move(destination, source)

def get_character(root, character_number, variation):
	character_model_files = root.get_path("model/fieldchar").children
	if variation:
		return [x for x in character_model_files if x.get_character_info("character_number") == character_number and x.get_character_info("variation") in [variation, ""]]
	else:
		return [x for x in character_model_files if x.get_character_info("character_number") == character_number]

def swap_characters(source_models, destination_models):
	move_character(source_models, destination_models) 
	move_character(destination_models, source_models)

def move_character(source_models, destination_models):
	for source_model in source_models:
		special_trait = source_model.get_character_info("special_trait")
		animation_number = source_model.get_character_info("animation_number")
		
		matching_destinations = [x for x in destination_models if x.get_character_info("special_trait") == special_trait and x.get_character_info("animation_number") == animation_number]
		
		for destination in matching_destinations:
			if DEBUG:
				print(source_model, destination)
			move(source_model, destination)
	
	if not [x for x in source_models if x.get_character_info("animation_number") == 3] and ADD_WEIRD_SPRINT:
		walking_model = [x for x in source_models if x.get_character_info("animation_number") == 2]
		if walking_model:
			walking_model = walking_model[0]
		else:
			error("Cannot add weird sprint, no walking animation found. Please disable ADD_WEIRD_SPRINT by adding the flag --disable-weird-sprint")
				
		running_destinations = [x for x in destination_models if x.get_character_info("animation_number") == 3]
		
		for destination in running_destinations:
			if DEBUG:
				print("ADD_WEIRD_SPRINT: ", end="")
				print(walking_model, destination)
			move(walking_model, destination)

# MARK: DEBUG
DEBUG = len(argv) > 1 and argv[1].lower() == "debug"
if DEBUG:
	argv.pop(1)
	print("debug mode enabled")

# MARK: CUSTOM_MODE
CUSTOM_MODE = len(argv) > 1 and argv[1].lower() == "custom"
if CUSTOM_MODE:
	argv.pop(1)
	print("custom mode enabled")

# MARK: ADD_WEIRD_SPRINT
ADD_WEIRD_SPRINT = len(argv) > 1 and argv[1].lower() not in ["-d", "--disable-weird-sprint"]
if not ADD_WEIRD_SPRINT:
	argv.pop(1)
	print("Disabling ADD_WEIRD_SPRINT")

# MARK: input_nds_file
if len(argv) > 1:
	input_nds_file = argv.pop(1)
	
	if not isfile(input_nds_file):
		error(f"Input file does not exist: '{input_nds_file}'")
else:
	nds_files = sorted(glob("*.nds"))
	
	if len(nds_files) == 0:
		error("No nds files found in current directory")
	elif len(nds_files) == 1:
		input_nds_file = nds_files[0]
	else:
		print("Found nds files:")
		for index, file_name in enumerate(nds_files):
			print(f"    [{index}] - {file_name}")

		try:
			input_nds_file_index = int(input("Pick an nds file as input: "))
			assert(input_nds_file_index >= 0)
			input_nds_file = nds_files[input_nds_file_index]
		except:
			error("Invalid index")

print(f"Using '{input_nds_file}' as input file", end="\n\n")

# MARK: output_nds_file
if len(argv) > 1:
	output_name = argv.pop(1)
	output_nds_file = f"{input_nds_file[:-4]} - {output_name}.nds"
else:
	output_name = input("Pick a name for the output file (ex: Rosie mod): ")
	output_nds_file = f"{input_nds_file[:-4]} - {output_name}.nds"

	if isfile(output_nds_file):
		overwrite = input(f"File '{output_nds_file}' already exists, do you want to overwrite it [y/N]? ")
		if not overwrite.lower().startswith("y"):
			error("Aborting...")

print(f"Using '{output_nds_file}' as output file", end="\n\n")

if not CUSTOM_MODE:
	if len(argv) > 1:
		character_number = argv.pop(1)
	else:
		character_number = input("Which character would you like to swap with Hunter? ")
	
	character_variation = "a"
	if not character_number.isdigit() and len(character_number) > 0:
		character_variation = character_number[-1]
		character_number = character_number[:-1]
	
	try:
		character_number = int(character_number)
	except:
		error(f"Invalid character id: {character_number}{character_variation}, expected an integer")
	
	if character_number < 0 or character_number > 47:
		error(f"Invalid character id: {character_number}, must be within range [0, 47]")
	
	print(f"Swapping Hunter with character {character_number}{character_variation}")

root = create_file_structure(input_nds_file)
copyfile(input_nds_file, output_nds_file)

# ╭──────────────────────────────────────────────────────────────────────────╮
# │ Commands                                                                 │
# ├──────────────────────────────────────────────────────────────────────────┤
# │ root                                                                     │
# │     An object representing the root directory of the ROM.                │
# │     This is created above with `create_file_structure`.                  │
# │                                                                          │
# │ root.get_path(path)                                                      │
# │     Given a file path, returns the file object at that path.             │
# │     Panics if an invalid path is provided.                               │
# │                                                                          │
# │ move(source, destination)                                                │
# │     Given two file objects, copy the data in the first (by reading from  │
# │     input_nds_file) to the second (by writing to output_nds_file).       │
# │                                                                          │
# │     Because the input and output files are different, performing         │
# │     > move(file1, file2)                                                 │
# │     > move(file2, file1)                                                 │
# │     results in file1 and file2 swapping data.                            │
# │                                                                          │
# │ move_path(source_path, destination_path)                                 │
# │     Convenience wrapper around `move` that calls `root.get_path` for     │
# │     each input path.                                                     │
# │                                                                          │
# │ swap(file1, file2)                                                       │
# │     Swaps file1 and file2. Because the input and output files are        │
# │     different, this is implemented with two `move`s.                     │
# │                                                                          │
# │ swap_path(path1, path2)                                                  │
# │     Convenience wrapper around `swap` that calls `root.get_path` for     │
# │     each input path.                                                     │
# │                                                                          │
# │ get_character(root, character_number, variant)                           │
# │     Get the character with a given character number and variant.         │
# │                                                                          │
# │     If variant is an empty string, all variations for that character are │
# │     returned. If this is used for the source of a move, each variation   │
# │     will be applied in order, resulting in the only last variation being │
# │     applied. That is, unless an earlier variation has an animation that  │
# │     a later variation doesn't, in which case all chaos ensues.           │
# │                                                                          │
# │     Technically, this returns an array of files, but you shouldn't       │
# │     need to worry about that.                                            │
# │                                                                          │
# │ move_character(source_character, destination_character)                  │
# │     Moves the model data of source_character to destination_character.   │
# │                                                                          │
# │ swap_characters(character1, character2)                                  │
# │     Swaps character1 and character2. Same as `swap` but with characters. │
# ╰──────────────────────────────────────────────────────────────────────────╯

if not CUSTOM_MODE:
	all_hunters = get_character(root, 1, "")
	hunter_deinonychus = get_character(root, 1, "c")
	input_character = get_character(root, character_number, character_variation)
	move_character(input_character, all_hunters)
	move_character(hunter_deinonychus, input_character)
	exit()

# Any code that you add here will only be run in custom mode

# MARK: Examples

# replace t-rex hunter head with rosie head
# hunter_head = root.get_path("model/fieldchar/head01a")
# rosie_head = root.get_path("model/fieldchar/head02")
# move(hunter_head, rosie_head)

# replace t-rex hunter head with rosie head
# move_path("model/fieldchar/head01a", "model/fieldchar/head02")

# swap t-rex hunter head and rosie head
# swap_path("model/fieldchar/head01a", "model/fieldchar/head02")

# replace t-rex hunter with rosie
# move_path("model/fieldchar/cha01a_01", "model/fieldchar/cha02_01")
# move_path("model/fieldchar/cha01a_02", "model/fieldchar/cha02_02")
# move_path("model/fieldchar/cha01a_03", "model/fieldchar/cha02_03")
# move_path("model/fieldchar/cha01a_04", "model/fieldchar/cha02_04")
# move_path("model/fieldchar/cha01a_06", "model/fieldchar/cha02_06")
# move_path("model/fieldchar/cha01a_08", "model/fieldchar/cha02_08")
# move_path("model/fieldchar/cha01a_10", "model/fieldchar/cha02_10")
# move_path("model/fieldchar/cha01a_11", "model/fieldchar/cha02_11")
# move_path("model/fieldchar/cha01a_12", "model/fieldchar/cha02_12")
# move_path("model/fieldchar/cha01a_13", "model/fieldchar/cha02_13")
# move_path("model/fieldchar/cha01a_15", "model/fieldchar/cha02_15")
# move_path("model/fieldchar/cha01a_79", "model/fieldchar/cha02_79")
# move_path("model/fieldchar/cha01a_80", "model/fieldchar/cha02_80")
# move_path("model/fieldchar/cha01a_81", "model/fieldchar/cha02_81")
# move_path("model/fieldchar/cha01a_82", "model/fieldchar/cha02_82")
# move_path("model/fieldchar/cha01_ice_01", "model/fieldchar/cha02_ice_01")
# move_path("model/fieldchar/head01a", "model/fieldchar/head02")

# replace t-rex hunter with rosie
# hunter = get_character(root, 1, "")
# rosie = get_character(root, 2, "a")
# move_character(hunter, rosie)

# swap t-rex hunter and rosie
# hunter = get_character(root, 1, "")
# rosie = get_character(root, 2, "a")
# swap_characters(hunter, rosie)
