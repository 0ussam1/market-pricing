class DistributionNotFound(Exception):
    pass


def get_distribution(_name):
    raise DistributionNotFound
