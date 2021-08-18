# 支語警察

detects chinese terms on discord
based off discord.py

## Basic

- python 3.8+

## How to

1. create `config.json` and set up the bot token

```javascript
{
    "prefix" : "~",
    "token" : "自己創ㄛ"
}
```

2. create `cogs/reaction_setting.json` and set up the emoji, reaction pictures and reaction channel

```javascript
{
    "reaction_image": [
    ],
    "guild": "",
    "self_dictionary": ""
}
```

3. create `cogs/server_mapping.json`, `cogs/mapping.json`, `cogs/taiwanword.txt`, `cogs/chinaword.txt`

```sh
echo '{}' > ./cogs/server_mapping.json
echo '{}' > ./cogs/mapping.json
echo '' > ./cogs/taiwanword.txt
echo '' > ./cogs/chinaword.txt
```

4. install python package

```sh
$ pip install -r requirements.txt
```

5. start the program

```sh
$ python index.py
```

## Contribute


