import os
import requests
import coloredlogs
import logging

import board_parser

coloredlogs.install()

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', 'https://discord.com/api/webhooks/...')


class AD(object):
    def __init__(self, ip, driver, scoreboard, teamname):
        global info, delta, soup
        delta = []
        self.ip = ip
        self.teamname = teamname
        self.scoreboard = scoreboard

        if not driver:
            soup = board_parser.get_soup_by_address(self.scoreboard)
        else:
            soup = None
        
        # Get challenge here
        # Valid across all system
        self.patch = board_parser.init_patch(driver, soup)
        print("Challenges: " + str(self.patch))

        # Get current round
        # Valid across all system
        self.round = board_parser.get_current_round(driver, soup)
        print(f"Current round: {self.round}")

        # Need classification
        info = board_parser.get_teams_info(driver, soup, self.scoreboard)
        print(f"info: {info}")

    def get_info_by_ip(self, ip):
        for team in info:
            if team['ip'] == ip:
                return team
        logging.critical("No team with IP {ip}".format(ip=ip))

    def get_info_by_name(self, name):
        for team in info:
            if team['name'] == name:
                return team
        logging.critical("No team with name {}".format(name))

    def dump(self):
        return info

    def get_delta_by_ip(self, ip):
        for team in delta:
            if team['ip'] == ip:
                return team
        logging.critical("No team with IP {ip}".format(ip=ip))

    def get_delta_by_name(self, name):
        for team in delta:
            if team['name'] == name:
                return team
        logging.critical("No team with name {name}".format(name=name))

    def refresh(self, driver):
        global info
        if driver:
            driver.get(self.scoreboard)
            current_round = board_parser.get_current_round(driver, None)
            if self.round != current_round:
                new_info = board_parser.get_teams_info(driver, None)
                self.round = current_round
                self.__recalculate_delta(new_info)
                info = new_info
                return True
            else:
                return False
        else:
            new_soup = board_parser.get_soup_by_address(self.scoreboard)
            new_info = board_parser.get_teams_info(driver, new_soup)
            current_round = board_parser.get_current_round(driver, new_soup)
            if self.round != current_round:
                self.round = current_round
                self.__recalculate_delta(new_info)
                info = new_info.copy()
                return True
            else:
                return False

    def __recalculate_delta(self, new_info):
        global delta
        delta = []
        for team_new in new_info:
            if self.ip:
                team_old = self.get_info_by_ip(team_new['ip'])
            else:
                team_old = self.get_info_by_name(team_new['name'])
            delta_services = {}
            for service_new, service_old in zip(team_new['services'], team_old['services']):
                name = service_new['name']
                team_got_new_flags = service_new['flags']['got'] - \
                    service_old['flags']['got']
                team_lost_new_flags = service_new['flags']['lost'] - \
                    service_old['flags']['lost']
                delta_services[name] = {
                    'status': service_new['status'],
                    'title':  service_new['title'],
                    'flags': {
                        'got': team_got_new_flags,
                        'lost': team_lost_new_flags
                    }}

            if team_new['ip'] == self.ip or team_new['name'] == self.teamname:
                # * Notification about team placement
                if team_old['place'] > team_new['place']:
                    discord_alert(
                        'PLACE', status='up', place_old=team_old['place'], place_new=team_new['place'])
                elif team_old['place'] < team_new['place']:
                    discord_alert(
                        'PLACE', status='down', place_old=team_old['place'], place_new=team_new['place'])

                # * Notification about service status
                for service_new, service_old in zip(team_new['services'], team_old['services']):
                    name = service_new['name']
                    title = service_new['title']

                    new_status = service_new['status']
                    old_status = service_old['status']

                    if soup:
                        new_status = board_parser.return_status(new_status)
                        old_status = board_parser.return_status(old_status)

                    # * If the service hasn't recovered or status hasn't changed
                    if new_status == old_status and new_status != 'UP':
                        discord_alert(
                            'STATUS',
                            status='not change',
                            now=new_status,
                            service=name,
                            title=title
                        )

                    # * If the service has recovered or changed status to UP
                    if old_status != 'UP' and new_status == 'UP':
                        discord_alert(
                            'STATUS',
                            status='up',
                            now=new_status,
                            service=name
                        )

                    # * If the service hasn't recovered or changed status not to UP
                    if old_status != new_status and new_status != 'UP':
                        discord_alert(
                            'STATUS',
                            status='down',
                            now=new_status,
                            service=name,
                            title=title
                        )

                    # * First blood notification
                    if int(delta_services[name]['flags']['lost']) != 0 and self.patch[name] == True:
                        self.patch[name] = False
                        discord_alert('FB', service=name)

                    # * Notification about stopping flag loss
                    elif int(delta_services[name]['flags']['lost']) == 0 and self.patch[name] == False and new_status == 'UP':
                        self.patch[name] = True
                        discord_alert('PATCH', service=name)

            delta.append({
                'round': self.round,
                'name': team_new['name'],
                'ip': team_new['ip'],
                'place': team_new['place'],
                'score': round(team_new['score'] - team_old['score'], 2),
                'services': delta_services
            })

def discord_alert(alert_type, **args):
    if alert_type == 'PLACE':
        requests.post(DISCORD_WEBHOOK, json={
            "content": "{} from *{}* to *{}* place".format('⬇ Our team dropped' if args['status'] == 'down' else '⬆ Our team climbed', args['place_old'], args['place_new'])
        })
    if alert_type == 'STATUS':
        if args['now'] == 'UP':
            simb = '🟢 {} 🟢\n'
        elif args['now'] == 'DOWN':
            simb = '🔴 {} 🔴\n'
        elif args['now'] == 'CORRUPT':
            simb = '🔵 {} 🔵\n'
        elif args['now'] == 'MUMBLE':
            simb = '🟠 {} 🟠\n'
        elif args['now'] == 'CHECK FAILED':
            simb = '🟡 {} 🟡\n'

        if args['status'] == 'down':
            otvet = "Service is down"
            if args['title']:
                otvet += "\n{}".format(args['title'])
        elif args['status'] == 'up':
            otvet = "Service is alive again"
        elif args['status'] == 'not change':
            otvet = "Service is STILL down"
            if args['title']:
                otvet += "\n **Check Error:** {}".format(args['title'])

        requests.post(DISCORD_WEBHOOK, json={
            "content": "{} {}".format(simb.format(args['service']), otvet)
        })
    if alert_type == 'FB':
        requests.post(DISCORD_WEBHOOK, json={
            "content": "🩸 We are losing flags on the service *{}*".format(args['service'])
        })
    if alert_type == 'PATCH':
        requests.post(DISCORD_WEBHOOK, json={
            "content": "💎 Our filter on the service *{}* is working.".format(args['service'])
        })
