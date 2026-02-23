#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning,
exporting the result to a new artifact
"""

import argparse
import logging
import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)-15s %(message)s")

logger = logging.getLogger()
from datetime import datetime


def go(args):

    #run = wandb.init(job_type="basic_cleaning", )

    run = wandb.init(
        job_type="basic_cleaning",
        name=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        settings=wandb.Settings(init_timeout=120)  # timeout in seconds
    )
    run.config.update(args)

    # Download artifact from W&B
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path)

    # Convert price to float (remove $ and commas)
    df["price"] = (
        df["price"]
        .replace(r"[\$,]", "", regex=True)
        .astype(float)
    )

    # Filter price outliers
    df = df[df["price"].between(args.min_price, args.max_price)].copy()

    # Convert last_review to datetime
    df["last_review"] = pd.to_datetime(df["last_review"])

    idx = df['longitude'].between(-74.25, -73.50) & \
      df['latitude'].between(40.5, 41.2)

    df = df[idx].copy()


    # Save cleaned dataset
    df.to_csv("clean_sample.csv", index=False)

    # Upload new artifact
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file("clean_sample.csv")
    #run.log_artifact(artifact)
    run.log_artifact(
        artifact,
        aliases=["latest", "reference"]
    )

    run.finish()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A very basic data cleaning"
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Input artifact name",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Output artifact name",
        required=True,
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Output artifact type",
        required=True,
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Output artifact description",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price threshold",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price threshold",
        required=True,
    )

    args = parser.parse_args()

    go(args)