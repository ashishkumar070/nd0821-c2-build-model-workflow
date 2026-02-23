import pytest
import pandas as pd
import wandb
import logging
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption("--csv", action="store")
    parser.addoption("--ref", action="store")
    parser.addoption("--kl_threshold", action="store")
    parser.addoption("--min_price", action="store")
    parser.addoption("--max_price", action="store")

@pytest.fixture(scope='session')
def data(request):
    logger.info("Starting wandb.init() for data fixture")
    logger.info(f"WANDB_API_KEY set: {bool(os.environ.get('WANDB_API_KEY'))}")
    logger.info(f"WANDB_MODE: {os.environ.get('WANDB_MODE', 'not set')}")
    logger.info(f"CSV artifact: {request.config.option.csv}")

    run = wandb.init(
        job_type="data_tests",
        resume="allow",        
        settings=wandb.Settings(init_timeout=300)
    )
    logger.info(f"wandb.init() completed, run id: {run.id}")

    data_path = run.use_artifact(request.config.option.csv).file()
    if data_path is None:
        pytest.fail("You must provide the --csv option on the command line")
    df = pd.read_csv(data_path)
    return df

@pytest.fixture(scope='session')
def ref_data(request):
    logger.info("Starting wandb.init() for ref_data fixture")
    run = wandb.init(
        job_type="data_tests",
        resume="allow",
        settings=wandb.Settings(init_timeout=300)
    )
    logger.info(f"wandb.init() completed, run id: {run.id}")

    data_path = run.use_artifact(request.config.option.ref).file()
    if data_path is None:
        pytest.fail("You must provide the --ref option on the command line")
    df = pd.read_csv(data_path)
    return df

@pytest.fixture(scope='session')
def kl_threshold(request):
    kl_threshold = request.config.option.kl_threshold
    if kl_threshold is None:
        pytest.fail("You must provide a threshold for the KL test")
    return float(kl_threshold)

@pytest.fixture(scope='session')
def min_price(request):
    min_price = request.config.option.min_price
    if min_price is None:
        pytest.fail("You must provide min_price")
    return float(min_price)

@pytest.fixture(scope='session')
def max_price(request):
    max_price = request.config.option.max_price
    if max_price is None:
        pytest.fail("You must provide max_price")
    return float(max_price)