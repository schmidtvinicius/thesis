# Evaluating Data Stream Write Performance in Current Lakehouse Systems

This repository contains the code that was produced as part of my Master Thesis Project at Radboud University.

## Installing dependencies
This project uses the `uv` project manager. Instructions on how to install it can be found [here](https://docs.astral.sh/uv/).

## Running the benchmark

### Preparing the data
Before any scripts can be run, you need to download and prepare the data. The benchmark works with the [NYC Taxi Dataset](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), sepcifically with the "Yellow Taxi Trip Records" files. You should download the files into the [raw_data/](./raw_data/) directory. The amount of files you use is limited only by how much storage and memory your machine has.

Once the files are downloaded, you can run the prepare the data by running:

```sh
uv run prepare_data.py
```

The script will read each file in the `raw_data` directory and write a new parquet file in the `data` directory. The new files have a column called `trip_id`, which is used to easily identify trips once the benchmark is run. The ids will always be generated in the same order for consistency and reproducibility reasons. The new parquet files will have an increase in file size of about 45% in comparison to the original files, so keep that in mind if your machine has limited storage capacity.