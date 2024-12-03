# MagInkDashPlus

**This is a fork of the original [MagInkDash](https://github.com/speedyg0nz/MagInkDash) -- replacing the Google Calendar integration with a generic ICS feed, removing the OpenAI integration, and using a Docker-based REST API that renders the image on-the-fly instead of a Raspberry Pi cronjob.**

This repo contains the code needed to drive an E-Ink Magic Dashboard that uses a Docker container on a different host to automatically retrieve updated content from an ICS calendar and OpenWeatherMap, format them into the desired layout, before serving it to a battery powered E-Ink display (Inkplate 10). Note that the code has only been tested on the specific hardware mentioned, but can be easily modified to work with other hardware (for both the server or display).

![20230412_214635](https://user-images.githubusercontent.com/5581989/231482915-154db674-9301-465d-8352-d2c4400093eb.JPG)

## Background

I liked the premise of [MagInkDash](https://github.com/speedyg0nz/MagInkDash) but I'd rather have a containerized backend doing the rendering since that's easier to setup in my Docker-based homelab. Additionally, I'd like to enable the use of non-Google calendars and remove cloud dependencies like ChatGPT (maybe I'll add an Ollama integration in the future). Read more about the project in the [MagInkDash README](https://github.com/speedyg0nz/MagInkDash#background).

## Hardware Required

* A machine that supports Docker - Used as a server to retrieve content and generate a dashboard for the E-Ink display. Just needs to have [Docker](https://docs.docker.com/get-started/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) installed so any old machine or SBC would do. I would recommend that this container is not exposed to the public Internet since it shows your calendar information without authentication.
* [Inkplate 10 Battery Powered E-Ink Display](https://soldered.com/product/soldered-inkplate-10-9-7-e-paper-board-with-enclosure-copy/) - Used as a client to display the generated dashboard. I went with this because it was an all-in-one with the enclosure and battery included so there's less hardware tinkering. But you could certainly go barebones and assemble the different parts yourself from scratch, i.e. display, microcontroller, case, and battery.

## How It Works

On the backend, a Python API based on Docker and FastAPI is serving the image with all the desired info. As soon as the Inkplate requests the image, it pulls the calendar data and a weather forecast from OpenWeatherMap. The retrieved content is then formatted into the desired layout and served as a PNG image file.

On the Inkplate 10, a script will then connect to the server on the local network via a WiFi connection, retrieve the image and display it on the E-Ink screen. The Inkplate 10 then goes to sleep to conserve battery. The dashboard remains displayed on the E-Ink screen, because well, E-Ink...

Some features of the dashboard: 
- **Battery Life**: As with similar battery powered devices, the biggest question is the battery life. I'm currently using a 1500mAh battery on the Inkplate 10 and based on current usage, it should last me around 3-4 months. With the 3000mAh that comes with the manufacturer assembled Inkplate 10, we could potentially be looking at 6-8 month battery life. With this crazy battery life, there are much more options available. Perhaps solar power for unlimited battery life? Or reducing the refresh interval to 15 or 30min to increase the information timeliness?
- **Calendar and Weather**: I'm currently displaying calendar events and weather forecast for current day and the upcoming two days. No real reason other than the desire to know what my weekend looks like on a Friday, and therefore helping me to better plan my weekend. Unfortunately, if you have a busy calendar with numerous events on a single day, the space on the dashboard will be consumed very quickly. If so, you might wish to modify the code to reduce/limit the number of days/events to be displayed.

![MagInkDash Features](https://user-images.githubusercontent.com/5581989/231484018-6ff6a883-3226-42c7-a387-fcef7ee9d49c.png)

## Setting Up 

1. On the server host, make sure that `docker` and `docker compose` are installed.

2. Download the `docker-compose.yml` file from this repo and adjust the environment variables, see the section **Config Reference** below.

3. Start up the server with `docker compose up -d`. You can check the logs with `docker compose logs -f` and ensure that there are no errors.

4. Using the DNS name or IP of your host machine, you can go to  <http://IP_ADDRESS:5000/docs> to see whether the API is running.

5. As for the Inkplate, I'm not going to devote too much space here since there are [official resources that describe how to set it up](https://inkplate.readthedocs.io/en/latest/get-started.html). It may take some trial and error for those new to microcontroller programming but it's all worth it! Only the Arduino portion of the guide is relevant, and you'll need to be able to run *.ino scripts via Arduino IDE before proceeding. From there, run the `inkplate.ino` file from the `inkplate` folder from the Arduino IDE when connected to the Inkplate.

6. That's all! Your Magic Dashboard should now be refreshed every hour! 

![20230412_214652](https://user-images.githubusercontent.com/5581989/231485348-35d7e0df-034e-49aa-8500-223b2b3bdcc0.JPG)
![20230412_215020](https://user-images.githubusercontent.com/5581989/231484068-aa6ce877-1e0a-49fe-b47e-7c024752f42c.JPG)
Selfie and family portrait together with the MagInkCal

## Config Reference

These are the config variables you can configure in the `environment` section of the Docker Compose file:

Variable | Required | Default | Description
--- | --- | --- | ---
ICS_URL | Yes | | URL of the ICS calendar feed
OWM_API_KEY | Yes | | OpenWeatherMap API key to retrieve weather forecast
DISPLAY_TZ | No | America/Los_Angeles | Time zone for displaying the calendar
LAT | No | 34.118333 | Latitude in decimal of the location to retrieve weather forecast for
LNG | No | -118.300333 | Longitude in decimal of the location to retrieve weather forecast for
WEATHER_UNITS | No | metric | Units of measurement for the temperature, `metric` and `imperial` units are available
NUM_CAL_DATS_TO_SHOW | No | 5 | Number of days to show from the calendar
IMAGE_WIDTH | No | 1200 | Width of image to be generated for display
IMAGE_HEIGHT | No | 825 | Height of image to be generated for display
ROTATE_ANGLE | No | 0 | If image is rendered in portrait orientation, angle to rotate to fit screen

## Limitations

* Recurring events in the ICS calendar feed are currently not supported

## Development

Run

```shell
poetry run python src/main.py
```

or

```shell
docker compose -f docker-compose.dev.yml up --build
```

locally to start the application, API docs will be served at <http://localhost:5000/docs>.

## Acknowledgements

- [Lexend Font](https://fonts.google.com/specimen/Lexend) and [Tilt Warp Font](https://fonts.google.com/specimen/Tilt+Warp): Fonts used for the dashboard display
- [Bootstrap](https://getbootstrap.com/): Styling toolkit to customise the look of the dashboard
- [Weather Icons](https://erikflowers.github.io/weather-icons/): Icons used for displaying of weather forecast information
- [Freepik](https://www.freepik.com/): For the background image used in this dashboard
  
## Contributing

Feel free to fork the repo and modify it for your own purpose or create an issue and I see whether I can help.
