# FF1 Asset Swapper

Hey! this is a tool I made to swap asset files in FF1.
In theory, it *should* be fully-featured for any nds ROM,
but in practice it probably wouldn't be useful. Allow me
to explain the way models are stored, which will hopefully
help make this script make any sense:

Almost all files in the Fossil Fighters ROM are formatted in
a proprietary format, then compressed into a proprietary format.
Because this tool only swaps asset files, it doesn't bother
encoding/decoding them, but it does require any two swapped files
to be the same size.

Luckily for us, the way 3D models are stored in FF1 is super
convenient for this! Because 3D models often share a lot of
data (for example, Hunter, with the same model in 8 different colors),
the actual model data itself is stored in one large table, and each
so-called 'asset file' just has a list of indexes into that table.
For example, the entire asset file for T-Rex Hunter is as follows:
(decompressed and formatted)

  > MM3 25 28 26 32 27  36 6517345 6517345 6517345

Now compare that to the asset file for Maiasaura Hunter:

  > MM3 25 28 26 32 149 36 6517345 6517345 6517345

The upshot of all this is that because each asset file
is the same size, we can swap them willy-nilly all we want!
...So long as they're in the same directory. Asset files
only point to the table in the directory they're in,
and while it's most likely possible to modify the table itself,
this isn't the tool for that job.

### Terms
These are the terms I use to describe the character model naming
convention. There are many exceptions. Thanks FF1 devs /s.

[Modeltype][CharacterNumber][Variation][SpecialTrait]\_[AnimationNumber]

Examples: cha01a_01, cha01b_01, cha02_01, cha02_02, cha02_ice_01,
          head01a, head01b, head02, head03a, head03b

#### Model type
"cha" indicates a character's body,
"head" is... well, obvious.

#### Character number
A number that indicates which character a model is.
This isn't literally a 'character' from the story,
for example, Duna/Human Duna, Rosie/Triconodonta Rosie,
and Bullwort/B.B. Bullwort all have different character numbers.
In addition, sometimes characters share the same character number,
like Peggy/Tipper, Ty Tull/Shopkeeper, etc.

#### Variation
An annoyingly inconsistently-used letter that indicates
what 'variation' of a character is used. For example,
Hunter's colors, Peggy/Tipper's clones, etc.

#### Special trait
This is used only for Hunter, Rosie, Duna, Dr. Diggins,
and Mr. Richmond to indicate some kind of special state:
frozen (ice), fossilized (rock), or paralyzed (paralysis).

Note: The files `cha0102_rock_01` and `cha0108_rock_01` do *not*
      refer to characters 102 and 108 (which don't exist), but
      instead refer to characters 1-and-2 and 1-and-8. These are
      used for the stone sleep return from Guhnash.

#### Animation number
This indicates which animation a model is in. For some reason,
each separate animation is stored as a separate model. As a result,
it may be impossible to completely replace one character with
another, as some animations will likely be missing.

### Usage

`python ff1_asset_swapper.py [DEBUG] [CUSTOM_MODE] [WEIRD_SPRINT] input_nds_file output_name character_number[variation]`

Note: At any point, all remaining arguments may be omitted, and will be
      prompted for at runtime, but options that are provided MUST be
      given in the order shown above.

#### DEBUG
Setting this to "debug" enables debug logging to the console.

#### CUSTOM_MODE
When this is set to "custom", 'custom mode' is activated.
In custom mode, the default behavior is skipped, and all
arguments after `WEIRD_SPRINT` are ignored. This allows custom
commands to be added to the bottom of the script that will only
be run in custom mode. For information on how to write custom
commands, see `Commands` at the bottom of the script.

#### WEIRD_SPRINT
WEIRD_SPRINT is a feature that allows for moving characters
without sprint animations. When moving character assets, if the
source character doesn't have a sprint animation, but the
destination one does, the source's walking animation will be used
as a replacement. This looks pretty weird, hence the name, but
it's better than reverting back to the original character every
time you sprint.

Setting this to "--disable-weird-sprint" or "-d" disables this
functionality.

#### input_nds_file
The input ROM that data is read to. This is expected to be
unmodified, but should still work otherwise.

#### output_name
Used to create the output ROM. Formatted as follows:
'[input file name] - [output_name].nds'

#### character_number
If CUSTOM_MODE is not enabled, Hunter's model (all variations) will
be replaced with this character's model and this character's model
will be replaced by Deinonychus Hunter (This can easily
be changed, see `Commands` at the bottom of the script).

#### variation
This optionally specifies which variation of the character's model
will be used.

### Examples
Easiest use case, prompts for all arguments at runtime:

`python ff1_asset_swapper.py`

Second easiest use case, same as above but with weird sprint disabled:

`python ff1_asset_swapper.py --disable-weird-sprint`

Prompts for most arguments at runtime, but not input_nds_file:

`python ff1_asset_swapper.py "Fossil Fighters.nds"`

Skips prompts for input_nds_file or output_name:

`python ff1_asset_swapper.py custom "Fossil Fighters.nds" "my mod"`

Same as above but with weird sprint disabled:

`python ff1_asset_swapper.py -d "Fossil Fighters.nds" "my mod"`

Swaps Hunter and Rosie:

`python ff1_asset_swapper.py "Fossil Fighters.nds" "Rosie mod" 2`

Swaps Hunter and Triconodonta Rosie:

`python ff1_asset_swapper.py "Fossil Fighters.nds" "Triconodonta Rosie mod" 11`

Swaps Hunter and Triconodonta Rosie with a hat:

`python ff1_asset_swapper.py "Fossil Fighters.nds" "Triconodonta Rosie with hat mod" 11b`
