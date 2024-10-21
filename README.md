# Attack/Defense CTF scoreboard parser

AD CTF scoreboard parser - a fork of [Red Cadets's Beard](https://github.com/Red-Cadets/beard)

# ✨ Features

- Parsing of supported scoreboards (hackerdom/forcad)
- Score graph of all teams with automatic scaling for your team
- Primitive prediction of the score graph
- Flag loss graph for each service
- Graph of receiving flags for each service (similar to the effectiveness of exploits)

## 🛠 Supported scoreboards

| **A/D framework**  | Link | Status | Description
| ------------------ | ---- | ------ | -----------
| ForcAD | https://github.com/pomo-mondreganto/ForcAD | ✅ | 
| HackerDom checksystem | https://github.com/HackerDom/checksystem | ✅ | parsing old-style view at /board
| ForcAD ASCIS | N/A | ✅ | Works now

## :whale: Fast Installation Guide

Clone repository
```bash
git clone https://github.com/teebow1e/beard.git
```
Go to folder:
```bash
cd beard
```
Change .env with your settings:
- `SCOREBOARD` - Scoreboard location. Example: `http://6.0.0.1/board`
- `TEAM` - Team name or team IP to display information about. Example: `Red Cadets` or `10.10.1.15`
- `TYPE` - Scoreboard type. Example: `forcad` or `hackerdom` or `ASCIS`
- `ROUND_TIME` - Round time in seconds. For example: `120`
- `EXTEND_ROUND` - The number of rounds to predict future graph. The prediction is based on the points of the last 5 rounds. For example: `10`
- `MONGO_USER` - DB username. Например: `parser`
- `MONGO_PASS` - DB password. Например: `parser`