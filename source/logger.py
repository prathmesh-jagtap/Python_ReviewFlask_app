import logging


logging.basicConfig(filename='../logger.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format="%(asctime)s : %(levelname)s  %(name)s - %(message)s",
                    )
log = logging.getLogger(__name__)
