import cfn_flip
import logging

logger = logging.getLogger(__name__)


def load_template(fpath: str):
    # TODO: Support JSON
    with open(fpath, "r") as f:
        try:
            data = cfn_flip.load_yaml(f)
            logger.info(f"Loaded {fpath} as CloudFormation template in YAML format")
            return data
        except:
            try:
                data = cfn_flip.load_json(f)
                logger.info(
                    f"Loaded {fpath} as a CloudFormation template in JSON format"
                )
                return data
            except:
                logger.error(f"Unable to load {fpath} as a CloudFormation template")
