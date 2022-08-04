import dotenv
import logging

# needed for local development; Inside docker the .env is loaded anyway.
dotenv.load_dotenv()


# Root logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdout = logging.StreamHandler()
stdout.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
stdout.setFormatter(formatter)

logger.addHandler(stdout)