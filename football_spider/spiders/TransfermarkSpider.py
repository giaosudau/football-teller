import re

import scrapy

from football_spider.items import ClubItem, PlayerItem, LeagueItem, MatchItem, GoalItem

STYLE_REGEX = re.compile(r'background-position:\s*(-?\d+)px\s*(-?\d+)px')


def remove_whitespace(string):
    return string.replace(" ", "").replace("\t", "").replace("\n", "") if string else ''


def get_image_number(style):
    match = STYLE_REGEX.search(style)
    if match:
        x = int(match.group(1))
        y = int(match.group(2))

        # Get row and col number
        col = -x // 36
        row = -y // 36

        # Calculate image number
        num = row * 10 + col + 1

        return num

    return None


class TransfermarkSpider(scrapy.Spider):
    name = "transfermark"
    start_urls = ['https://www.transfermarkt.co.uk/wettbewerbe/europa']

    def __init__(self, season='2022', num_pages=None, num_leagues_per_page=None, **kwargs):
        super().__init__(**kwargs)
        self.season = season
        self.num_page = num_pages
        self.num_leagues_per_page = num_leagues_per_page

    def start_requests(self):
        for url in self.start_urls:
            # yield scrapy.Request(url=f'{url}/plus/?saison_id={self.season}', callback=self.parse_league)
            yield scrapy.Request(url, callback=self.parse_region)

    def parse_region(self, response, **kwargs):
        last_page_class = 'tm-pagination__list-item--icon-last-page'
        page_item_class = 'tm-pagination__list-item'
        num_pages = response.xpath(f'//*[@class="{page_item_class} {last_page_class}"]//@href').get().split("=")[-1]
        self.logger.info(f"-----------Num Pages {num_pages}")
        if not self.num_page:
            self.num_page = int(num_pages)
        for i in range(1, int(self.num_page) + 1):
            url = f'{self.start_urls[0]}?page={i}'
            yield scrapy.Request(url, callback=self.parse_region_by_page)

    def parse_region_by_page(self, response, **kwargs):
        num_leagues = len(response.xpath('//*[@id="yw1"]/table/tbody/tr/td[1]//tr/td[2]//a/@href').extract())
        self.logger.info(f"-------------Numer of league {num_leagues} -------------")
        if not self.num_leagues_per_page:
            self.num_leagues_per_page = num_leagues
        for i in range(1, int(self.num_leagues_per_page) + 2):
            league_url = response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[1]//tr/td[1]//@href').get()
            if not league_url:
                self.logger.debug("Skip the Section")
                continue
            league_id = league_url.split("/")[-1]
            league = LeagueItem(
                url=league_url
                , id=league_id
                , season=self.season
                , name=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[1]//tr/td[2]/a/text()').get()
                , country=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[2]/img/@title').get()
                , num_clubs=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[3]/text()').get()
                , num_players=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[4]/text()').get()
                , avg_age=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[5]/text()').get()
                , percentage_foreigner=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[6]//text()').get()
                , total_value=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[8]//text()').get()
            )
            # self.logger.debug(league)
            yield league
            url = str(response.urljoin(league_url)) + f'/plus/?saison_id={self.season}'
            yield scrapy.Request(url, callback=self.parse_league, meta={'league_id': league_id})

    def parse_league(self, response, **kwargs):
        num_clubs = len(response.xpath('//*[@id="yw1"]/table/tbody/tr').extract())
        self.logger.info(f"-------------Parse function num clubs {num_clubs} -------------")
        league_id = response.request.meta['league_id']
        for i in range(1, num_clubs + 1):
            league_url = response.xpath(f'.//tr[{i}]/td[1]/a/@href').get()
            slug_name = league_url.split('/')[1]
            club_league = ClubItem(
                name=response.xpath(f'.//tr[{i}]/td[1]/a/@title').get()
                , slug_name=slug_name
                , season=self.season
                , url=league_url
                , league_id=league_id
                , squads=response.xpath(f'.//tr[{i}]/td[3]/a/text()').get()
                , avg_age=response.xpath(f'.//tr[{i}]/td[4]/text()').get()
                , num_foreigners=response.xpath(f'.//tr[{i}]/td[5]/text()').get()
                , avg_market_value=response.xpath(f'.//tr[{i}]/td[6]/text()').get()
                , total_market_value=response.xpath(f'.//tr[{i}]/td[7]/a/text()').get()
            )
            # self.logger.debug(club_league)
            yield club_league
            club_url = response.xpath(f'.//tr[{i}]/td[2]/a/@href').get()
            url = str(response.urljoin(club_url))
            yield scrapy.Request(f'{url}?saison_id={self.season}', callback=self.parse_club)

            league_match_url = f'https://www.transfermarkt.co.uk/{slug_name}/gesamtspielplan/wettbewerb/{league_id}/saison_id/{self.season}'
            # self.logger.debug(f"league_match_url {league_match_url}")
            yield scrapy.Request(league_match_url, callback=self.parse_league_match, meta={'league_id': league_id})

    def parse_league_match(self, response, **kwargs):
        match_days = response.xpath(
            '//*[@id="main"]/main/div[2]/div//*[@class="content-box-headline"][contains(translate(text(), "Matchday", "matchday"), "matchday")]/text()').extract()
        self.logger.info(f"-------------TOTAL MATCH DAY {len(match_days)}-------------")
        prev_date = None
        prev_time_at = None
        league_id = response.request.meta['league_id']
        for i in range(1, len(match_days) + 1):
            self.logger.debug(f"-------------MATCH DAY {i}-------------")
            num_matches = len(
                response.xpath(f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr//td[5]').extract())
            self.logger.debug(f"NUMER OF MATCHES {num_matches}")
            loop = len(response.xpath('//*[@id="main"]/main/div[2]/div[2]/div/table/tbody/tr').extract())
            for j in range(0, loop + 1):
                result = response.xpath(
                    f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[5]/a/text()').get()
                if not result:
                    continue

                date_parsed = response.xpath(
                    f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[1]/a/text()').get()
                time_parsed = response.xpath(
                    f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[2]/text()').get()
                url = response.xpath(
                    f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[5]/a/@href').get()

                # if date and time was not there get previous one
                date_parsed = remove_whitespace(date_parsed)
                date_parsed = date_parsed or prev_date
                time_parsed = remove_whitespace(time_parsed)
                time_parsed = time_parsed or prev_time_at
                prev_date = date_parsed
                prev_time_at = time_parsed

                home_club_xpath = f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[3]/a'
                away_club_xpath = f'//*[@id="main"]/main/div[2]/div[{i + 1}]/div/table/tbody/tr[{j + 2}]/td[7]/a'

                home_club_url = response.xpath(f'{home_club_xpath}/@href').get()
                home_club_id = home_club_url.split("/")[4]
                away_club_url = response.xpath(f'{away_club_xpath}/@href').get()
                away_club_id = away_club_url.split("/")[4]
                game_id = url.split('/')[-1]
                match_item = MatchItem(
                    date=date_parsed
                    , season=self.season
                    , league_id=league_id
                    , match_day=i
                    , time_at=time_parsed
                    , home_club_name=response.xpath(f'{home_club_xpath}/@title').get()
                    , home_club_id=home_club_id
                    , away_club_name=response.xpath(f'{away_club_xpath}/@title').get()
                    , away_club_id=away_club_id
                    , result=result
                    , match_id=game_id
                    , url=url
                )
                # self.logger.debug(match_item)
                yield match_item
                match_sheet_url = str(response.urljoin(url))
                yield scrapy.Request(match_sheet_url, callback=self.parse_match_sheet, meta={'game_id': game_id})

    def parse_match_sheet(self, response, **kwargs):
        away_club_goal_path = '//*[@id="sb-tore"]/ul/li[@class="sb-aktion-gast"]'
        home_club_id = response.xpath('//*[@id="main"]/main/div[6]/div/div/div[1]//nobr/a/@href').get()
        away_club_id = response.xpath('//*[@id="main"]/main/div[6]/div/div/div[2]//nobr/a/@href').get()
        home_club_goal_path = '//*[@id="sb-tore"]/ul/li[@class="sb-aktion-heim"]'

        def parse_goal(root_path):
            player_ids = response.xpath(f'{root_path}/div/div[3]//@href').extract()
            goal_details = response.xpath(f'{root_path}/div/div[4]/text()[2]').extract()
            goal_scores = response.xpath(f'{root_path}/div/div[2]//text()').extract()
            goal_minutes = response.xpath(f'{root_path}/div/div[1]/span/@style').extract()
            is_home_club = root_path == home_club_goal_path
            club_id = home_club_id if is_home_club else away_club_id
            return [
                {'player_id': pid.split("/")[4]
                    , 'club_id': club_id.split("/")[4]
                    , 'is_home_goal': is_home_club
                    , 'goal_score': score
                    , 'goal_minute': get_image_number(minute)
                    , 'goal_detail': detail}
                for pid, score, minute, detail in
                zip(player_ids, goal_scores, goal_minutes, goal_details)]

        players = parse_goal(home_club_goal_path) + parse_goal(away_club_goal_path)
        count = 1
        for player in players:
            game_id = response.meta['game_id']
            goal = GoalItem(player_id=player['player_id']
                            , goal_id=f'{game_id}{count}'
                            , season=self.season
                            , club_id=player['club_id']
                            , is_home_goal=player['is_home_goal']
                            , game_id=game_id
                            , goal_at_minutes=player['goal_minute']
                            , goal_score=player['goal_score']
                            , goal_detail=player['goal_detail']
                            )
            self.logger.info(goal)
            count += 1
            yield goal

    def parse_club(self, response, **kwargs):
        nums_players = len(response.xpath('//*[@id="yw1"]/table/tbody/tr').extract())
        self.logger.info(f"-------------Parse function num players {nums_players} -------------")
        club_id = response.xpath('//*[@id="overview"]/a/@href').get().split("/")[4]
        for i in range(1, nums_players + 1):
            player_url = response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[2]/table//tr[1]/td[2]/a/@href').get()
            player = PlayerItem(
                id=player_url.split('/')[4]
                , club_id=club_id
                , season=self.season
                , number=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[1]/div/text()').get()
                , url=player_url
                , name=response.xpath(
                    f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[2]/table//tr[1]/td[2]/a/text()').get()
                , position=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[2]//tr[2]/td/text()').get()
                , birth=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[4]/text()').get()
                , nationality=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[5]/img/@alt').extract()
                , market_value=response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[6]/a/text()').get()
            )
            # self.logger.debug(player)
            yield player
            # url = str(response.urljoin(player_url))
            # self.logger.debug(url)
            # yield scrapy.Request(url, callback=self.parse_player)

    def parse_player(self, response, **kwargs):
        pass
