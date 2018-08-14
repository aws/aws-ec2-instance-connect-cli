import logging

class EC2InstanceConnectLogger(object):
    """
    Common logger for all the EC2InstanceConnect components.
    """

    def __init__(self, verbose=None):
        """
        :param verbose: Specifies if debug messages should be enabled
        :type verbose: bool or None
        """
        self.logger = logging.getLogger('EC2InstanceConnect')
        log_level = logging.ERROR
        if verbose:
            log_level = logging.DEBUG
        self.logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch) 

    def get_logger(self):
        return self.logger
