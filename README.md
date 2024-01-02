# Podcast RSS Generator

[![Python Unit Tests and Linting](https://github.com/vpetersson/podcast-rss-generator/actions/workflows/python-tests.yml/badge.svg)](https://github.com/vpetersson/podcast-rss-generator/actions/workflows/python-tests.yml)

## Description

This an RSS Feed Generator is designed to generate an RSS feed for audio/video podcasts, reading metadata and episode data from a YAML file.

It assumes that you self-host your video episodes somewhere (e.g. S3/GCS/R2) as well as the output of this script. You can then point YouTube/Spotify/Apple Podcast to this path.

This tool was written for my podcast [Nerding Out with Viktor](https://blog.viktorpetersson.com/nerding-out-with-viktor/) to solve for the fact that Apple's [Podcast Connect](https://podcastsconnect.apple.com) require you to self-host videos in order to publish.

## Features

- Generates RSS feed for audio/video podcasts
- Reads podcast metadata and episode data from a YAML file
- Converts ISO format dates to RFC 2822 format
- Attempts to follow [The Podcast RSS Standard](https://github.com/Podcast-Standards-Project/PSP-1-Podcast-RSS-Specification)

## Known Issues

* Videos uploaded to YouTube [via RSS](https://support.google.com/youtube/answer/13525207?hl=en#zippy=%2Ccan-i-deliver-an-rss-feed-if-i-already-have-a-podcast-on-youtube) will be uploaded as audio
* Spotify can't handle videos via RSS yet. You will be able to see the episodes in Podcaster, but they will not be processed and sent to Spotify properly. This is apparently a known issue that they are working on resolving.

The workaround for the above issues is to manually upload the episodes.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- ffmpeg

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

**Optional:** Install `yamllint`, `xq` and `flake8`.

## Usage

1. **Prepare Your Data Files**

Copy `podcast_config.example.yaml` to `podcast_config.yaml` and fill out your podcast metadata and eepisodes.

2. **Generate the RSS Feed**

Make sure your YAML is valid:

```bash
$ yamllint podcast_config.yaml
```

Generate your `podcast_feed.xml` file:

```bash
$ python rss_generator.py
```

Now copy your `podcast_feed.xml` to S3/GCS/R2 using a tool like `s3cmd`, `aws` or `mc` (from Minio).

**Optional:** You can verify your RSS feed using a tool like [Podbase](https://podba.se/validate/).

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
