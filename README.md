# Podcast RSS Generator

[![Python Unit Tests and Linting](https://github.com/vpetersson/podcast-rss-generator/actions/workflows/python-tests.yml/badge.svg)](https://github.com/vpetersson/podcast-rss-generator/actions/workflows/python-tests.yml)

## Description

This an RSS Feed Generator is designed to generate an RSS feed for audio/video podcasts, reading metadata from a YAML file and video details from a CSV file.

It assumes that you self-host your video episodes somewhere (e.g. S3/GCS/R2) as well as the output of this script. You can then point YouTube/Spotify/Apple Podcast to this path.

This tool was written for my podcast [Nerding Out with Viktor](https://blog.viktorpetersson.com/nerding-out-with-viktor/) to solve for the fact that Apple's [Podcast Connect](https://podcastsconnect.apple.com) require you to self-host videos in order to publish.

## Features

- Generates RSS feed for video podcasts
- Reads podcast metadata from a YAML file
- Extracts video details from a CSV file
- Converts ISO format dates to RFC 2822 format

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the Repository**

```bash
$ git clone https://github.com/vpetersson/podcast-rss-generator.git
$ cd podcast-rss-generator
```

2. **Install Dependencies**

```bash
$ pip install -r requirements.txt
```

*Note: Ensure your `requirements.txt` file includes all necessary packages like `pyyaml` and `flake8`.*

## Usage

1. **Prepare Your Data Files**

- Copy `metadata.yaml.example` to `metadata.yaml` and fill out your podcast metadata.
- Copy `videos.csv.example` to `videos.csv` file and popuylate it with your podcast episodes.

2. **Generate the RSS Feed**

```bash
$ python rss_generator.py
```

This command will generate an RSS feed in XML format.

You can verify your RSS feed using a tool like [Podbase](https://podba.se/validate/).

You might also qant to install `xq` (which is like `jq`, but for XML) for easier local debugging.

## Running Tests

To run unit tests, use:

```bash
$ python -m unittest discover tests
```

## Contributing

Contributions to this project are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Submit a pull request.

## License
[MIT License](LICENSE)
