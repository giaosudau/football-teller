# Football Teller App

Welcome to the Football Teller app! This application provides information about football leagues, clubs, matches, and players.

## Architecture

The app follows the following architecture:

```mermaid
graph TD
    UI[React UI]
    Nginx[Nginx Proxy]
    Flask[Flask App]
    Scrapy[Crawler]
    MySQL[(MySQL Database)]
    subgraph LLama Index
      direction TB
      Llama[(Llama Index)]
      OpenAI[OpenAI API]
    end

    UI-- API -->Nginx
    Nginx-- Forwards Requests -->Flask

    Flask-- Queries -->MySQL
    Scrapy-- Stores Scraped Data -->MySQL

    Flask-- Queries Index -->Llama
    Llama-- Answers Questions -->OpenAI

    OpenAI-- Generates Responses -->Flask
```

## Data Models

Here are the data models used in the app:

```mermaid
classDiagram
  class LeagueModel {
    league_id: String(5) (PK)
    league_season: String(255) (PK)
    league_name: String(255) (Index)
    league_url: String(255)
    league_country: String(255)
    league_num_clubs: Integer
    league_num_players: Integer
    league_avg_age: Float
    league_percentage_foreigner: Float
    league_total_value: Float
  }

  class ClubModel {
    club_id: Integer (PK)
    club_season: String(255) (PK)
    club_name: String(255) (Index)
    club_url: String(255)
    club_league_id: String(5) (FK)
    club_league: LeagueModel
    club_slug_name: String(255)
    club_squads: Integer
    club_avg_age: Float
    club_num_foreigners: Integer
    club_avg_market_value: Float
    club_total_market_value: Float
  }

  class MatchModel {
    game_id: Integer (PK)
    game_season: String(255) (PK)
    game_date: String(20)
    game_day: String(10)
    game_time_at: String(20)
    game_league_id: String(5) (FK)
    game_league: LeagueModel
    game_home_club_id: Integer (FK)
    game_home_club: ClubModel
    game_away_club_id: Integer (FK)
    game_away_club: ClubModel
    game_home_club_name: String(255)
    game_away_club_name: String(255)
    game_result: String(10)
    game_url: String(255)
  }

  class PlayerModel {
    player_id: Integer (PK)
    player_season: String(255) (PK)
    player_club_id: Integer (FK)
    player_club: ClubModel
    player_number: Integer
    player_url: String(255)
    player_name: String(255)
    player_position: String(255)
    player_birth: String(255)
    player_nationality: String(255)
    player_market_value: Float
  }

  LeagueModel --|> ClubModel
  LeagueModel --|> MatchModel
  ClubModel --|> MatchModel
  ClubModel --|> PlayerModel
```

## Getting Started

To run the app, use the provided `docker-compose.yml` file and `Makefile`:

### Prerequisites

- Docker
- Docker Compose

### Setup

1. Clone this repository.
2. Create a `dev.env` file with necessary environment variables.
3. Run the following command to start the app:

   ```sh
   make install  # Install dependencies
   make test     # Run tests
   ```

### Docker Compose

The app can be deployed using Docker Compose:

1. Edit the dev.env file with your configuration, including OPENAI_API_KEY.

2. Run the following command to start the app:

   ```sh
   docker-compose up
   ```

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
```

You can copy and paste this markdown into your `README.md` file. Please make sure to adjust any placeholders like project names, descriptions, and paths to fit your actual project structure.