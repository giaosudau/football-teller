import scrapy

from football_spider.items import ClubItem, PlayerItem, LeagueItem, MatchItem


def remove_whitespace(string):
    return string.replace(" ", "").replace("\t", "").replace("\n", "") if string else ''


class TransfermarkSpider(scrapy.Spider):
    name = "transfermark"
    start_urls = ['https://www.transfermarkt.co.uk/wettbewerbe/europa']

    def __init__(self, season='2022', **kwargs):
        super().__init__(**kwargs)
        self.season = season

    def start_requests(self):
        for url in self.start_urls:
            # yield scrapy.Request(url=f'{url}/plus/?saison_id={self.season}', callback=self.parse_league)
            yield scrapy.Request(url, callback=self.parse_region)

    def parse_region(self, response, **kwargs):
        last_page_class = 'tm-pagination__list-item--icon-last-page'
        page_item_class = 'tm-pagination__list-item'
        num_pages = response.xpath(f'//*[@class="{page_item_class} {last_page_class}"]//@href').get().split("=")[-1]
        self.logger.info(f"-----------Num Pages {num_pages}")
        for i in range(1, int(num_pages) + 1):
            url = f'{self.start_urls[0]}?page={i}'
            yield scrapy.Request(url, callback=self.parse_region_by_page)

    def parse_region_by_page(self, response, **kwargs):
        num_leagues = len(response.xpath('//*[@id="yw1"]/table/tbody/tr/td[1]//tr/td[2]//a/@href').extract())
        self.logger.info(f"-------------Numer of league {num_leagues} -------------")
        for i in range(1, num_leagues + 2):
            league_url = response.xpath(f'//*[@id="yw1"]/table/tbody/tr[{i}]/td[1]//tr/td[1]//@href').get()
            if not league_url:
                self.logger.debug("Skip the Section")
                continue
            league_id = league_url.split("/")[-1]
            league = LeagueItem(
                url=league_url
                , id=league_id
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
            self.logger.debug(club_league)
            yield club_league
            club_url = response.xpath(f'.//tr[{i}]/td[2]/a/@href').get()
            url = str(response.urljoin(club_url))
            yield scrapy.Request(url, callback=self.parse_club)

            league_match_url = f'https://www.transfermarkt.co.uk/{slug_name}/gesamtspielplan/wettbewerb/{league_id}/saison_id/{self.season}'
            self.logger.debug(f"league_match_url {league_match_url}")
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
                    , match_id=url.split('/')[-1]
                    , url=url
                )
                self.logger.debug(match_item)
                yield match_item

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
            self.logger.debug(player)
            yield player
            url = str(response.urljoin(player_url))
            self.logger.debug(url)
            # yield scrapy.Request(url, callback=self.parse_player)

    def parse_player(self, response, **kwargs):
        pass
