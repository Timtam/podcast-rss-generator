import lxml.etree as ET
from datetime import datetime
from email.utils import format_datetime
import argparse

import markdown
import requests
import yaml
from sh import ffprobe


def read_podcast_config(yaml_file_path):
    with open(yaml_file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def convert_iso_to_rfc2822(iso_date):
    date_obj = datetime.fromisoformat(iso_date)
    return format_datetime(date_obj)


def get_file_info(url):
    response = requests.head(url, allow_redirects=True)

    # Get duration of audio/video file
    # We're using the response.url here in order to
    # follow redirects and get the actual file

    probe = ffprobe(
        "-hide_banner",
        "-v",
        "quiet",
        "-show_streams",
        "-print_format",
        "flat",
        response.url,
    )
    lines = probe.split("\n")

    # Filtering out the line that contains 'streams.stream.0.duration'
    duration_line = next(
        (line for line in lines if line.startswith("streams.stream.0.duration=")), None
    )

    if duration_line:
        # Extracting the numeric value and converting it to an integer
        duration = int(float(duration_line.split("=")[1].strip('"')))
    else:
        duration = None

    return {
        "content-length": response.headers.get("content-length"),
        "content-type": response.headers.get("content-type"),
        "duration": duration,
    }


def format_description(description):
    """
    Convert Markdown description to HTML
    """
    html_description = markdown.markdown(description)

    # Ensure byte limit for the channel description
    byte_limit = 4000
    if len(html_description.encode("utf-8")) > byte_limit:
        # Truncate the description if it exceeds the limit
        # Note: Truncation logic might need to be more sophisticated to handle HTML correctly
        html_description = html_description[:byte_limit]

    return html_description


def generate_rss(config, output_file_path):
    #ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    #ET.register_namespace("atom", "http://www.w3.org/2005/Atom")

    # Global itunes:explicit setting
    global_explicit = (
        "yes" if config["metadata"].get("itunes_explicit", False) else "no"
    )

    nsmap = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
             "atom": "http://www.w3.org/2005/Atom"
            }

    rss = ET.Element(
        "rss",
        version="2.0",
        nsmap = nsmap,
    )
    # Metadata
    channel = ET.SubElement(rss, "channel")
    metadata = config["metadata"]
    ET.SubElement(channel, "title").text = metadata["title"]
    ET.SubElement(channel, "description").text = ET.CDATA(metadata['description'])
    ET.SubElement(channel, "language").text = metadata.get("language", "en-us")
    ET.SubElement(channel, "link").text = metadata["link"]
    ET.SubElement(
        channel, "generator"
    ).text = (
        "Podcast RSS Generator (https://github.com/vpetersson/podcast-rss-generator)"
    )
    ET.SubElement(
        channel,
        f"{{{nsmap['atom']}}}link",
        href=metadata["rss_feed_url"],
        rel="self",
        type="application/rss+xml",
    )

    # Adds explicit tag
    itunes_explicit = ET.SubElement(channel, f"{{{nsmap['itunes']}}}explicit")
    itunes_explicit.text = global_explicit

    # Add itunes:owner and itunes:email tags
    itunes_owner = ET.SubElement(channel, f"{{{nsmap['itunes']}}}owner")
    ET.SubElement(itunes_owner, f"{{{nsmap['itunes']}}}email").text = metadata["itunes_email"]

    # Add itunes:author tag
    itunes_author = ET.SubElement(channel, f"{{{nsmap['itunes']}}}author")
    itunes_author.text = metadata["itunes_author"]

    # Duplicate description to itunes summary
    itunes_summary = ET.SubElement(channel, f"{{{nsmap['itunes']}}}summary")
    itunes_summary.text = ET.CDATA(metadata["description"])

    # Add itunes:category tag
    if "itunes_category" in metadata:
        ET.SubElement(channel, f"{{{nsmap['itunes']}}}category", text=metadata["itunes_category"])

    if "itunes_image" in metadata:
        itunes_image = ET.SubElement(channel, f"{{{nsmap['itunes']}}}image")
        itunes_image.set("href", metadata["itunes_image"])

    # Episodes
    for episode in config["episodes"]:
        print(f"Processing episode {episode['title']}...")

        # Don't pre-publish episodes
        if not datetime.fromisoformat(episode["publication_date"]) < datetime.utcnow():
            print(
                f"Skipping episode {episode['title']} as it's not scheduled to be released until {episode['publication_date']}."
            )
            continue

        file_info = get_file_info(episode["asset_url"])
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "pubDate").text = convert_iso_to_rfc2822(
            episode["publication_date"]
        )
        ET.SubElement(item, "title").text = episode["title"]
        ET.SubElement(item, "description").text = ET.CDATA(format_description(
            episode["description"]
        ))
        ET.SubElement(item, "guid").text = episode["asset_url"]
        ET.SubElement(
            item,
            "enclosure",
            url=episode["asset_url"],
            type=file_info["content-type"],
            length=str(file_info["content-length"]),
        )

        # Apply global itunes:explicit setting to each episode
        itunes_explicit = ET.SubElement(item, f"{{{nsmap['itunes']}}}explicit")
        itunes_explicit.text = global_explicit

        # Add itunes:duration tag
        itunes_duration = ET.SubElement(item, f"{{{nsmap['itunes']}}}duration")
        itunes_duration.text = str(file_info["duration"])

        # iTunes-specific tags
        if episode.get("episode") is not None:
            itunes_episode = ET.SubElement(item, f"{{{nsmap['itunes']}}}episode")
            itunes_episode.text = str(episode["episode"])

        if episode.get("season") is not None:
            itunes_season = ET.SubElement(item, f"{{{nsmap['itunes']}}}season")
            itunes_season.text = str(episode["season"])

        if episode.get("episode_type") is not None:
            itunes_episode_type = ET.SubElement(item, f"{{{nsmap['itunes']}}}episodeType")
            itunes_episode_type.text = episode["episode_type"]

        # Add link if available, if not, use global
        link = ET.SubElement(item, "link")
        link.text = episode.get("link", metadata["link"])

        # Use episode specific artwork if available
        itunes_image_url = episode.get("itunes_image", metadata["itunes_image"])

        # Creating the 'itunes:image' element with the determined URL
        itunes_image = ET.SubElement(item, f"{{{nsmap['itunes']}}}image")
        itunes_image.set("href", itunes_image_url)

    tree = ET.ElementTree(rss)
    tree.write(output_file_path, encoding="UTF-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description="Process some parameters.")

    parser.add_argument(
        "--input-file", type=str, default="podcast_config.yaml", help="Input YAML file"
    )
    parser.add_argument(
        "--output-file", type=str, default="podcast_feed.xml", help="Output XML file"
    )

    # Parse arguments from the command line
    args = parser.parse_args()

    print(f"Input file: {args.input_file}, Output file: {args.output_file}")

    config = read_podcast_config(args.input_file)
    generate_rss(config, args.output_file)


if __name__ == "__main__":
    main()
